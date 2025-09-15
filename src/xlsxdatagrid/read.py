# std libs
import importlib.util
import json
import sys
import typing as ty
from datetime import timezone
from pathlib import Path
from tempfile import TemporaryDirectory

from datamodel_code_generator import DataModelType, InputFileType, generate
from pydantic import AwareDatetime, BaseModel

# 3rd party
from python_calamine import CalamineSheet, CalamineWorkbook
from stringcase import snakecase

# local
from xlsxdatagrid.xlsxdatagrid import DataGridMetaData


def pydantic_model_from_json_schema(json_schema: str) -> ty.Type[BaseModel]:
    load = json_schema["title"].replace(" ", "") if "title" in json_schema else "Model"
    # TODO: refactor this when title vs name vs code has been sorted out...

    with TemporaryDirectory() as temporary_directory_name:
        temporary_directory = Path(temporary_directory_name)
        file_path = "model.py"
        module_name = file_path.split(".")[0]
        output = Path(temporary_directory / file_path)
        generate(
            json.dumps(json_schema),
            input_file_type=InputFileType.JsonSchema,
            input_filename="example.json",
            output=output,
            output_model_type=DataModelType.PydanticV2BaseModel,
            capitalise_enum_members=True,
        )
        spec = importlib.util.spec_from_file_location(module_name, output)
        module = importlib.util.module_from_spec(spec)
        sys.modules[module_name] = module
        spec.loader.exec_module(module)
    return getattr(module, load)


def read_metadata(s: str) -> DataGridMetaData:
    s = s.replace("#", "")
    li = [x.split("=") for x in s.split(" - ")]
    di = {snakecase(x[0]): x[1] for x in li}
    return DataGridMetaData(**di)


def process_data(
    data: list[dict], metadata: DataGridMetaData, *, empty_string_to_none=True
) -> tuple[list[dict], DataGridMetaData]:
    hd = metadata.header_depth
    is_t = metadata.is_transposed
    if is_t:
        data = list(map(list, zip(*data)))

    # else:
    header_names = [d[0] for d in data[0:hd]]
    data = [d[1:] for d in data]
    if empty_string_to_none:
        data = [[(lambda _: None if _ == "" else _)(_) for _ in d] for d in data]

    headers = {h: data[n] for n, h in enumerate(header_names)}
    header = headers[header_names[-1]]
    metadata.datagrid_index_name = list(headers.keys())
    metadata.header = list(headers.values())

    data = data[len(header_names) :]
    data = [dict(zip(header, d)) for d in data]

    return data, metadata


def read_data(data) -> tuple[list[dict], DataGridMetaData]:
    if data[0][0][0] != "#":
        raise ValueError(
            "the first row must be a metadata string beginning with the char '#'"
        )
    metadata = read_metadata(data[0][0])
    data = data[1:]
    return process_data(data, metadata)


def get_datamodel(metadata: DataGridMetaData) -> dict:
    pass


def make_datetime_tz_aware(data, pydantic_model):
    def field_is_aware_datetime(field):
        if hasattr(field.annotation, "__args__"):
            if AwareDatetime in field.annotation.__args__:
                return True
            else:
                return False
        elif isinstance(field.annotation, AwareDatetime):
            return True
        else:
            return False

    row_model = pydantic_model.model_fields["root"].annotation.__args__[0]
    keys = [k for k, v in row_model.model_fields.items() if field_is_aware_datetime(v)]
    if len(keys) > 0:
        return [d | {k: d[k].replace(tzinfo=timezone.utc) for k in keys} for d in data]
    else:
        return data


def read_worksheet(
    worksheet: CalamineSheet,
    get_datamodel: ty.Optional[ty.Callable[[DataGridMetaData], dict]] = None,
    *,
    return_pydantic_model: bool = False,
) -> list[dict]:
    data = worksheet.to_python(skip_empty_area=True)
    data, metadata = read_data(data)
    if get_datamodel is not None:
        json_schema = get_datamodel(metadata)
        if json_schema is not None:
            pydantic_model = pydantic_model_from_json_schema(json_schema)

            data = make_datetime_tz_aware(data, pydantic_model)
            # ^ HACK: assume utc time for all datetimes as excel doesn't support tz...
            if return_pydantic_model:
                return pydantic_model.model_validate(data), metadata
            else:
                return (
                    pydantic_model.model_validate(data).model_dump(
                        mode="json", by_alias=True
                    ),
                    metadata,
                )
        else:
            return data, metadata
    else:
        return data, metadata


def read_excel(
    path,
    get_datamodel: ty.Optional[
        ty.Callable[[DataGridMetaData], ty.Type[BaseModel]]
    ] = None,
):
    workbook = CalamineWorkbook.from_path(path)
    sheet = workbook.sheet_names[0]
    worksheet = workbook.get_sheet_by_name(sheet)
    return read_worksheet(worksheet, get_datamodel)
