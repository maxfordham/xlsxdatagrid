import datetime
import json
import typing as ty

from pydantic import BaseModel

from xlsxdatagrid.read import pydantic_model_from_json_schema, read_excel, read_tsv_string
from xlsxdatagrid.xlsxdatagrid import DataGridMetaData

from .constants import PATH_JSONSCHEMA_RAW
from .test_xlsxdatagrid import (
    TestArray,
    TestArrayTransposed,
    from_json_with_null,  # req. fixture  # noqa: F401
    write_table_test,  # req. fixture  # noqa: F401
)

from .transposed_tsv_model import DataTypesArrayTransposed

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
    path, xl_tbl = write_table_test
    obj, metadata = read_excel(path, get_datamodel=get_datamodel)
    assert isinstance(obj, list)
    assert len(obj) == 3
    print("done")
    
# def test_read_records(type_spec_model=DistributionBoard):  # noqa: F811
#     """
#         Test to ensure that the data is consistent between edit tsv and within the editgrid.
#         In some cases EditTsv replaces None with ''
#     """
#     edit_tsv_records = [
#         {
#             'Abbreviation': 'DB',
#             'TypeReference': 1,
#             'Symbol': '',
#             'ClassificationUniclassProductNumber': 'Pr_60_70_22_22',
#             'ClassificationUniclassSystemNumber': '',
#             'FunctionReference': '',
#             'Notes': '',
#             'OverallLength': None,
#             'ManufacturerWebsite': 'https://maxfordham.com/',
#             'Voltage': None,
#             'Id': 2
#         },
#         {
#             'Abbreviation': 'DB',
#             'TypeReference': 2,
#             'Symbol': '',
#             'ClassificationUniclassProductNumber': 'Pr_60_70_22_21',
#             'ClassificationUniclassSystemNumber': '',
#             'FunctionReference': '',
#             'Notes': '',
#             'OverallLength': None,
#             'ManufacturerWebsite': 'https://maxfordham.com/',
#             'Voltage': None,
#             'Id': 3
#         }
#     ]
#     type_spec_records = [
#         {
#             'Abbreviation': 'DB',
#             'TypeReference': 1,
#             'Symbol': '',
#             'ClassificationUniclassProductNumber': 'Pr_60_70_22_22',
#             'ClassificationUniclassSystemNumber': '',
#             'FunctionReference': None,
#             'Notes': None,
#             'OverallLength': None,
#             'ManufacturerWebsite': 'https://maxfordham.com/',
#             'Voltage': None,
#             'Id': 2
#         },
#         {
#             'Abbreviation': 'DB',
#             'TypeReference': 2,
#             'Symbol': '',
#             'ClassificationUniclassProductNumber': 'Pr_60_70_22_21',
#             'ClassificationUniclassSystemNumber': '',
#             'FunctionReference': None,
#             'Notes': None,
#             'OverallLength': None,
#             'ManufacturerWebsite': 'https://maxfordham.com/',
#             'Voltage': None,
#             'Id': 3
#         }
#     ]
#     assert type_spec_records != edit_tsv_records
#     obj = read_records(edit_tsv_records, type_spec_model)
#     assert isinstance(obj, list)
#     assert obj != type_spec_records
#     print("done")

# def test_read_tsv_string(type_spec_model=DistributionBoard):  # noqa: F811
#     """
#         Test to ensure that the data is consistent between edit tsv string and within the editgrid.
#         In some cases EditTsv replaces None with ''
#     """
#     edit_tsv_string = """Abbreviation\tDB\tDB\nTypeReference\t1\t2\nSymbol\t\t\nClassificationUniclassProductNumber\tPr_60_70_22_22\tPr_60_70_22_21\nClassificationUniclassSystemNumber\t\t\nFunctionReference\t\t\nNotes\t\t\nOverallLength\t1\t2\nManufacturerWebsite\thttps://maxfordham.com/\thttps://maxfordham.com/\nVoltage\t1\t240\nId\t2\t3\n"""

#     type_spec_records = [
#     {
#         'Abbreviation': 'DB',
#         'TypeReference': 1,
#         'Symbol': '',
#         'ClassificationUniclassProductNumber': 'Pr_60_70_22_22',
#         'ClassificationUniclassSystemNumber': '',
#         'FunctionReference': None,
#         'Notes': None,
#         'OverallLength': None,
#         'ManufacturerWebsite': 'https://maxfordham.com/',
#         'Voltage': None,
#         'Id': 2
#     },
#     {
#         'Abbreviation': 'DB',
#         'TypeReference': 2,
#         'Symbol': '',
#         'ClassificationUniclassProductNumber': 'Pr_60_70_22_21',
#         'ClassificationUniclassSystemNumber': '',
#         'FunctionReference': None,
#         'Notes': None,
#         'OverallLength': None,
#         'ManufacturerWebsite': 'https://maxfordham.com/',
#         'Voltage': None,
#         'Id': 3
#     }
# ]

#     assert type_spec_records != edit_tsv_string
#     obj = read_tsv_string(edit_tsv_string, type_spec_model, transposed=True)
#     assert isinstance(obj, list)
#     assert obj != type_spec_records
#     print("done")

def test_read_tsv_string(write_table_test):
    tsv_string = """type\ttitle\tname\trow1\trow2\trow3
                    numeric\tA Int\ta_int\t1\t2\t3
                    numeric\tA Constrainedint\ta_constrainedint\t3\t3\t3
                    numeric\tB Float\tb_float\t1.5\t2.5\t3.5
                    unicode\tC Str\tc_str\tstring\tasdf\tbluey
                    unicode\tC Constrainedstr\tc_constrainedstr\tstring\tstring\tstring
                    unicode\tMyColor\td_enum\tgreen\tgreen\tblue
                    boolean\tE Bool\te_bool\tTRUE\tTRUE\tFALSE
                    datetime\tF Date\tf_date\t2025-21-10\t2025-21-10\t2025-21-10
                    datetime\tG Datetime\tg_datetime\t2025-21-10T13:36:16+00:00\t2025-21-10T13:36:16+00:00\t2025-21-10T13:36:16+00:00
                    datetime\tH Time\th_time\t13:36:16+00:00\t13:36:16+00:00\t13:36:16+00:00
                    datetime\tI Duration\ti_duration\tP2:33:03\tP2:33:03\tP2:33:03
                    numeric\tB Calcfloat\tb_calcfloat\t1.5\t5\t10.5"""

    model = DataTypesArrayTransposed
    data, metadata = read_tsv_string(tsv_string, False, True, header_depth=3, model = model)
    
    assert isinstance(data, list)
    assert len(data) == 3
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
