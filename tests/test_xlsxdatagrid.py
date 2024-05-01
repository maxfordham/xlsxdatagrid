import pathlib
from pydantic import (
    BaseModel,
    RootModel,
    Field,
    ConfigDict,
    computed_field,
    StringConstraints,
)
from enum import Enum
from typing_extensions import Annotated
from datetime import date, datetime
import xlsxwriter as xw

from xlsxdatagrid.xlsxdatagrid import write_table, get_data_and_schema, XlTableWriter


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
    f_date: date = Field(date.today(), json_schema_extra=dict(section="date"))
    g_datetime: datetime = Field(datetime.now(), json_schema_extra=dict(section="date"))

    @computed_field(
        description="calc value",
        json_schema_extra=dict(formula="a_int * b_float", section="numeric"),
    )
    def b_calcfloat(self) -> float:
        return self.a_int * self.b_float


class Test1(BaseModel):
    b_int: int = Field(1, json_schema_extra=dict(section="numeric"))
    b_constrainedint: Annotated[int, Field(ge=0, le=10)] = Field(
        3, json_schema_extra=dict(section="numeric")
    )


class TestArray(RootModel):
    model_config = ConfigDict(
        json_schema_extra=dict(
            datagrid_index_name=("section", "title", "name"), is_transposed=False
        )
    )
    root: list[Test]


class TestArrayTransposed(TestArray):
    model_config = ConfigDict(
        json_schema_extra=dict(
            datagrid_index_name=("section", "title", "name"), is_transposed=True
        )
    )


class TestArray1(RootModel):
    root: list[Test1]


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


def test_write_table():
    pyd_obj = get_test_array()
    data, gridschema = get_data_and_schema(pyd_obj)
    xl_tbl = XlTableWriter(data=data, gridschema=gridschema)
    name = f"{gridschema.title}"
    PATH_OUT = pathlib.Path(__file__).parent / f"{name}.xlsx"
    workbook = xw.Workbook(str(PATH_OUT))
    write_table(workbook, xl_tbl)
    workbook.close()
    assert PATH_OUT.is_file()
    print("done")


def test_write_table_transposed():
    pyd_obj = get_test_array(is_transposed=True)
    data, gridschema = get_data_and_schema(pyd_obj)
    xl_tbl = XlTableWriter(data=data, gridschema=gridschema)
    name = f"{gridschema.title}"
    PATH_OUT = pathlib.Path(__file__).parent / f"{name}.xlsx"
    workbook = xw.Workbook(str(PATH_OUT))
    write_table(workbook, xl_tbl)
    workbook.close()
    assert PATH_OUT.is_file()
    print("done")
