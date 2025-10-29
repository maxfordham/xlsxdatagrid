# SPDX-FileCopyrightText: 2024-present jgunstone <j.gunstone@maxfordham.com>
#
# SPDX-License-Identifier: MIT

"""
root package for xlsxdatagrid
expected usage:
```py
import xlsxdatagrid as xdg

xdg.xdg_from_json(...)  # outputs excel file from json data (list of dicts, or dict of columnar arrays)
xdg.xdg_from_dataframe(...)  # outputs excel file from pandas dataframe
etc.
```
"""

from xlsxdatagrid.read import (
    read_csv_string,
    read_excel,
    # read_csv_string_from_metadata,
    read_excel_from_metadata,
)
from xlsxdatagrid.xlsxdatagrid import (
    # wb_from_pydantic_object,
    # wb_from_pydantic_objects,
    wb_from_dataframe,
    wb_from_dataframes,
    wb_from_json,
    wb_from_jsons,
    xdg_from_dataframe,
    xdg_from_dataframes,
    xdg_from_json,
    xdg_from_jsons,
    xdg_from_pydantic_object,
    xdg_from_pydantic_objects,
)

__all__ = [
    "xdg_from_pydantic_object",
    "xdg_from_pydantic_objects",
    "xdg_from_dataframe",
    "xdg_from_dataframes",
    "xdg_from_json",
    "xdg_from_jsons",
    "wb_from_dataframe",
    "wb_from_dataframes",
    "wb_from_json",
    "wb_from_jsons",
    "read_excel_from_metadata",  # TODO: improve functionality here...
    "read_csv_string",
    "csv_from_string",
    "read_excel",
]
from_pydantic_object = xdg_from_pydantic_object  # TODO: delete
from_pydantic_objects = xdg_from_pydantic_objects  # TODO: delete
