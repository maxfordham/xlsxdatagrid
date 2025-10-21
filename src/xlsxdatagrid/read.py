# std libs
import csv
import importlib.util
import json
import sys
import typing as ty
from datetime import timezone, time, date, datetime, timedelta
from pathlib import Path
from tempfile import TemporaryDirectory
from io import StringIO

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

def _replace_empty_with_none(value: str) -> ty.Optional[str]:
    """Helper to replace empty strings with None."""
    return None if value == "" else value

def process_data(
    data: list[
        list[
            int
            | float
            | str
            | bool
            | time
            | date
            | datetime
            | timedelta
        ],],
    is_transposed: bool = False,
    header_depth: int = 1,
    datagrid_index_name: ty.Optional[list[str]] = None,
    *,
    empty_string_to_none=True,
    include_header_line: bool = True,
    model: BaseModel | None = None,
) -> list[dict]:
    metadata: DataGridMetaData = DataGridMetaData(
        title="",
        is_transposed=is_transposed,
        header_depth=header_depth,
        datagrid_index_name=tuple(datagrid_index_name or ()),
    )
    if is_transposed:
        data = list(map(list, zip(*data)))

    header_names = [d[0] for d in data[0:header_depth]]
    if include_header_line:
        data = [d[1:] for d in data]

    if empty_string_to_none:
        data = [[_replace_empty_with_none(v) for v in row] for row in data]

    headers = {h: data[n] for n, h in enumerate(header_names)}
    header = headers[header_names[-1]]
    metadata.datagrid_index_name = list(headers.keys())
    metadata.header = list(headers.values())

    data = data[len(header_names):]
    data = [dict(zip(header, d)) for d in data]

    return data, metadata

def read_data(
    data, 
    includes_header_line = True,
    is_transposed: bool = False,
    header_depth: int = 1,
    datagrid_index_name: list[str] | None = None,   
    model: BaseModel | None = None,    
) -> tuple[list[dict], DataGridMetaData]:
    if includes_header_line:
        if data[0][0][0] != "#":
            raise ValueError(
                "the first row must be a metadata string beginning with the char '#'"
            )
        metadata = read_metadata(data[0][0])
        data = data[1:]
        return process_data(data, metadata.is_transposed, metadata.header_depth, metadata.datagrid_index_name)
    else:
        return process_data(data, is_transposed, header_depth, datagrid_index_name, include_header_line=includes_header_line, model=model)


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

def get_metadata(data) -> DataGridMetaData:
    if data[0][0] != "#":
        raise ValueError(
            "the first row must be a metadata string beginning with the char '#'"
        )
    return read_metadata(data[0][0])

def get_list_of_list_from_worksheet(worksheet: CalamineSheet) -> list[list]:
    return worksheet.to_python(skip_empty_area=True)


def get_list_of_list_from_string(tsv_string: str, delimiter: str = "\t") -> list[
        list[
            int
            | float
            | str
            | bool
            | time
            | date
            | datetime
            | timedelta
        ],]:
    tsv_file = StringIO(tsv_string.strip())
    reader = csv.reader(tsv_file, delimiter=delimiter)
    data = [x for x in reader]
    return data

def pydantic_validate_data(data, metadata = None, get_datamodel = None, return_pydantic_model: bool = False, model: BaseModel | None = None):
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
    elif model is not None:
        return model.model_validate(data).model_dump(mode="json", by_alias=True), metadata
    else:
        return data, metadata

def read_worksheet(
    worksheet: CalamineSheet,
    get_datamodel: ty.Optional[ty.Callable[[DataGridMetaData], dict]] = None,
    *,
    return_pydantic_model: bool = False,
) -> list[dict]:
    data = get_list_of_list_from_worksheet(worksheet) 
    # metadata = get_metadata(data[0][0])
    # data = process_data(data[1:], metadata) # TODO
    data, metadata = read_data(data)
    return pydantic_validate_data(data, metadata, get_datamodel, return_pydantic_model=return_pydantic_model)
    
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

def read_tsv_string(
    tsv_string: str,
    includes_header_line: bool = False,
    is_transposed: bool = False,
    header_depth: int = 1,
    model: BaseModel | None = None,
):
    data = get_list_of_list_from_string(tsv_string)
    processed_data = read_data(data, includes_header_line, is_transposed, header_depth, model=model)
    return pydantic_validate_data(processed_data[0], None, model=model)
