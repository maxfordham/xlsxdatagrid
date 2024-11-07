import typing as ty
from datetime import date, datetime, time, timedelta
from enum import StrEnum

import jsonref
import pandas as pd
import pytest
import requests
import xlsxwriter as xw
from dirty_equals import IsInstance
from frictionless import Package, Resource
from jsonref import replace_refs
from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    NaiveDatetime,
    # NaiveDate,
    RootModel,
    StringConstraints,
    computed_field,
)
from typing_extensions import Annotated

import xlsxdatagrid.xlsxdatagrid as xdg
from xlsxdatagrid.xlsxdatagrid import (
    DataGridSchema,
    FieldSchema,
    XlTableWriter,
    coerce_schema,
    convert_list_records_to_dict_arrays,
    convert_records_to_datagrid_schema,
    from_pydantic_object,
    from_pydantic_objects,
    wb_from_dataframe,
    wb_from_dataframes,
    write_table,
    convert_dict_arrays_to_list_records
)

from . import constants as c


class MyColor(StrEnum):
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
        return c.PATH_XL_TRANSPOSED, get_test_array(is_transposed)
    else:
        return c.PATH_XL, get_test_array(is_transposed)


@pytest.fixture(params=[True, False])
def write_table_test(request):
    fpth, pyd_obj = get_pydantic_test_inputs(is_transposed=request.param)
    fpth.unlink(missing_ok=True)
    fpth = from_pydantic_object(pyd_obj, fpth)
    return fpth


def test_pydantic_object_write_table(write_table_test):
    fpth = write_table_test
    assert fpth.is_file()


def test_pydantic_objects_write_tables():
    fpth, pyd_obj = get_pydantic_test_inputs(is_transposed=False)
    fpth = c.PATH_XL_MANY_SHEETS
    fpth.unlink(missing_ok=True)
    pyd_obj = TestArray(convert_dict_arrays_to_list_records(ARRAY_DATA))
    pyd_obj1 = TestArray1(convert_dict_arrays_to_list_records(ARRAY_DATA1))

    fpth = from_pydantic_objects([pyd_obj, pyd_obj1], fpth)
    assert fpth.is_file()


def get_schema_test_inputs(is_transposed=False):
    if is_transposed:
        return (
            c.PATH_XL_FROM_SCHEMA_TRANSPOSED,
            TEST_ARRAY_SCHEMA_TRANSPOSED,
            ARRAY_DATA,
        )
    else:
        return c.PATH_XL_FROM_SCHEMA, TEST_ARRAY_SCHEMA, ARRAY_DATA


@pytest.mark.parametrize("is_transposed", [True, False])
def test_schema_and_data_write_table(is_transposed):
    fpth, schema, data = get_schema_test_inputs(is_transposed=is_transposed)

    fpth.unlink(missing_ok=True)
    gridschema = convert_records_to_datagrid_schema(schema)
    DataGridSchema(**gridschema)
    xl_tbl = XlTableWriter(gridschema=gridschema, data=data)
    workbook = xw.Workbook(str(fpth))
    write_table(workbook, xl_tbl)
    workbook.close()
    assert fpth.is_file()


@pytest.mark.skip(reason="needs the MXF api so skip for CI")
class TestDigitalSchedulesApi:
    def test_schema_and_data_from_digital_schedules_api():
        fpth = c.PATH_XL_FROM_API
        response = requests.get(
            "https://aectemplater-dev.maxfordham.com/type_specs/project_revision/1/object/602/grid?override_units=true"
        )
        assert (
            response.status_code == 200
        ), f"API request failed with status code {response.status_code}"

        fpth.unlink(missing_ok=True)
        data = jsonref.replace_refs(response.json(), merge_props=True)
        data["data"] = data["data"] + data["data"]
        data_array = convert_list_records_to_dict_arrays(data["data"])

        gridschema = convert_records_to_datagrid_schema(data["$schema"])
        gridschema["datagrid_index_name"] = ("section", "unit", "name")
        gridschema["is_transposed"] = True

        xl_tbl = XlTableWriter(gridschema=gridschema, data=data_array)
        workbook = xw.Workbook(str(fpth))
        write_table(workbook, xl_tbl)
        workbook.close()
        assert fpth.is_file()


def test_IsInstance():
    class Foo(BaseModel):
        a: str = "a"

    class FooArray(RootModel):
        root: list[Foo] = [Foo()]

    assert Foo() == IsInstance(Foo)
    assert Foo() == IsInstance(BaseModel)
    assert Foo() == IsInstance(Foo, only_direct_instance=True)
    assert Foo() != IsInstance(BaseModel, only_direct_instance=True)
    assert isinstance(Foo(), BaseModel)
    assert issubclass(Foo, BaseModel)
    assert not FooArray() == IsInstance(Foo)


def test_enum_field_schema():
    class Test(BaseModel):
        m_color: Annotated[MyColor, Field(json_schema_extra={"section": "unicode"})]

    item = replace_refs(Test.model_json_schema(), merge_props=True)
    name = "m_color"
    fschema = item.get("properties").get(name) | {"name": name}

    f = FieldSchema(**fschema)
    assert f == IsInstance(FieldSchema)


def test_coerce_schema():
    class Foo(BaseModel):
        a: str = "a"

    class FooArray(RootModel):
        root: list[Foo] = [Foo()]

    schema = {
        "$defs": {
            "Foo": {
                "properties": {"a": {"default": "a", "title": "A", "type": "string"}},
                "title": "Foo",
                "type": "object",
            }
        },
        "default": [{"a": "a"}],
        "items": {"$ref": "#/$defs/Foo"},
        "title": "FooArray",
        "type": "array",
    }

    assert coerce_schema(FooArray) == IsInstance(
        DataGridSchema, only_direct_instance=True
    )
    assert coerce_schema(FooArray()) == IsInstance(
        DataGridSchema, only_direct_instance=True
    )
    assert coerce_schema(schema) == IsInstance(
        DataGridSchema, only_direct_instance=True
    )
    assert coerce_schema(
        DataGridSchema(**convert_records_to_datagrid_schema(schema))
    ) == IsInstance(DataGridSchema, only_direct_instance=True)

    assert coerce_schema(TestArrayTransposed) == IsInstance(DataGridSchema)

    assert coerce_schema(TestArray) == IsInstance(DataGridSchema)


def test_datapackage():
    class Foo(BaseModel):
        a: str = "a"
        b: int = 2
        c: float = 2.3

    class FooArray(RootModel):
        root: list[Foo] = [Foo()]

    schema = coerce_schema(FooArray).model_dump(exclude_none=True, exclude="type")
    data = [{k: n * v for k, v in Foo().model_dump().items()} for n in range(1, 4)]

    Resource(data=data, schema=schema)
    Package(
        resources=[Resource(data=pd.DataFrame(data)) for d in data]
    )  # from arguments
    print("done")


def x_squared():
    x = range(-5, 6)
    y = [_**2 for _ in x]
    return pd.DataFrame({"x": x, "y": y})


def x_cubed():
    x = range(-5, 6)
    y = [_**3 for _ in x]
    return pd.DataFrame({"x": x, "y": y})


def test_wb_from_dataframe():
    fpth = c.PATH_FROM_DF_WITH_CHART
    fpth.unlink(missing_ok=True)
    df = x_squared()
    workbook, xl_tbl, worksheet = wb_from_dataframe(df, fpth)

    # TODO: support xl chart from vega-lite spec?
    #       https://frictionlessdata.io/blog/2017/03/31/data-package-views-proposal/#graph-spec

    chart = workbook.add_chart({"type": "line"})

    chart.add_series(
        {
            "name": "x squared",
            "categories": [worksheet.name] + list(xl_tbl.rng_arrays["x"]),
            "values": [worksheet.name] + list(xl_tbl.rng_arrays["y"]),
        }
    )

    # Add a chart title and some axis labels.
    chart.set_title({"name": "x squared"})
    chart.set_x_axis({"name": "x"})
    chart.set_y_axis({"name": "y"})

    # Set an Excel chart style.
    chart.set_style(11)

    # Add the chart to the chartsheet.
    depth = xl_tbl.gridschema.header_depth + 4
    width = len(xl_tbl.gridschema.fields) + 2
    worksheet.insert_chart(depth, width, chart)
    workbook.close()

    assert fpth.is_file()


def test_wb_from_dataframes():
    fpth = c.PATH_FROM_DF_WITH_MANY_CHARTS
    fpth.unlink(missing_ok=True)
    df_labels = pd.DataFrame(
        {"a": [1, 2, 3, None], "b": list("abcd"), "c": [None, "e", "f", pd.NA]}
    )
    # df_labels = df_labels.fillna("")
    workbook, worksheets, xl_tbls = wb_from_dataframes(
        [x_squared(), x_cubed(), df_labels], fpth
    )
    workbook.close()
    assert fpth.is_file()


@pytest.fixture
def from_json_with_null():
    fpth = c.PATH_FROM_JSON
    fpth.unlink(missing_ok=True)

    class TestItem(BaseModel):
        a: ty.Optional[int]
        b: str
        c: ty.Optional[str]

    class TestGrid(RootModel):
        root: list[TestItem]

    data = [
        {"a": 1, "b": "a", "c": None},
        {"a": 2, "b": "b", "c": "e"},
        {"a": 3, "b": "c", "c": "f"},
        {"a": None, "b": "d", "c": None},
    ]
    xdg.from_json(data, schema=TestGrid, fpth=fpth)
    return fpth, data, TestGrid


def test_from_json(from_json_with_null):
    fpth, data, TestGrid = from_json_with_null
    assert fpth.is_file()


@pytest.mark.parametrize("is_transposed", [True, False])
def test_from_json_empty_data(is_transposed):
    class TestItem(BaseModel):
        a: ty.Optional[int]
        b: str
        c: ty.Optional[str]

    class TestGrid(RootModel):
        root: list[TestItem]

    fpth = (
        c.PATH_FROM_JSON_EMPTY if is_transposed else c.PATH_FROM_JSON_EMPTY_TRANSPOSED
    )

    data = [dict(a=2, b="b", c=None)]
    xdg.from_json(data, schema=TestGrid, fpth=fpth, is_transposed=is_transposed)
    assert fpth.is_file()
