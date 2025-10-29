from __future__ import annotations

from datetime import date, datetime, time, timedelta
from enum import Enum
from typing import List, Literal, Optional

from pydantic import BaseModel, ConfigDict, Field, RootModel, StringConstraints
from typing_extensions import Annotated


class MyColor(str, Enum):
    red = "red"
    green = "green"
    blue = "blue"


class DataTypesArrayTransposedItem(BaseModel):
    a_constrainedint: Annotated[int, Field(ge=1, le=10)] = Field(
        3,
        title="A Constrainedint",
        json_schema_extra=dict(
            section="numeric",
        ),
    )

    a_int: Optional[int] = Field(
        1,
        title="A Int",
        json_schema_extra=dict(section="numeric"),
    )

    b_float: Optional[float] = Field(
        1.5,
        title="B Float",
        json_schema_extra=dict(section="numeric"),
    )

    c_constrainedstr: Annotated[str, StringConstraints(min_length=0, max_length=20)] = (
        Field(
            "string",
            title="C Constrainedstr",
            json_schema_extra=dict(
                section="unicode",
            ),
        )
    )

    c_str: Optional[str] = Field(
        "string",
        title="C Str",
        json_schema_extra=dict(section="unicode"),
    )

    d_enum: MyColor = Field(
        "red",
        title="D Enum",
        json_schema_extra=dict(
            section="unicode",
        ),
    )

    e_bool: Optional[bool] = Field(
        True,
        title="E Bool",
        json_schema_extra=dict(section="boolean"),
    )

    f_date: Optional[date] = Field(
        "2024-06-06",
        title="F Date",
        json_schema_extra=dict(section="datetime"),
    )

    g_datetime: Optional[datetime] = Field(
        "2024-06-06T10:42:54.822063",
        title="G Datetime",
        json_schema_extra=dict(section="datetime"),
    )

    h_time: Optional[time] = Field(
        "10:42:54.822257",
        title="H Time",
        json_schema_extra=dict(section="datetime"),
    )

    i_duration: Optional[timedelta] = Field(
        "PT2H33M3S",
        title="I Duration",
        json_schema_extra=dict(section="datetime"),
    )

    model_config = ConfigDict(
        title="Test",
        json_schema_extra=dict(
            required=["d_enum", "b_calcfloat"],
        ),
    )


class DataTypesArrayTransposed(RootModel):
    model_config = ConfigDict(
        title="ExampleArrayTransposed",
        json_schema_extra=dict(
            datagrid_index_name=("section", "title", "name"),
        ),
    )
    root: List[DataTypesArrayTransposedItem]
