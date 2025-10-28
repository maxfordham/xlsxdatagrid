from datetime import date, datetime, time, timedelta
from enum import StrEnum

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


class MyColor(StrEnum):
    RED = "red"
    GREEN = "green"
    BLUE = "blue"


class DataTypes(BaseModel):
    """
    Many data types defined, to be used as a row in excel files
    """

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


class DataTypesBasicFields(BaseModel):
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


class DataTypesArray(RootModel):
    """
    Array of D Types - Rows of excel file
    """

    model_config = ConfigDict(
        json_schema_extra=dict(
            datagrid_index_name=("section", "title", "name"), is_transposed=False
        )
    )
    root: list[DataTypes]


class DataTypesArrayTransposed(RootModel):
    """
    Array of D Types - Rows of excel file
    """

    model_config = ConfigDict(
        json_schema_extra=dict(
            datagrid_index_name=("section", "title", "name"), is_transposed=True
        )
    )
    root: list[DataTypes]
