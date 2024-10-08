# generated by datamodel-codegen:
#   filename:  test.json
#   timestamp: 2024-09-19T14:16:11+00:00

from __future__ import annotations

from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class DEnum(Enum):
    yellow = "yellow"
    red = "red"
    violet = "violet"


class Test(BaseModel):
    a_int: Optional[int] = Field(1, title="A Int")
    DEnum: DEnum = Field(..., description="pick colour")
