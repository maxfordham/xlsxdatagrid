from __future__ import annotations

from typing import List, Optional, Literal
from pydantic import BaseModel, Field, RootModel, ConfigDict,conint, constr
from datetime import date, datetime, time, timedelta
from typing import List, Literal, Optional

class DataTypesArrayTransposedItem(BaseModel):
    a_int: Optional[int] = Field(
        None,
        alias='a_int',
        description='Simple integer value',
        title='A Int',
        json_schema_extra=dict(section="numeric"),
    )
    a_constrainedint: Optional[conint(ge=0, le=100)] = Field(
        None,
        alias='a_constrainedint',
        description='Integer constrained between 0 and 100',
        title='A Constrained Int',
        json_schema_extra=dict(section="numeric"),
    )
    b_float: Optional[float] = Field(
        None,
        alias='b_float',
        description='Floating point number',
        title='B Float',
        json_schema_extra=dict(section="numeric"),
    )
    c_str: Optional[str] = Field(
        None,
        alias='c_str',
        description='Basic string field',
        title='C Str',
        json_schema_extra=dict(section="unicode"),
    )
    c_constrainedstr: Optional[constr(min_length=1, max_length=50)] = Field(
        None,
        alias='c_constrainedstr',
        description='String constrained to length 1–50',
        title='C Constrained Str',
        json_schema_extra=dict(section="unicode"),
    )
    d_enum: Optional[Literal["red", "green", "blue"]] = Field(
        None,
        alias='d_enum',
        description='String value that must be one of: "red", "green", or "blue"',
        title='D Enum',
        json_schema_extra=dict(section="unicode"),
    )
    e_bool: Optional[bool] = Field(
        None,
        alias='e_bool',
        description='Boolean value (True/False)',
        title='E Bool',
        json_schema_extra=dict(section="boolean"),
    )
    f_date: Optional[date] = Field(
        None,
        alias='f_date',
        description='Date value (YYYY-MM-DD)',
        title='F Date',
        json_schema_extra=dict(section="datetime"),
    )
    g_datetime: Optional[datetime] = Field(
        None,
        alias='g_datetime',
        description='Datetime value (ISO format)',
        title='G Datetime',
        json_schema_extra=dict(section="datetime"),
    )
    h_time: Optional[time] = Field(
        None,
        alias='h_time',
        description='Time of day (HH:MM:SS)',
        title='H Time',
        json_schema_extra=dict(section="datetime"),
    )
    i_duration: Optional[timedelta] = Field(
        None,
        alias='i_duration',
        description='Time duration value',
        title='I Duration',
        json_schema_extra=dict(section="datetime"),
    )


class DataTypesArrayTransposed(RootModel):
    model_config = ConfigDict(
        json_schema_extra=dict(
            datagrid_index_name=("section", "title", "name"),
        )
    )
    root: List[DataTypesArrayTransposedItem] = Field(
        ...,
        title='Data Types Array Transposed',
    )
