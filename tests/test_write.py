import pathlib

import pytest

from xlsxdatagrid.xlsxdatagrid import xdg_from_pydantic_object

from .csv_model import DataTypesArrayTransposed


def _as_delimited(text: str, delimiter: str) -> str:
    return text if delimiter == "\t" else text.replace("\t", delimiter)


@pytest.mark.parametrize(
    "is_transposed, exclude_metadata, exclude_header_lines",
    [
        (True, False, False),
        (True, True, False),
        (True, False, True),
        (True, True, True),
        (False, False, False),
        (False, True, False),
        (False, False, True),
        (False, True, True),
    ],
)
def test_xdg_from_pydantic_object(
    is_transposed: bool, exclude_metadata: bool, exclude_header_lines: bool
):
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
        dest_dir
        / f"test_from_pydantic_object-{is_transposed}-{exclude_metadata}-{exclude_header_lines}.xlsx"
    )

    out_fpth, _ = xdg_from_pydantic_object(
        pydantic_obj,
        fpth=fpth,
        is_transposed=is_transposed,
        exclude_metadata=exclude_metadata,
        exclude_header_lines=exclude_header_lines,
    )

    assert out_fpth.exists()
