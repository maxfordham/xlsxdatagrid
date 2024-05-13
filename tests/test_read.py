from xlsxdatagrid.read import read_excel, pydantic_model_from_json_schema
from xlsxdatagrid.xlsxdatagrid import DataGridMetaData
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

# PATH_SCHEMA = pathlib.Path()
schemas = [TestArray.model_json_schema(), TestArrayTransposed.model_json_schema()]
schemas = {s["title"]: s for s in schemas}

# paths = list(pathlib.Path("tests").glob("*schema.*"))
# for p in paths:
#     schema = json.loads(p.read_text())
#     schemas[schema["title"]] = schema


# def pydantic_model_from_json_schema(json_schema: str) -> ty.Type[BaseModel]:
#     with TemporaryDirectory() as temporary_directory_name:
#         temporary_directory = Path(temporary_directory_name)
#         file_path = "model.py"
#         module_name = file_path.split(".")[0]
#         output = Path(temporary_directory / file_path)
#         generate(
#             json_schema,
#             input_file_type=InputFileType.JsonSchema,
#             input_filename="example.json",
#             output=output,
#             output_model_type=DataModelType.PydanticV2BaseModel,
#         )
#         spec = importlib.util.spec_from_file_location(module_name, output)
#         module = importlib.util.module_from_spec(spec)
#         sys.modules[module_name] = module
#         spec.loader.exec_module(module)
#     return module.Model


def get_schema(name, schemas=schemas):
    return schemas.get(name)


def get_jsonschema(metadata: DataGridMetaData) -> dict:
    return schemas.get(metadata.template_name)


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
    pydantic_model = pydantic_model_from_json_schema(json.loads(TEST_JSON_SCHEMA))
    assert issubclass(pydantic_model, BaseModel)
    assert isinstance(pydantic_model(), BaseModel)


def test_get_jsonschema():

    metadata = DataGridMetaData(template_name="TestArray")
    jsonschema = get_jsonschema(metadata)
    assert jsonschema["title"] == "TestArray"


@pytest.mark.parametrize("path", [PATH_XL, PATH_XL_TRANSPOSED])
def test_read_excel(path):
    obj = read_excel(path, get_jsonschema=get_jsonschema)
    assert isinstance(obj, list)
    assert len(obj) == 3
    print("done")
