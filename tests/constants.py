import pathlib

FDIR = pathlib.Path(__file__).parent / "xl"
PATH_XL, PATH_XL_TRANSPOSED = FDIR / "simple.xlsx", FDIR / "simple-T.xlsx"
PATH_XL_MANY_SHEETS = FDIR / "many-sheets.xlsx"

PATH_XL_FROM_SCHEMA, PATH_XL_FROM_SCHEMA_TRANSPOSED = (
    FDIR / "from-schema.xlsx",
    FDIR / "from-schema-T.xlsx",
)
PATH_XL_FROM_API = FDIR / "from-ds-api.xlsx"
PATH_JSONSCHEMA_RAW = FDIR / "schema-1.json"
PATH_FROM_DF_WITH_CHART = FDIR / "df-x-squared.xlsx"
PATH_FROM_DF_WITH_MANY_CHARTS = FDIR / "many-charts.xlsx"
PATH_FROM_JSON = FDIR / "from-json.xlsx"
PATH_FROM_JSON_EMPTY, PATH_FROM_JSON_EMPTY_TRANSPOSED = (
    FDIR / "from-json.xlsx",
    FDIR / "from-json-T.xlsx",
)
PATH_WRITE_GRID = FDIR / "write-grid.xlsx"
