import pathlib

import pytest

from xlsxdatagrid.read import read_excel
from xlsxdatagrid.xlsxdatagrid import xdg_from_pydantic_object

from .csv_model import DataTypesArrayTransposed


def _as_delimited(text: str, delimiter: str) -> str:
    return text if delimiter == "\t" else text.replace("\t", delimiter)


@pytest.mark.parametrize(
    "is_transposed, exclude_metadata",
    [
        (True, False),
        (True, True),
        (False, False),
        (False, True),
    ],
)
def test_xdg_from_pydantic_object(is_transposed: bool, exclude_metadata: bool):
    data = [
        {
            "a_constrainedint": 3,
            "a_int": 1,
            "b_float": 1.5,
            "c_constrainedstr": "string",
            "c_str": "string",
            "d_enum": "green",
            "e_bool": True,
            "f_date": "2025-10-24",
            "g_datetime": "2025-10-24T11:16:17Z",
            "h_time": "11:16:17Z",
            "i_duration": "PT2H33M3S",
        },
        {
            "a_constrainedint": 3,
            "a_int": 2,
            "b_float": 2.5,
            "c_constrainedstr": "string",
            "c_str": "asdf",
            "d_enum": "green",
            "e_bool": True,
            "f_date": "2025-10-24",
            "g_datetime": "2025-10-24T11:16:17Z",
            "h_time": "11:16:17Z",
            "i_duration": "PT2H33M3S",
        },
        {
            "a_constrainedint": 3,
            "a_int": 3,
            "b_float": 3.5,
            "c_constrainedstr": "string",
            "c_str": "bluey",
            "d_enum": "blue",
            "e_bool": False,
            "f_date": "2025-10-24",
            "g_datetime": "2025-10-24T11:16:17Z",
            "h_time": "11:16:17Z",
            "i_duration": "PT2H33M3S",
        },
    ]

    dest_dir = pathlib.Path("tests/xl/pydantic")
    dest_dir.mkdir(parents=True, exist_ok=True)

    pydantic_obj = DataTypesArrayTransposed(data)
    fpth = (
        dest_dir / f"test_from_pydantic_object-{is_transposed}-{exclude_metadata}.xlsx"
    )

    out_fpth, _ = xdg_from_pydantic_object(
        pydantic_obj,
        fpth=fpth,
        is_transposed=is_transposed,
        exclude_metadata=exclude_metadata,
    )

    assert out_fpth.exists()

    data, errors = read_excel(
        out_fpth,
        is_transposed=is_transposed,
        header_depth=3,
        model=DataTypesArrayTransposed,
    )

    assert not errors
    assert isinstance(data, list)
    assert len(data) == 3


def test_optional_enum_write():
    from enum import Enum
    from typing import Optional

    from pydantic import BaseModel, RootModel

    class ColorEnum(str, Enum):
        RED = "red"
        GREEN = "green"
        BLUE = "blue"

    class ModelWithOptionalEnum(BaseModel):
        color: Optional[ColorEnum]
        value: int

    class ModelWithOptionalEnumList(RootModel):
        root: list[ModelWithOptionalEnum]

    data = [
        {"color": "red", "value": 10},
        {"color": "green", "value": 20},
        {"color": "blue", "value": 30},
        # {"color": None, "value": 40},
    ]

    pydantic_object = ModelWithOptionalEnumList(data)

    dest_dir = pathlib.Path("tests/xl/pydantic")
    dest_dir.mkdir(parents=True, exist_ok=True)

    fpth = dest_dir / "test_optional_enum_write.xlsx"

    out_fpth, _ = xdg_from_pydantic_object(
        pydantic_object,
        fpth=fpth,
        is_transposed=False,
        exclude_metadata=False,
    )

    assert out_fpth.exists()

    read_data, errors = read_excel(
        out_fpth,
        is_transposed=False,
        header_depth=1,
        model=ModelWithOptionalEnumList,
    )


def test_enum_write():
    from enum import Enum

    from pydantic import BaseModel, RootModel

    class ColorEnum(str, Enum):
        RED = "red"
        GREEN = "green"
        BLUE = "blue"

    class ModelWithEnum(BaseModel):
        color: ColorEnum
        value: int

    class ModelWithEnumList(RootModel):
        root: list[ModelWithEnum]

    data = [
        {"color": "red", "value": 10},
        {"color": "green", "value": 20},
        {"color": "blue", "value": 30},
        # {"color": None, "value": 40},
    ]

    pydantic_object = ModelWithEnumList(data)

    dest_dir = pathlib.Path("tests/xl/pydantic")
    dest_dir.mkdir(parents=True, exist_ok=True)

    fpth = dest_dir / "test_enum_write.xlsx"

    out_fpth, _ = xdg_from_pydantic_object(
        pydantic_object,
        fpth=fpth,
        is_transposed=False,
        exclude_metadata=False,
    )

    assert out_fpth.exists()

    read_data, errors = read_excel(
        out_fpth,
        is_transposed=False,
        header_depth=1,
        model=ModelWithEnumList,
    )
