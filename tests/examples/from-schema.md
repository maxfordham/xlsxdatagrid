---
title: "report-a4-p"
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


from xlsxdatagrid.demo_schemas.dtypes import MyColor, DataTypes, DataTypesArray


t1, t2, t3 = (
    DataTypes(d_enum=MyColor.GREEN),
    DataTypes(a_int=2, b_float=2.5, c_str="asdf", d_enum=MyColor.GREEN),
    DataTypes(a_int=3, b_float=3.5, c_str="bluey", d_enum=MyColor.BLUE, e_bool=False),
)
t_array = DataTypesArray([t1, t2, t3])
import xlsxdatagrid as xdg
fpth = pathlib.Path("tests/xl/test.xlsx")
xdg.from_pydantic_object(t_array, fpth)
print(fpth, fpth.is_file())
#> tests/xl/test.xlsx True
```

:::

```{=html}
<embed src="../xl/test.xlsx" width="600px" height="1000px" />
```