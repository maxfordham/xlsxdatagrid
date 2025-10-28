# SPDX-FileCopyrightText: 2024-present jgunstone <j.gunstone@maxfordham.com>
#
# SPDX-License-Identifier: MIT

"""
root package for xlsxdatagrid
expected usage:
```py
import xlsxdatagrid as xdg

xdg.from_json(...)  # outputs excel file from json data (list of dicts, or dict of columnar arrays)
xdg.from_dataframe(...)  # outputs excel file from pandas dataframe
etc.
```
"""

from xlsxdatagrid.read import (
    read_csv_string,
    # read_csv_string_from_metadata,
    read_excel,  # read_excel_from_metadata
    read_excel_with_model,  # read_excel
)
from xlsxdatagrid.xlsxdatagrid import (
    from_dataframe,  # xdg_from_dataframe
    from_dataframes,  # xdg_from_dataframes
    from_json,  # xdg_from_json
    from_jsons,  # xdg_from_jsons
    from_pydantic_object,  # xdg_from_pydantic_object
    from_pydantic_objects,  # xdg_from_pydantic_objects
    # wb_from_pydantic_object,
    # wb_from_pydantic_objects,
    wb_from_dataframe,
    wb_from_dataframes,
    wb_from_json,
    wb_from_jsons,
)

__all__ = [
    "from_pydantic_object",
    "from_pydantic_objects",
    "from_dataframe",
    "from_dataframes",
    "from_json",
    "from_jsons",
    "wb_from_dataframe",
    "wb_from_dataframes",
    "wb_from_json",
    "wb_from_jsons",
    "read_excel",  # TODO: improve functionality here...
    "read_csv_string",
    "csv_from_string",
    "read_excel_with_model",
]
