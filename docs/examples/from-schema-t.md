---
title: "report-a4-p Transposed"
---

::: {.callout-note collapse="true" icon=false}


## code

```py
import pathlib
from xlsxdatagrid.demo_schemas.dtypes import (
    MyColor,
    DataTypes,
    DataTypesArrayTransposed,
)
import xlsxdatagrid as xdg

t1, t2, t3 = (
    DataTypes(d_enum=MyColor.GREEN),
    DataTypes(a_int=2, b_float=2.5, c_str="asdf", d_enum=MyColor.GREEN),
    DataTypes(a_int=3, b_float=3.5, c_str="bluey", d_enum=MyColor.BLUE, e_bool=False),
)
t_array = DataTypesArrayTransposed([t1, t2, t3])
fpth = pathlib.Path("tests/xl/test-t.xlsx")
fpth.parent.mkdir(parents=True, exist_ok=True)
xdg.xdg_from_pydantic_object(t_array, fpth)
print(fpth, fpth.is_file())
#> tests/xl/test-t.xlsx True
```

:::

<a href="../xl/test-t.xlsx">
  <img src="../logos/Excel-icon.png" alt="Download Excel" width="48">
</a>