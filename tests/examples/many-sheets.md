---
title: "many sheets"
---

::: {.callout-note collapse="true" icon=false}


## code

```py
import pathlib
import typing as ty
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
from xlsxdatagrid.xlsxdatagrid import (
    convert_dict_arrays_to_list_records,
    from_pydantic_objects
)

from xlsxdatagrid.demo_schemas.dtypes import (
    MyColor,
    DataTypes,
    DataTypesBasicFields,
    DataTypesArray,
    DataTypesArrayTransposed
)

ARRAY_DATA = {
    "a_int": [1, 2, 3],
    "a_constrainedint": [3, 3, 3],
    "b_float": [1.5, 2.5, 3.5],
    "c_str": ["string", "asdf", "bluey"],
    "c_constrainedstr": ["string", "string", "string"],
    "d_enum": ["green", "green", "blue"],
    "e_bool": [True, True, False],
    "f_date": ["2024-06-06", "2024-06-06", "2024-06-06"],
    "g_datetime": [
        "2024-06-06T10:08:52.078770",
        "2024-06-06T10:08:52.078770",
        "2024-06-06T10:08:52.078770",
    ],
    "h_time": ["10:08:52.078959", "10:08:52.078959", "10:08:52.078959"],
    "i_duration": ["PT2H33M3S", "PT2H33M3S", "PT2H33M3S"],
    "b_calcfloat": [1.5, 5.0, 10.5],
}

ARRAY_DATA1 = {k: v * 2 for k, v in ARRAY_DATA.items() if k in DataTypesBasicFields.model_fields}

pyd_obj = DataTypesArrayTransposed(convert_dict_arrays_to_list_records(ARRAY_DATA))
pyd_obj1 = DataTypesArray(convert_dict_arrays_to_list_records(ARRAY_DATA1))
import xlsxdatagrid as xdg
fpth = pathlib.Path("tests/xl/test-many-sheets.xlsx")
from_pydantic_objects([pyd_obj, pyd_obj1], fpth)
print(fpth, fpth.is_file())
#> tests/xl/test-many-sheets.xlsx True
```

:::

```{=html}
<embed src="../xl/test-many-sheets.xlsx" width="600px" height="1000px" />
```