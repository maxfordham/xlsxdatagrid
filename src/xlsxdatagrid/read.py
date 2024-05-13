from python_calamine import CalamineWorkbook, CalamineSheet
import typing as ty
from pydantic import BaseModel
from xlsxdatagrid.xlsxdatagrid import DataGridMetaData
from stringcase import snakecase
from pathlib import Path

from tempfile import TemporaryDirectory
from datamodel_code_generator import InputFileType, generate
from datamodel_code_generator import DataModelType
import importlib.util
import sys
import json


def pydantic_model_from_json_schema(json_schema: str) -> ty.Type[BaseModel]:
    load = json_schema["title"] if "title" in json_schema else "Model"

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
        )
        spec = importlib.util.spec_from_file_location(module_name, output)
        module = importlib.util.module_from_spec(spec)
        sys.modules[module_name] = module
        spec.loader.exec_module(module)
    return getattr(module, load)


def read_metadata(s: str) -> DataGridMetaData:
    s = s.replace("#", "")
    li = [l.split("=") for l in s.split(" - ")]
    di = {snakecase(l[0]): l[1] for l in li}
    return DataGridMetaData(**di)


def process_data(
    data: list[dict], metadata: DataGridMetaData
) -> tuple[list[dict], DataGridMetaData]:
    hd = metadata.header_depth
    is_t = metadata.is_transposed
    if is_t:
        data = list(map(list, zip(*data)))

    # else:
    header_names = [d[0] for d in data[0:hd]]
    data = [d[1:] for d in data]
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


def get_jsonschema(metadata: DataGridMetaData) -> dict:
    pass


def read_worksheet(
    worksheet: CalamineSheet,
    get_jsonschema: ty.Optional[ty.Callable[[DataGridMetaData], dict]] = None,
) -> list[dict]:
    data = worksheet.to_python(skip_empty_area=True)
    data, metadata = read_data(data)
    if get_jsonschema is not None:
        json_schema = get_jsonschema(metadata)
        if json_schema is not None:
            pydantic_model = pydantic_model_from_json_schema(json_schema)
            return pydantic_model.model_validate(data).model_dump(mode="json")
        else:
            return data
    else:
        return data


def read_excel(
    path,
    get_jsonschema: ty.Optional[
        ty.Callable[[DataGridMetaData], ty.Type[BaseModel]]
    ] = None,
):
    workbook = CalamineWorkbook.from_path(path)
    sheet = workbook.sheet_names[0]
    worksheet = workbook.get_sheet_by_name(sheet)
    return read_worksheet(worksheet, get_jsonschema)
