from __future__ import annotations

from typing import List, Optional, Literal
from pydantic import BaseModel, Field, RootModel, conint, constr, confloat
from datetime import date, datetime, time, timedelta


class DataTypesArrayTransposedItem(BaseModel):
    a_int: Optional[int] = Field(
        None,
        alias='a_int',
        description='Simple integer value',
        title='A Int',
    )
    a_constrainedint: Optional[conint(ge=0, le=100)] = Field(
        None,
        alias='a_constrainedint',
        description='Integer constrained between 0 and 100',
        title='A Constrained Int',
    )
    b_float: Optional[float] = Field(
        None,
        alias='b_float',
        description='Floating point number',
        title='B Float',
    )
    c_str: Optional[str] = Field(
        None,
        alias='c_str',
        description='Basic string field',
        title='C Str',
    )
    c_constrainedstr: Optional[constr(min_length=1, max_length=50)] = Field(
        None,
        alias='c_constrainedstr',
        description='String constrained to length 1–50',
        title='C Constrained Str',
    )
    d_enum: Optional[Literal["red", "green", "blue"]] = Field(
        None,
        alias='d_enum',
        description='String value that must be one of: "red", "green", or "blue"',
        title='D Enum',
    )
    e_bool: Optional[bool] = Field(
        None,
        alias='e_bool',
        description='Boolean value (True/False)',
        title='E Bool',
    )
    f_date: Optional[date] = Field(
        None,
        alias='f_date',
        description='Date value (YYYY-MM-DD)',
        title='F Date',
    )
    g_datetime: Optional[datetime] = Field(
        None,
        alias='g_datetime',
        description='Datetime value (ISO format)',
        title='G Datetime',
    )
    h_time: Optional[time] = Field(
        None,
        alias='h_time',
        description='Time of day (HH:MM:SS)',
        title='H Time',
    )
    i_duration: Optional[timedelta] = Field(
        None,
        alias='i_duration',
        description='Time duration value',
        title='I Duration',
    )
    b_calcfloat: Optional[confloat(gt=0)] = Field(
        None,
        alias='b_calcfloat',
        description='Calculated float value that must be positive',
        title='B Calc Float',
    )


class DataTypesArrayTransposed(RootModel[List[DataTypesArrayTransposedItem]]):
    root: List[DataTypesArrayTransposedItem] = Field(
        ...,
        title='Data Types Array Transposed',
    )
