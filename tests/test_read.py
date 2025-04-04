import datetime
import json
import typing as ty

from pydantic import BaseModel

from xlsxdatagrid.read import pydantic_model_from_json_schema, read_excel
from xlsxdatagrid.xlsxdatagrid import DataGridMetaData

from .constants import PATH_JSONSCHEMA_RAW
from .test_xlsxdatagrid import (
    TestArray,
    TestArrayTransposed,
    from_json_with_null,  # req. fixture  # noqa: F401
    write_table_test,  # req. fixture  # noqa: F401
)

schemas = [TestArray.model_json_schema(), TestArrayTransposed.model_json_schema()]
schemas = {s["title"]: s for s in schemas}


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


def get_datamodel(metadata: DataGridMetaData) -> dict:
    return schemas.get(metadata.name)


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

TEST_JSON_SCHEMA1: str = """{
    "properties": {
        "a_int": {
            "default": 1,
            "section": "numeric",
            "title": "A Int",
            "type": "integer"
        },
        "Abbreviation": {
            "enum": [
                "yellow",
                "red",
                "violet"
            ],
            "type": "string",
            "default": "yellow",
            "description": "pick colour"
        }
    },
    "required": [
        "Abbreviation"
    ],
    "title": "Test",
    "type": "object"
}"""

#


def test_load_model_from_json_schema():
    pydantic_model = pydantic_model_from_json_schema(json.loads(TEST_JSON_SCHEMA))
    assert issubclass(pydantic_model, BaseModel)
    assert isinstance(pydantic_model(), BaseModel)


def test_load_model_from_json_schema_issue2091():
    # TODO: remove this once resolved: https://github.com/koxudaxi/datamodel-code-generator/issues/2091
    pydantic_model = pydantic_model_from_json_schema(json.loads(TEST_JSON_SCHEMA1))
    assert issubclass(pydantic_model, BaseModel)
    assert isinstance(pydantic_model(Abbreviation="yellow"), BaseModel)


def test_get_datamodel():
    metadata = DataGridMetaData(name="TestArray", title="Test Array")
    jsonschema = get_datamodel(metadata)
    assert jsonschema["title"] == "TestArray"


def test_read_excel(write_table_test):  # noqa: F811
    path = write_table_test
    obj, metadata = read_excel(path, get_datamodel=get_datamodel)
    assert isinstance(obj, list)
    assert len(obj) == 3
    print("done")


def get_raw_jsonschema(metadata: DataGridMetaData) -> dict:
    return json.loads(PATH_JSONSCHEMA_RAW.read_text())


def test_read_excel_with_null(from_json_with_null):  # noqa: F811
    fpth, data, schema = from_json_with_null
    obj, metadata = read_excel(
        fpth, get_datamodel=lambda *args: schema.model_json_schema()
    )
    assert obj == data


def test_timedelta():
    # https://github.com/koxudaxi/datamodel-code-generator/issues/1624
    schema = {
        "title": "Test",
        "type": "object",
        "properties": {
            "a_int": {"default": 1, "title": "A Int", "type": "integer"},
            "i_duration": {
                "default": "PT2H33M3S",
                "format": "duration",
                "title": "I Duration",
                "type": "string",
            },
        },
    }

    Model = pydantic_model_from_json_schema(schema)
    assert (
        Model.model_fields["i_duration"].annotation == ty.Optional[datetime.timedelta]
    )


def test_field_name_change():
    """Test that the field name changes in the pydantic model if enumeration
    given same name as property.
    This behaviour introduced in version 0.28.5.
    Issue discussing this behaviour: https://github.com/koxudaxi/datamodel-code-generator/issues/2364
    """
    schema = {
        "type": "object",
        "properties": {"Fruit": {"$ref": "#/definitions/Fruit"}},
        "definitions": {
            "Fruit": {
                "enum": ["apple", "banana"],
                "name": "Fruit",
                "title": "Fruit",
                "type": "string",
            }
        },
    }
    test_model = pydantic_model_from_json_schema(schema)
    assert "Fruit_1" in test_model.__annotations__
    assert "Fruit" in test_model.model_fields["Fruit_1"].alias
    validated_model = test_model.model_validate({"Fruit": "apple"})
    assert validated_model.model_dump(by_alias=True, mode="json") == {"Fruit": "apple"}
