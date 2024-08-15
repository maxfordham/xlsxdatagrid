from enum import Enum
from typing_extensions import Annotated
from datetime import date, datetime, time, timedelta

from pydantic import (
    BaseModel,
    RootModel,
    Field,
    ConfigDict,
    computed_field,
    StringConstraints,
    PlainSerializer,
    NaiveDatetime,
    # NaiveDate,
)
import pytest
import xlsxwriter as xw

from .constants import (
    PATH_XL,
    PATH_XL_MANY_SHEETS,
    PATH_XL_TRANSPOSED,
    PATH_XL_FROM_SCHEMA,
    PATH_XL_FROM_SCHEMA_TRANSPOSED,
)
from xlsxdatagrid.xlsxdatagrid import (
    write_table,
    get_data_and_schema,
    convert_records_to_datagrid_schema,
    XlTableWriter,
    DataGridSchema,
    convert_date_to_excel_ordinal,
    convert_list_records_to_dict_arrays,
)


class MyColor(Enum):
    RED = "red"
    GREEN = "green"
    BLUE = "blue"


class Test(BaseModel):
    a_int: int = Field(1, json_schema_extra=dict(section="numeric"))
    a_constrainedint: Annotated[int, Field(ge=0, le=10)] = Field(
        3, json_schema_extra=dict(section="numeric")
    )
    b_float: float = Field(1.5, json_schema_extra=dict(section="numeric"))
    c_str: str = Field("string", json_schema_extra=dict(section="unicode"))
    c_constrainedstr: Annotated[
        str,
        StringConstraints(
            max_length=10,
        ),
    ] = Field("string", json_schema_extra=dict(section="unicode"))
    d_enum: MyColor = Field(json_schema_extra=dict(section="unicode"))
    e_bool: bool = Field(True, json_schema_extra=dict(section="boolean"))
    f_date: date = Field(date.today(), json_schema_extra=dict(section="datetime"))
    g_datetime: NaiveDatetime = Field(
        datetime.now(), json_schema_extra=dict(section="datetime")
    )
    h_time: time = Field(
        datetime.now().time(), json_schema_extra=dict(section="datetime")
    )
    i_duration: timedelta = Field(
        timedelta(days=0, hours=2, minutes=33, seconds=3),
        json_schema_extra=dict(section="datetime"),
    )

    @computed_field(
        description="calc value",
        json_schema_extra=dict(formula="a_int * b_float", section="numeric"),
    )
    def b_calcfloat(self) -> float:
        return self.a_int * self.b_float


class Test1(BaseModel):
    a_int: int = Field(1, json_schema_extra=dict(section="numeric"))
    a_constrainedint: Annotated[int, Field(ge=0, le=10)] = Field(
        3, json_schema_extra=dict(section="numeric")
    )
    b_float: float = Field(1.5, json_schema_extra=dict(section="numeric"))
    c_str: str = Field("string", json_schema_extra=dict(section="unicode"))
    c_constrainedstr: Annotated[
        str,
        StringConstraints(
            max_length=10,
        ),
    ] = Field("string", json_schema_extra=dict(section="unicode"))
    d_enum: MyColor = Field(json_schema_extra=dict(section="unicode"))


class TestArray(RootModel):
    model_config = ConfigDict(
        json_schema_extra=dict(
            datagrid_index_name=("section", "title", "name"), is_transposed=False
        )
    )
    root: list[Test]


class TestArray1(RootModel):
    model_config = ConfigDict(
        json_schema_extra=dict(
            datagrid_index_name=("section", "title", "name"), is_transposed=False
        )
    )
    root: list[Test1]


class TestArrayTransposed(TestArray):
    model_config = ConfigDict(
        json_schema_extra=dict(
            datagrid_index_name=("section", "title", "name"), is_transposed=True
        )
    )


TEST_ARRAY_SCHEMA = {
    "$defs": {
        "MyColor": {
            "enum": ["red", "green", "blue"],
            "title": "MyColor",
            "type": "string",
        },
        "Test": {
            "properties": {
                "a_constrainedint": {
                    "default": 3,
                    "maximum": 10,
                    "minimum": 0,
                    "section": "numeric",
                    "title": "A " "Constrainedint",
                    "type": "integer",
                },
                "a_int": {
                    "default": 1,
                    "section": "numeric",
                    "title": "A Int",
                    "type": "integer",
                },
                "b_calcfloat": {
                    "description": "calc value",
                    "formula": "a_int * b_float",
                    "readOnly": True,
                    "section": "numeric",
                    "title": "B Calcfloat",
                    "type": "number",
                },
                "b_float": {
                    "default": 1.5,
                    "section": "numeric",
                    "title": "B Float",
                    "type": "number",
                },
                "c_constrainedstr": {
                    "default": "string",
                    "maxLength": 10,
                    "section": "unicode",
                    "title": "C " "Constrainedstr",
                    "type": "string",
                },
                "c_str": {
                    "default": "string",
                    "section": "unicode",
                    "title": "C Str",
                    "type": "string",
                },
                "d_enum": {
                    "allOf": [{"$ref": "#/$defs/MyColor"}],
                    "section": "unicode",
                },
                "e_bool": {
                    "default": True,
                    "section": "boolean",
                    "title": "E Bool",
                    "type": "boolean",
                },
                "f_date": {
                    "default": "2024-06-06",
                    "format": "date",
                    "section": "datetime",
                    "title": "F Date",
                    "type": "string",
                },
                "g_datetime": {
                    "default": "2024-06-06T10:42:54.822063",
                    "format": "date-time",
                    "section": "datetime",
                    "title": "G Datetime",
                    "type": "string",
                },
                "h_time": {
                    "default": "10:42:54.822257",
                    "format": "time",
                    "section": "datetime",
                    "title": "H Time",
                    "type": "string",
                },
                "i_duration": {
                    "default": "PT2H33M3S",
                    "format": "duration",
                    "section": "datetime",
                    "title": "I Duration",
                    "type": "string",
                },
            },
            "required": ["d_enum", "b_calcfloat"],
            "title": "Test",
            "type": "object",
        },
    },
    "datagrid_index_name": ("section", "title", "name"),
    "is_transposed": False,
    "items": {"$ref": "#/$defs/Test"},
    "title": "TestArrayTransposed",
    "type": "array",
}

TEST_ARRAY_SCHEMA_TRANSPOSED = {
    k: (lambda k, v: True if k == "is_transposed" else v)(k, v)
    for k, v in TEST_ARRAY_SCHEMA.items()
}

ARRAY_DATA = {
    "a_int": [1, 2, 3],
    "a_constrainedint": [3, 3, 3],
    "b_float": [1.5, 2.5, 3.5],
    "c_str": ["string", "asdf", "bluey"],
    "c_constrainedstr": ["string", "string", "string"],
    "d_enum": ["green", "green", "blue"],
    "e_bool": [True, True, False],
    "f_date": ["2024-06-06", "2024-06-06", "2024-06-06"],
    "g_datetime": [
        "2024-06-06T10:08:52.078770",
        "2024-06-06T10:08:52.078770",
        "2024-06-06T10:08:52.078770",
    ],
    "h_time": ["10:08:52.078959", "10:08:52.078959", "10:08:52.078959"],
    "i_duration": ["PT2H33M3S", "PT2H33M3S", "PT2H33M3S"],
    "b_calcfloat": [1.5, 5.0, 10.5],
}

ARRAY_DATA1 = {k: v * 2 for k, v in ARRAY_DATA.items() if k in Test1.model_fields}


def array_to_records(di):
    length = len(list(di.values())[0])
    keys = list(di.keys())
    return [dict(zip(keys, [di[k][n] for k in keys])) for n in range(0, length)]


def get_test_array(is_transposed=False):
    t1, t2, t3 = (
        Test(d_enum=MyColor.GREEN),
        Test(a_int=2, b_float=2.5, c_str="asdf", d_enum=MyColor.GREEN),
        Test(a_int=3, b_float=3.5, c_str="bluey", d_enum=MyColor.BLUE, e_bool=False),
    )

    if is_transposed:
        return TestArrayTransposed([t1, t2, t3])
    else:
        return TestArray([t1, t2, t3])


def get_pydantic_test_inputs(is_transposed=False):

    if is_transposed:
        return PATH_XL_TRANSPOSED, get_test_array(is_transposed)
    else:
        return PATH_XL, get_test_array(is_transposed)


@pytest.mark.parametrize("is_transposed", [True, False])
def test_pydantic_object_write_table(is_transposed):
    fpth_xl, pyd_obj = get_pydantic_test_inputs(is_transposed=is_transposed)

    fpth_xl.unlink(missing_ok=True)
    pyd_obj = get_test_array()
    data, gridschema = get_data_and_schema(pyd_obj)
    xl_tbl = XlTableWriter(data=data, gridschema=gridschema)
    workbook = xw.Workbook(str(fpth_xl))
    write_table(workbook, xl_tbl)
    workbook.close()
    assert fpth_xl.is_file()


def test_pydantic_objects_write_tables():
    fpth_xl, pyd_obj = get_pydantic_test_inputs(is_transposed=False)
    fpth_xl = PATH_XL_MANY_SHEETS
    fpth_xl.unlink(missing_ok=True)
    pyd_obj = TestArray(array_to_records(ARRAY_DATA))
    pyd_obj1 = TestArray1(array_to_records(ARRAY_DATA1))

    data, gridschema = get_data_and_schema(pyd_obj)
    xl_tbl = XlTableWriter(data=data, gridschema=gridschema)
    workbook = xw.Workbook(str(fpth_xl))
    write_table(workbook, xl_tbl)

    data1, gridschema1 = get_data_and_schema(pyd_obj1)
    xl_tbl1 = XlTableWriter(data=data1, gridschema=gridschema1)
    write_table(workbook, xl_tbl1)

    workbook.close()
    assert fpth_xl.is_file()


def get_schema_test_inputs(is_transposed=False):
    if is_transposed:
        return PATH_XL_FROM_SCHEMA_TRANSPOSED, TEST_ARRAY_SCHEMA_TRANSPOSED, ARRAY_DATA
    else:
        return PATH_XL_FROM_SCHEMA, TEST_ARRAY_SCHEMA, ARRAY_DATA


@pytest.mark.parametrize("is_transposed", [True, False])
def test_schema_and_data_write_table(is_transposed):
    fpth_xl, schema, data = get_schema_test_inputs(is_transposed=is_transposed)

    fpth_xl.unlink(missing_ok=True)
    gridschema = convert_records_to_datagrid_schema(schema)
    dgschema = DataGridSchema(**gridschema)
    xl_tbl = XlTableWriter(gridschema=gridschema, data=data)
    workbook = xw.Workbook(str(fpth_xl))
    write_table(workbook, xl_tbl)
    workbook.close()
    assert fpth_xl.is_file()


def test_schema_and_data_from_digital_schedules_api():
    import requests
    import jsonref
    import pathlib

    response = requests.get(
        "https://aectemplater-dev.maxfordham.com/type_specs/project_revision/1/object/602/grid?override_units=true"
    )
    fpth_xl = pathlib.Path("./test.xlsx")
    data = jsonref.replace_refs(response.json())
    data_array = convert_list_records_to_dict_arrays(data["data"])

    gridschema = convert_records_to_datagrid_schema(data["$schema"])
    # HOTFIX: Replace all anyOfs with the first type
    for field in gridschema["fields"]:
        if "anyOf" in field.keys():
            field["type"] = field["anyOf"][0]["type"]
            field.pop("anyOf")
    gridschema["datagrid_index_name"] = ("section", "unit", "title")
    gridschema["is_transposed"] = False

    xl_tbl = XlTableWriter(gridschema=gridschema, data=data_array)
    workbook = xw.Workbook(str(fpth_xl))
    write_table(workbook, xl_tbl)
    workbook.close()
    assert fpth_xl.is_file()
