import datetime
import json
import typing as ty

import pytest
from pydantic import BaseModel

from xlsxdatagrid.read import (
    pydantic_model_from_json_schema,
    read_csv_string,
    read_csv_string_with_metadata,
    read_excel,
    read_excel_from_metadata,
)
from xlsxdatagrid.xlsxdatagrid import DataGridMetaData

from .constants import PATH_JSONSCHEMA_RAW
from .csv_model import DataTypesArrayTransposed
from .edit_tsv_records_model import DistributionBoard
from .test_xlsxdatagrid import (
    ExampleArray,
    ExampleArrayTransposed,
    from_json_with_null,  # req. fixture  # noqa: F401
    write_table_test,  # req. fixture  # noqa: F401
)

schemas = [ExampleArray.model_json_schema(), ExampleArrayTransposed.model_json_schema()]
schemas = {s["title"]: s for s in schemas}


def _as_delimited(text: str, delimiter: str) -> str:
    return text if delimiter == "\t" else text.replace("\t", delimiter)


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
    metadata = DataGridMetaData(name="ExampleArray", title="Example Array")
    jsonschema = get_datamodel(metadata)
    assert jsonschema["title"] == "ExampleArray"


def test_read_excel_from_metadata(write_table_test):  # noqa: F811
    path, xl_tbl = write_table_test
    obj, metadata = read_excel_from_metadata(path, get_datamodel=get_datamodel)
    assert isinstance(obj, list)
    assert len(obj) == 3
    print("done")


def test_read_excel(write_table_test):  # noqa: F811
    path, xl_tbl = write_table_test
    is_transposed = xl_tbl.gridschema.is_transposed
    model = DataTypesArrayTransposed
    data, errors = read_excel(
        path,
        is_transposed=is_transposed,
        header_depth=xl_tbl.gridschema.header_depth,
        model=model,
    )
    assert isinstance(data, list)
    assert len(data) == 3


@pytest.mark.parametrize("delimiter", ["\t", ","], ids=["tsv", "csv"])
def test_read_csv_string(delimiter):
    string = """#Title=ExampleArray - HeaderDepth=3 - IsTransposed=False - DateTime=2025-10-29 11:07:21.014106 - DatamodelUrl=None											
numeric	numeric	numeric	unicode	unicode	unicode	boolean	datetime	datetime	datetime	datetime	numeric
A Int	A Constrainedint	B Float	C Str	C Constrainedstr	MyColor	E Bool	F Date	G Datetime	H Time	I Duration	B Calcfloat
a_int	a_constrainedint	b_float	c_str	c_constrainedstr	d_enum	e_bool	f_date	g_datetime	h_time	i_duration	b_calcfloat
1	3	1.5	string	string	green	TRUE	2025-10-29	2025-10-29T11:07:19+00:00	11:07:19+00:00	PT2H33M03S	1.5
2	3	2.5	asdf	string	green	TRUE	2025-10-29	2025-10-29T11:07:19+00:00	11:07:19+00:00	PT2H33M03S	5
3	3	3.5	bluey	string	blue	FALSE	2025-10-29	2025-10-29T11:07:19+00:00	11:07:19+00:00	PT2H33M03S	10.5
"""

    model = DataTypesArrayTransposed
    data_string = _as_delimited(string, delimiter)
    data, errors = read_csv_string(
        data_string, False, header_depth=3, model=model, delimiter=delimiter
    )

    assert isinstance(data, list)
    assert len(data) == 3
    print("done")


@pytest.mark.parametrize("delimiter", ["\t", ","], ids=["tsv", "csv"])
def test_read_csv_string_transposed(delimiter):
    string = """numeric	A Int	a_int	1	2	3
numeric	A Constrainedint	a_constrainedint	3	3	3
numeric	B Float	b_float	1.5	2.5	3.5
unicode	C Str	c_str	string	asdf	bluey
unicode	C Constrainedstr	c_constrainedstr	string	string	string
unicode	MyColor	d_enum	green	green	blue
boolean	E Bool	e_bool	TRUE	TRUE	FALSE
datetime	F Date	f_date	2025-10-22	2025-10-22	2025-10-22
datetime	G Datetime	g_datetime	2025-10-22T13:36:16+00:00	2025-10-22T13:36:16+00:00	2025-10-22T13:36:16+00:00
datetime	H Time	h_time	13:36:16+00:00	13:36:16+00:00	13:36:16+00:00
datetime	I Duration	i_duration	PT2H33M3S	PT2H33M3S	PT2H33M3S
numeric	B Calcfloat	b_calcfloat	1.5	5	10.5
"""

    model = DataTypesArrayTransposed
    data_string = _as_delimited(string, delimiter)
    data, errors = read_csv_string(
        data_string, True, header_depth=3, model=model, delimiter=delimiter
    )

    assert isinstance(data, list)
    assert len(data) == 3
    print("done")


@pytest.mark.parametrize("delimiter", ["\t", ","], ids=["tsv", "csv"])
def test_read_csv_string_with_metadata(delimiter):
    string = """#Title=ExampleArray - HeaderDepth=3 - IsTransposed=False - DateTime=2025-10-22 15:15:55.981465 - DatamodelUrl=None
    #some hash string comment that should be ignored												
section	numeric	numeric	numeric	unicode	unicode	unicode	boolean	datetime	datetime	datetime	datetime	numeric
title	A Int	A Constrainedint	B Float	C Str	C Constrainedstr	MyColor	E Bool	F Date	G Datetime	H Time	I Duration	B Calcfloat
name	a_int	a_constrainedint	b_float	c_str	c_constrainedstr	d_enum	e_bool	f_date	g_datetime	h_time	i_duration	b_calcfloat
	1	3	1.5	string	string	green	TRUE	2025-10-22	2025-10-22T15:15:56+00:00	15:15:56+00:00	PT2H33M03S	1.5
	2	3	2.5	asdf	string	green	TRUE	2025-10-22	2025-10-22T15:15:56+00:00	15:15:56+00:00	PT2H33M03S	5
	3	3	3.5	bluey	string	blue	FALSE	2025-10-22	2025-10-22T15:15:56+00:00	15:15:56+00:00	PT2H33M03S	10.5"""

    data_string = _as_delimited(string, delimiter)
    obj, metadata = read_csv_string_with_metadata(
        data_string, get_datamodel=get_datamodel, delimiter=delimiter
    )

    assert isinstance(obj, list)
    assert len(obj) == 3
    print("done")


@pytest.mark.parametrize("delimiter", ["\t", ","], ids=["tsv", "csv"])
def test_read_csv_string_with_metadata_transposed(delimiter):
    string = """#Title=ExampleArrayTransposed - HeaderDepth=3 - IsTransposed=True - DateTime=2025-10-22 15:42:29.557047 - DatamodelUrl=None
    #some hash string comment that should be ignored					
section	title	name	Column3	Column4	Column5
numeric	A Int	a_int	1	2	3
numeric	A Constrainedint	a_constrainedint	3	3	3
numeric	B Float	b_float	1.5	2.5	3.5
unicode	C Str	c_str	string	asdf	bluey
unicode	C Constrainedstr	c_constrainedstr	string	string	string
unicode	MyColor	d_enum	green	green	blue
boolean	E Bool	e_bool	TRUE	TRUE	FALSE
datetime	F Date	f_date	2025-10-22	2025-10-22	2025-10-22
datetime	G Datetime	g_datetime	2025-10-22T15:42:30+00:00	2025-10-22T15:42:30+00:00	2025-10-22T15:42:30+00:00
datetime	H Time	h_time	15:42:30+00:00	15:42:30+00:00	15:42:30+00:00
datetime	I Duration	i_duration	PT2H33M03S	PT2H33M03S	PT2H33M03S
numeric	B Calcfloat	b_calcfloat	1.5	5	10.5"""

    data_string = _as_delimited(string, delimiter)
    obj, metadata = read_csv_string_with_metadata(
        data_string, get_datamodel=get_datamodel, delimiter=delimiter
    )

    assert isinstance(obj, list)
    assert len(obj) == 3
    print("done")


def get_raw_jsonschema(metadata: DataGridMetaData) -> dict:
    return json.loads(PATH_JSONSCHEMA_RAW.read_text())


def test_read_excel_with_null(from_json_with_null):  # noqa: F811
    fpth, data, schema = from_json_with_null
    obj, metadata = read_excel_from_metadata(
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


def test_transposed_string_processing_issue():
    model = DistributionBoard
    tsv_string = """Abbreviation	DB
ClassificationUniclassProductNumber	Pr_60_70_22_22
ClassificationUniclassSystemNumber	
FunctionReference	
Id	2
ManufacturerWebsite	https://maxfordham.com/
Notes	
OverallLength	
Symbol	
TypeReference	1
Voltage	"""
    data, errors = read_csv_string(
        tsv_string, is_transposed=True, header_depth=1, model=model, delimiter="\t"
    )
    assert data != []
