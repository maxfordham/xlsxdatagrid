---
title: "many sheets"
---

::: {.callout-note collapse="true" icon=false}


## code

```py
import pathlib
from xlsxdatagrid.xlsxdatagrid import (
    convert_dict_arrays_to_list_records,
    xdg_from_pydantic_objects,
)

from xlsxdatagrid.demo_schemas.dtypes import (
    DataTypesBasicFields,
    DataTypesArray,
    DataTypesArrayTransposed,
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

ARRAY_DATA1 = {
    k: v * 2 for k, v in ARRAY_DATA.items() if k in DataTypesBasicFields.model_fields
}

pyd_obj = DataTypesArrayTransposed(convert_dict_arrays_to_list_records(ARRAY_DATA))
pyd_obj1 = DataTypesArray(convert_dict_arrays_to_list_records(ARRAY_DATA1))
fpth = pathlib.Path("tests/xl/test-many-sheets.xlsx")
fpth.parent.mkdir(parents=True, exist_ok=True)
xdg_from_pydantic_objects([pyd_obj, pyd_obj1], fpth)
print(fpth, fpth.is_file())
#> tests/xl/test-many-sheets.xlsx True
```

:::

<a href="../xl/test-many-sheets.xlsx">
  <img src="../logos/Excel-icon.png" alt="Download Excel" width="48">
</a>