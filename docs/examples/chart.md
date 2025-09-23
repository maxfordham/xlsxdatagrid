---
title: "chart"
---

::: {.callout-note collapse="true" icon=false}


## code

```py
import pathlib
from xlsxdatagrid.xlsxdatagrid import (
    wb_from_dataframe,
)
import pandas as pd


def x_squared():
    x = range(-5, 6)
    y = [_**2 for _ in x]
    return pd.DataFrame({"x": x, "y": y})


fpth = pathlib.Path("tests/xl/chart.xlsx")
fpth.parent.mkdir(parents=True, exist_ok=True)
df = x_squared()

workbook, xl_tbl, worksheet = wb_from_dataframe(df, fpth)

chart = workbook.add_chart({"type": "line"})

chart.add_series(
    {
        "name": "x squared",
        "categories": [worksheet.name] + list(xl_tbl.rng_arrays["x"]),
        "values": [worksheet.name] + list(xl_tbl.rng_arrays["y"]),
    }
)

# Add a chart title and some axis labels.
chart.set_title({"name": "x squared"})
chart.set_x_axis({"name": "x"})
chart.set_y_axis({"name": "y"})

# Set an Excel chart style.
chart.set_style(11)

# Add the chart to the chartsheet.
depth = xl_tbl.gridschema.header_depth + 4
width = len(xl_tbl.gridschema.fields) + 2
worksheet.insert_chart(depth, width, chart)
workbook.close()

print(fpth, fpth.is_file())
#> tests/xl/chart.xlsx True
```

:::

<a href="../xl/chart.xlsx">
  <img src="../logos/Excel-icon.png" alt="Download Excel" width="48">
</a>