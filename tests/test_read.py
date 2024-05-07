from xlsxdatagrid.read import read_excel
from .constants import PATH_XL, PATH_XL_TRANSPOSED
from .test_xlsxdatagrid import TestArray, TestArrayTransposed
import typing as ty
from pydantic import BaseModel
import pytest
import pathlib
import json
from pathlib import Path
from tempfile import TemporaryDirectory
from datamodel_code_generator import InputFileType, generate
from datamodel_code_generator import DataModelType
import importlib.util
import sys

paths = list(pathlib.Path("tests").glob("*schema.*"))
schemas = {}
for p in paths:
    schema = json.loads(p.read_text())
    schemas[schema["title"]] = schema


def model_loader(name):
    if name in globals():
        return globals()[name]
    else:
        return None


def pydantic_model_from_json_schema(json_schema):
    with TemporaryDirectory() as temporary_directory_name:
        temporary_directory = Path(temporary_directory_name)
        file_path = "model.py"
        module_name = file_path.split(".")[0]
        output = Path(temporary_directory / file_path)
        generate(
            json_schema,
            input_file_type=InputFileType.JsonSchema,
            input_filename="example.json",
            output=output,
            output_model_type=DataModelType.PydanticV2BaseModel,
        )
        spec = importlib.util.spec_from_file_location(module_name, output)
        module = importlib.util.module_from_spec(spec)
        sys.modules[module_name] = module
        spec.loader.exec_module(module)
    return module.Model


@pytest.mark.parametrize("path", [PATH_XL, PATH_XL_TRANSPOSED])
def test_read_excel(path):
    obj = read_excel(path, model_loader=model_loader)
    assert obj.model_json_schema()["datagrid_index_name"] == (
        "section",
        "title",
        "name",
    )
    assert isinstance(obj.model_dump(), list)
    print("done")


def get_schema(name, schemas=schemas):
    return schemas.get(name)


TEST_JSON_SCHEMA: str = """{
    "type": "object",
    "properties": {
        "number": {"type": "number"},
        "street_name": {"type": "string"},
        "street_type": {"type": "string",
                        "enum": ["Street", "Avenue", "Boulevard"]
                        }
    }
}"""


def test_load_model_from_json_schema():
    pydantic_model = pydantic_model_from_json_schema(TEST_JSON_SCHEMA)
    assert issubclass(pydantic_model, BaseModel)
    assert isinstance(pydantic_model(), BaseModel)


def load_model_from_xl_metadata():

    pass
