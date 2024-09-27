import pathlib
import logging
from annotated_types import doc
import annotated_types
from pydantic import (
    BaseModel,
    Field,
    ConfigDict,
    computed_field,
    model_validator,
    field_validator,
    AliasChoices,
    ValidationError,
)
from typing_extensions import Annotated
from jsonref import replace_refs
from annotated_types import doc
import functools
import typing as ty
from xlsxdatagrid.colours import get_color_pallette
from pydantic_extra_types.color import Color
from typing_extensions import Annotated
from datetime import datetime, date
from xlsxwriter.utility import xl_rowcol_to_cell, datetime_to_excel_datetime

# https://specs.frictionlessdata.io//table-schema/
name_doc = """The field descriptor MUST contain a name property.
 This property SHOULD correspond to the name of field/column in the data file (if it has a name).
 As such it SHOULD be unique (though it is possible, but very bad practice, for the data file to have multiple columns with the same name). 
 name SHOULD NOT be considered case sensitive in determining uniqueness. 
 However, since it should correspond to the name of the field in the data file it may be important to preserve case."""


# NOT IN USE -------------------------------
class HeaderStyling(BaseModel):  # matches ipydatagrid
    header_background_color: ty.Optional[Color] = Field(
        None, description="background color for all non-body cells (index and columns)"
    )
    header_grid_line_color: ty.Optional[Color] = Field(
        None, description="grid line color for all non-body cells (index and columns)"
    )
    header_vertical_grid_line_color: ty.Optional[Color] = Field(
        None, description="vertical grid line color for all non-body cells"
    )
    header_horizontal_grid_line_color: ty.Optional[Color] = Field(
        None, description="horizontal grid line color for all non-body cells"
    )
    header_selection_fill_color: ty.Optional[Color] = Field(
        None,
        description="fill color of headers intersecting with selected area at column or row",
    )
    header_selection_border_color: ty.Optional[Color] = Field(
        None,
        description="border color of headers intersecting with selected area at column or row",
    )


XL_FORMAT_PROPERTIES = (
    "font_name",
    "font_size",
    "font_color",
    "bold",
    "italic",
    "underline",
    "font_strikeout",
    "font_script",
    "num_format",
    "locked",
    "hidden",
    "align",
    "valign",
    "rotation",
    "text_wrap",
    "reading_order",
    "text_justlast",
    "center_across",
    "indent",
    "shrink",
    "pattern",
    "bg_color",
    "fg_color",
    "border",
    "bottom",
    "top",
    "left",
    "right",
    "border_color",
    "bottom_color",
    "top_color",
    "left_color",
    "right_color",
)
# ^these are set at property level per column

XL_TABLE_PROPERTIES = (
    "data",
    "autofilter",
    "header_row",
    "banded_columns",
    "banded_rows",
    "first_column",
    "last_column",
    "style",
    "total_row",
    "columns",
    "name",
)
# ^these are set at schema level for the whole table

# ^ NOT IN USE -------------------------------


class Constraints(BaseModel):
    minimum: ty.Optional[ty.Union[int, float]] = None
    maximum: ty.Optional[ty.Union[int, float]] = None
    exclusiveMinimum: ty.Optional[bool] = None
    exclusiveMaximum: ty.Optional[bool] = None
    enum: ty.Optional[list[ty.Any]] = None
    maxLength: ty.Optional[int] = None
    minLength: ty.Optional[int] = None


NUMERIC_CONSTRAINTS = [
    i for i in list(Constraints.__annotations__.keys()) if i != "enum"
]
LI_CONSTRAINTS = list(Constraints.__annotations__.keys())
# https://xlsxwriter.readthedocs.io/working_with_data_validation.html#criteria

MAP_TYPES_JSON_XL = {"integer": "integer", "float": "decimal", "date": "date"}


XL_TABLE_COLUMNS_PROPERTIES = (
    "header",
    "header_format",
    "formula",
    "total_string",
    "total_function",
    "total_value",
    "format",
)


DATETIME_STR = 'yyyy-dd-mmThh:mm:ss"+00:00"'
DATE_STR = "yyyy-dd-mm"
TIME_STR = 'hh:mm:ss"+00:00"'
DURATION_STR = '"P"[h]:mm:ss'

DATETIME_FORMAT = {"num_format": DATETIME_STR}
DATE_FORMAT = {"num_format": DATE_STR}
TIME_FORMAT = {"num_format": TIME_STR}
DURATION_FORMAT = {"num_format": DURATION_STR}

PY2XL = {
    "**": "^",
    "!=": "<>",
    # other simple arithemetic operators the same
}


def py2xl_formula(formula, map_names):
    def replace(formula, di):

        for k, v in di.items():
            if k in formula:
                formula = formula.replace(k, v)
        return formula

    map_table_names = {l: f"[@[{l}]]" for l in map_names.keys()}
    formula = replace(formula, PY2XL)
    formula = replace(formula, map_names)
    formula = replace(formula, map_table_names)
    return "= " + formula


def get_numeric_constraints(di):
    return [k for k in di.keys() if k in NUMERIC_CONSTRAINTS]


def map_simple_numeric_constraints(di):
    pass


def map_constraints(di):
    li_num = get_numeric_constraints(di)
    return None


class FieldSchema(BaseModel):
    model_config = ConfigDict(extra="allow")

    name: Annotated[str, doc(name_doc)]
    type: str  # TODO: create enum
    format: str = None
    title: Annotated[str, doc("A human readable label or title for the field")] = None
    description: Annotated[
        str, doc("A description for this field e.g. 'The recipient of the funds'")
    ] = None
    example: Annotated[str, doc("An example value for the field")] = None
    constraints: ty.Optional[Constraints] = (
        None  # this is what the https://specs.frictionlessdata.io//table-schema/ but other things
    )
    formula: ty.Optional[str] = None


class FieldSchemaXl(FieldSchema):
    data_validation: dict = {}
    conditional_format: str
    cell_format: dict
    xl_formula: ty.Optional[str] = None


def get_xl_constraints(f: FieldSchema):  # TODO: write text for this
    if f.type == "boolean":
        return {
            "validate": "list",
            "source": ["TRUE", "FALSE"],
            "input_title": "must be a boolean value",
            "input_message": "TRUE or FALSE only",
        }
    if f.constraints is None:
        return None
    if f.constraints.enum is not None:
        return {
            "validate": "list",
            "source": f.constraints.enum,
            "input_title": "select from list",
            "input_message": f"must be one of: {str(f.constraints.enum)}",
        }

    if f.type == "integer" or f.type == "number" or f.type == "date":
        _type = "decimal" if f.type == "number" else f.type
        _min, _max, _exmin, _exmax = (
            f.constraints.minimum,
            f.constraints.maximum,
            f.constraints.exclusiveMinimum,
            f.constraints.exclusiveMaximum,
        )
        if _min is not None and _max is not None:
            return {
                "validate": _type,
                "criteria": "between",
                "minimum": _min,
                "maximum": _max,
                "input_title": f"select {_type}",
                "input_message": f"between {_min} and {_max}",
            }
        elif _min is not None and _exmin is not None:
            return {
                "validate": _type,
                "criteria": "<",
                "minimum": _min,
                "input_title": f"select {_type}",
                "input_message": f"exclusive minimum {_min}",
            }
        elif _min is not None and _exmin is None:
            return {
                "validate": _type,
                "criteria": "=<",
                "minimum": _min,
                "input_title": f"select {_type}",
                "input_message": f"minimum {_min}",
            }
        elif _max is not None and _exmax is not None:
            return {
                "validate": _type,
                "criteria": ">",
                "maximum": _max,
                "input_title": f"select {_type}",
                "input_message": f"exclusive maximum {_max}",
            }
        elif _max is not None and _exmax is None:
            return {
                "validate": _type,
                "criteria": ">=",
                "maximum": _max,
                "input_title": f"select {_type}",
                "input_message": f"maximum {_max}",
            }
        else:
            ValueError(
                f"no numeric match found for: min={_min}, max={_max}, type={_type}"
            )
    if f.type == "string" and f.constraints.maxLength is not None:
        return {
            "validate": "length",
            "criteria": "<",
            "value": f.constraints.maxLength,
            "input_title": f"select {f.type}",
            "input_message": f"with less than {f.constraints.maxLength} characters",
        }
    if f.type == "string" and f.constraints.minLength is not None:
        return {
            "validate": "length",
            "criteria": ">",
            "value": f.constraints.minLength,
            "input_title": f"select {f.type}",
            "input_message": f"with less than {f.constraints.minLength} characters",
        }


from typing_extensions import Self
from pydantic import HttpUrl

METADATA_FSTRING: str = (
    "#Title={title} - HeaderDepth={header_depth} - IsTransposed={is_transposed} - DateTime={now} - SchemaUrl={schema_url}"
)

import pathlib

# from urllib.parse import urlparse
# import requests


# def is_url_or_path(string):
#     parsed = urlparse(string)
#     if parsed.scheme in ("http", "https"):
#         return "url"
#     elif pathlib.Path(string).is_absolute() or any(
#         sep in string for sep in (pathlib.Path().anchor, pathlib.Path().drive)
#     ):
#         return "path"
#     else:
#         return "unknown"


class DataGridMetaData(BaseModel):
    title: str = Field(alias_choices=AliasChoices("title", "Title"))
    name: ty.Optional[str] = Field(
        None, alias_choices=AliasChoices("template_name", "name")
    )
    is_transposed: bool = False  # TODO: rename -> display_transposed
    header_depth: int = Field(1, validate_default=True)
    schema_url: ty.Optional[HttpUrl] = Field(
        None, alias_choices=AliasChoices("schema_url", "SchemaUrl")
    )
    # schema_path: ty.Optional[pathlib.Path] = Field(
    #     None, alias_choices=AliasChoices("schema_path", "SchemaPath")
    # ) TODO: could add this as an option
    metadata_fstring: str = Field(
        METADATA_FSTRING
    )  # TODO: should this be fixed... or validate that the base string is included...
    date_time: ty.Optional[datetime] = None
    datagrid_index_name: tuple = ("name",)  # RENAME: header_field_keys
    header: list[list[str]] = []

    @model_validator(mode="before")
    @classmethod
    def check_schema_url(cls, data: ty.Any) -> ty.Any:
        if isinstance(data, dict):
            if "schema_url" in data:
                if data["schema_url"] == "None":
                    data["schema_url"] = None
        return data

    @computed_field
    def now(self) -> datetime:
        return datetime.now()

    @model_validator(mode="after")
    def check_name(self) -> Self:
        # if self.schema_url is not None and self.schema_path is not None:
        #     logging.warning(
        #         "schema_url and schema_path both given, schema_url will be used to retrieve schema"
        #     )
        if self.name is None:
            self.name = self.title.replace(" ", "")
        return self


class DataGridSchema(DataGridMetaData):
    model_config = ConfigDict(extra="allow")

    header_background_color: ty.Optional[Color] = None
    base_row_size: int = 20
    base_column_size: int = 64
    base_row_header_size: int = 64
    base_column_header_size: int = 20
    column_widths: dict[str, float] = {}
    fields: list[FieldSchema]

    @model_validator(mode="after")
    def get_header_depth(self) -> "DataGridSchema":
        self.header_depth = len(self.datagrid_index_name)
        self.header = [
            [getattr(f, nm) for f in self.fields] for nm in self.datagrid_index_name
        ]
        return self

    @computed_field
    def map_name_header(self) -> dict[str, ty.Union[str, list[str]]]:

        if self.datagrid_index_name == ("name",):
            return None
        elif len(self.datagrid_index_name) == 1:
            return {
                f.name: getattr(f, self.datagrid_index_name[0]) for f in self.fields
            }
        elif len(self.datagrid_index_name) > 1:
            return {
                f.name: [getattr(f, nm) for nm in self.datagrid_index_name]
                for f in self.fields
            }
        else:
            raise ValueError("incorrect type")

    @computed_field
    def field_names(self) -> list:
        return [f.name for f in self.fields]


def convert_date_to_excel_ordinal(d: date, offset: int = 693594):
    # the offset date value for the date of 1900-01-00 = 693594
    return d.toordinal() - offset


from pydantic import RootModel
from datetime import time, timedelta


def get_datetime(d):
    return RootModel[datetime](d).model_dump()


def get_time(d):
    return RootModel[time](d).model_dump()


def get_date(d):
    return RootModel[date](d).model_dump()


def get_duration(d):
    return RootModel[timedelta](d).model_dump()


class XlTableWriter(BaseModel):
    gridschema: DataGridSchema
    data: dict[str, list]
    is_table: bool = True
    header_sections: list = ["section", "category"]  # used to colour code only
    xy: tuple[int, int] = 0, 0  # row, col
    xy_arrays: dict[str, tuple[int, int]] = {"a": (0, 0)}
    format_arrays: dict[str, str] = Field({})  # col-name: format
    comment_arrays: dict[str, str] = Field({})  # col-name: comment
    rng_arrays: dict[str, tuple[int, int, int, int]] = {"a": (0, 0, 0, 0)}
    xy_headers: list[tuple[int, int]] = [(0, 0)]
    rng_headers: list[tuple[int, int, int, int]] = [(0, 0, 0, 0)]
    format_headers: list = [None]
    tbl_range: tuple[int, int, int, int] = (0, 0, 0, 0)
    tbl_headers: ty.Optional[list[dict]] = None
    validation_arrays: ty.Optional[dict[str, dict]] = None
    formula_arrays: dict[str, str] = {}
    formats: dict[str, dict] = {
        "datetime": DATETIME_FORMAT,
        "date": DATE_FORMAT,
        "time": TIME_FORMAT,
        "duration": DURATION_FORMAT,
    }
    conditional_formats: list[dict] = []
    hide_gridlines: Annotated[int, annotated_types.Interval(ge=0, le=2)] = (
        2  # hidden by default
    )
    metadata: str = ""
    # length: int = 0

    @model_validator(mode="after")
    def build(self) -> "XlTableWriter":

        self.metadata = self.gridschema.metadata_fstring.format(
            **self.gridschema.model_dump()
        )
        x, y = self.xy  # start coordinates
        is_t = self.gridschema.is_transposed
        ix_nm = self.gridschema.datagrid_index_name  # column headings
        hd = self.gridschema.header_depth  # header depth
        fd_nns = self.gridschema.field_names  # field names
        length = (
            len(self.data[fd_nns[0]]) - 1 if len(self.data) > 0 else 0
        )  # length of data arrays
        self.format_headers = hd * [None]

        # ensure data and key col names in same order
        if self.gridschema.field_names != list(self.data.keys()):
            self.data = {
                l: (lambda l, data: data[l] if l in data.keys() else [None] * length)(
                    l, self.data
                )
                for l in self.gridschema.field_names
            }
        assert self.gridschema.field_names == list(self.data.keys())
        # TODO: allow option of only outputting fields which have data associated with them

        if is_t:
            x += 1
        else:
            y += 1
        # ^ leave room for the header names

        x += 1
        # ^ leave room for the metadata

        if not is_t:  # build a normal xl table
            self.xy_arrays = {
                f: (x + hd, y + n) for n, f in enumerate(fd_nns)
            }  # +1 as below header row
            self.rng_arrays = {
                k: (v[0], v[1], v[0] + length, v[1]) for k, v in self.xy_arrays.items()
            }
            beg, end = self.rng_arrays[fd_nns[0]][0:2], self.rng_arrays[fd_nns[-1]][2:4]
            beg = (beg[0] - 1, beg[1])  # inc. header
            self.tbl_range = (*beg, *end)
            self.xy_headers = [(x + n, y) for n in range(0, hd)]
            self.rng_headers = [
                (v[0], v[1], v[0], v[1] + len(self.xy_arrays)) for v in self.xy_headers
            ]  # (x1, y1, x2, y2)

            self.tbl_headers = self.gridschema.header[-1]

            # formulas currently only posible with normal tables
            map_names = {
                k: v
                for k, v in zip(set(self.gridschema.field_names), set(self.tbl_headers))
            }
            self.formula_arrays = {
                f.name: py2xl_formula(f.formula, map_names)
                for f in self.gridschema.fields
                if f.formula is not None
            } | {
                f.name: getattr(f, "xl_formula")
                for f in self.gridschema.fields
                if hasattr(f, "xl_formula") and getattr(f, "xl_formula") is not None
            }  # formula override (normally empty)

        else:  # build a transposed xl table
            self.xy_arrays = {
                f: (x + n, y + hd) for n, f in enumerate(fd_nns)
            }  # +1 as below header row
            self.rng_arrays = {
                k: (v[0], v[1], v[0], v[1] + length) for k, v in self.xy_arrays.items()
            }
            beg, end = self.rng_arrays[fd_nns[0]][0:2], self.rng_arrays[fd_nns[-1]][2:4]
            beg = (beg[0] - 1, beg[1] - hd)  # inc. header
            self.tbl_range = (*beg, *end)
            self.xy_headers = [(x, y + n) for n in range(0, hd)]
            self.rng_headers = [
                (v[0], v[1], v[0] + len(self.xy_arrays), v[1]) for v in self.xy_headers
            ]  # (x1, y1, x2, y2)
            self.tbl_headers = None

        palettes_in_use = []
        self.header_sections = [h for h in self.header_sections if h in ix_nm]
        di_section_colors = {}
        for h in self.header_sections:
            sections = list(set([getattr(f, h) for f in self.gridschema.fields]))
            colors = get_color_pallette(len(sections), palettes_in_use)
            di_section_colors = di_section_colors | {
                h: [(s, c) for s, c in zip(sections, colors)]
            }

        for v in di_section_colors.values():
            self.formats = self.formats | {f"{l[1]}": {"bg_color": l[1]} for l in v}

        for k, v in di_section_colors.items():
            r1, c1, r2, c2 = self.rng_headers[ix_nm.index(k)]
            for _ in v:
                self.conditional_formats = self.conditional_formats + [
                    [
                        r1,
                        c1,
                        r2,
                        c2,
                        {
                            "type": "cell",
                            "criteria": "equal to",
                            "value": '"{0}"'.format(_[0]),
                            "format": _[1],
                        },
                    ]
                ]

        self.validation_arrays = {
            f.name: get_xl_constraints(f) for f in self.gridschema.fields
        }
        dates = [f.name for f in self.gridschema.fields if f.format == "date"]
        date_times = [f.name for f in self.gridschema.fields if f.format == "date-time"]
        durations = [f.name for f in self.gridschema.fields if f.format == "duration"]
        times = [f.name for f in self.gridschema.fields if f.format == "time"]

        for d in date_times:
            self.data[d] = [
                datetime_to_excel_datetime(get_datetime(v), False, True)
                for v in self.data[d]
            ]
            self.format_arrays[d] = "datetime"
        for d in dates:
            self.data[d] = [
                datetime_to_excel_datetime(get_datetime(v), False, True)
                for v in self.data[d]
            ]
            self.format_arrays[d] = "date"
        for d in times:
            self.data[d] = [
                datetime_to_excel_datetime(get_time(v), False, True)
                for v in self.data[d]
            ]
            self.format_arrays[d] = "time"
        for d in durations:
            self.data[d] = [
                datetime_to_excel_datetime(get_duration(v), False, True)
                for v in self.data[d]
            ]
            self.format_arrays[d] = "duration"

        return self


def flatten_allOf(di: dict) -> dict:
    if "allOf" in di.keys():
        for _ in di["allOf"]:
            di = {**di, **_}
        return {k: v for k, v in di.items() if k != "allOf"}
    else:
        return di


def flatten_anyOf(fields: list) -> list:
    for field in fields:
        if "anyOf" in field.keys():
            types = list(set([f["type"] for f in field["anyOf"]]))
            if len(types) == 2:
                field["type"] = field["anyOf"][0]["type"]
            if len(types) > 2:
                logging.warning(
                    f"more than 2 types allowed ({types})... for {field['name']}"
                )
            field.pop("anyOf")
    return fields


def convert_records_to_datagrid_schema(schema: dict):
    li_constraints = list(Constraints.__annotations__.keys())
    gridschema = replace_refs(schema)
    gridschema["fields"] = [
        flatten_allOf(v) | {"name": k}
        for k, v in gridschema["items"]["properties"].items()
    ]
    gridschema["fields"] = flatten_anyOf(gridschema["fields"])
    # move constraints
    for n in range(0, len(gridschema["fields"])):
        for k in list(gridschema["fields"][n].keys()):
            if k in li_constraints:
                if "constraints" not in list(gridschema["fields"][n].keys()):
                    gridschema["fields"][n]["constraints"] = {}
                gridschema["fields"][n]["constraints"] = gridschema["fields"][n][
                    "constraints"
                ] | {k: gridschema["fields"][n][k]}
                gridschema["fields"][n].pop(k)

    gridschema["format"] = "dataframe"
    gridschema = {k: v for k, v in gridschema.items() if k not in ["$defs", "items"]}
    return gridschema


from dirty_equals import IsInstance  # , IsPartialDict
import inspect


def coerce_schema(
    schema: ty.Union[dict, DataGridSchema, BaseModel, ty.Type[BaseModel]]
) -> DataGridSchema:
    if schema == IsInstance(DataGridSchema, only_direct_instance=True):
        return schema  # its already a `DataGridSchema`
    elif isinstance(schema, BaseModel):
        return DataGridSchema(
            **convert_records_to_datagrid_schema(schema.model_json_schema())
        )  # its a pydantic object
    elif inspect.isclass(schema) and issubclass(schema, BaseModel):
        return DataGridSchema(
            **convert_records_to_datagrid_schema(schema.model_json_schema())
        )  # its a pydantic model
    elif (
        isinstance(schema, dict)
        and "fields" in schema.keys()
        and isinstance(schema["fields"], list)
    ):
        return DataGridSchema(**schema)  # its a frictionless schema
    elif (
        isinstance(schema, dict)
        and schema["type"] == "array"
        and "items" in schema.keys()
    ):
        return DataGridSchema(
            **convert_records_to_datagrid_schema(schema)
        )  # its a json schema as array of object records
    else:
        raise AttributeError(
            "schema must be a `DataGridSchema`,",
            "a pydantic array of objects jsonschema",
            f"or a frictionless datagrid schema, not: {schema}",
        )


def convert_list_records_to_dict_arrays(data: list[dict]) -> dict[str, list]:
    if len(data) == 0:
        return {}
    return {k: [dic[k] for dic in data] for k in data[0]}


def convert_dict_arrays_to_list_records(
    data: dict[str, list]
) -> list[dict]:  # NOT IN USE
    if len(data) == 0:
        return []
    return [dict(zip(data.keys(), values)) for values in zip(*data.values())]


import numpy as np


def write_table(workbook, xl_tbl: XlTableWriter):
    name = xl_tbl.gridschema.title
    worksheet = workbook.add_worksheet(name=name)
    is_t = xl_tbl.gridschema.is_transposed
    headers = xl_tbl.gridschema.datagrid_index_name
    ix_nm = xl_tbl.gridschema.datagrid_index_name
    hd = len(ix_nm)  # header depth
    label_index = xl_tbl.xy[0] if is_t else xl_tbl.xy[1]
    write_array = worksheet.write_row if is_t else worksheet.write_column
    write_header = worksheet.write_row if not is_t else worksheet.write_column
    header_index = xl_tbl.xy_headers[-1][1] if is_t else xl_tbl.xy_headers[-1][0]
    set_header_border = (
        functools.partial(worksheet.set_row, header_index)
        if not is_t
        else functools.partial(worksheet.set_column, header_index, header_index)
    )
    freeze_panes = (0, header_index + 1) if is_t else (header_index + 1, 0)
    header_border = {"right": 5} if is_t else {"bottom": 5}
    formats = {k: workbook.add_format(v) for k, v in xl_tbl.formats.items()}
    format_arrays = {k: formats[v] for k, v in xl_tbl.format_arrays.items()}
    conditional_formats = []

    for c in xl_tbl.conditional_formats:
        di = c[4]
        f = di["format"]
        di = di | {"format": formats[f]}
        conditional_formats += [c[0:4] + [di]]
    _format = dict(bold=True) | header_border | {"locked": True}
    if is_t:
        _format = _format | {"align": "right"}

    header_cell_format = workbook.add_format(_format)
    calc_cell_format = workbook.add_format(dict(font_color="blue", italic=True))
    header_label_cell_format = workbook.add_format(
        dict(font_color="#999999", italic=True)
    )
    header_white_cell_format = workbook.add_format(dict(font_color="#FFFFFF"))

    # special formats for arrays (mostly used for datetime)
    # for k, v in xl_tbl.format_arrays.items():

    # make table --------------------------
    length = len(list(xl_tbl.data.values())[0]) + len(ix_nm)
    get_name = lambda n, hd: f"Column{n}" if n >= hd else ix_nm[n]
    column_labels = [get_name(n, hd) for n in range(0, length)]

    formula_columns = []
    if is_t:  # transposed - with headers
        columns = [{"header": c} for c in column_labels]

        options = dict(
            style="Table Style Light 1",
            header_row=True,
            first_column=False,
            columns=columns,
        )

    else:  # not transposed - with headers
        columns = {
            f.name: {"header": h}
            | {
                k: v
                for k, v in f.model_dump(exclude_none=True).items()
                if k in XL_TABLE_COLUMNS_PROPERTIES[0:6]
            }
            for h, f in zip(xl_tbl.tbl_headers, xl_tbl.gridschema.fields)
        }
        for k, v in xl_tbl.formula_arrays.items():
            if "formula" in columns[k].keys():
                formula_columns += [k]
                columns[k]["formula"] = xl_tbl.formula_arrays[k]
                columns[k]["format"] = calc_cell_format

        for k, v in xl_tbl.format_arrays.items():
            columns[k]["format"] = formats[v]
        # ^ TODO: formatting dates and datetime as numeric with excel string formatting
        options = dict(
            style="Table Style Light 1",
            header_row=True,
            first_column=False,
            columns=list(columns.values()),
        )

    options = options  # | {"name": name}  # TODO: <- table name needs to not inc. spaces etc... update
    # ^ a known table name will be important if / when we want to do lookups between tables...

    worksheet.add_table(*xl_tbl.tbl_range, options)
    # NOTE: if you write a table to excel with a header - the table range includes the header.

    # -------------------------------------
    # write arrays
    for k, v in xl_tbl.xy_arrays.items():
        if k not in formula_columns:
            # li = list(np.array(xl_tbl.data[k]))
            li = xl_tbl.data[k]

            if k in format_arrays:
                write_array(*v, li, format_arrays[k])
            else:
                write_array(*v, li)

    if len(ix_nm) > 1:
        if xl_tbl.gridschema.is_transposed:
            rngs, headers = xl_tbl.xy_headers, xl_tbl.gridschema.header
        else:
            rngs, headers = (
                xl_tbl.xy_headers[:-1],
                xl_tbl.gridschema.header[:-1],
            )  # table headers are inserted into when adding table
        {
            write_header(*start_cell, data, header_cell_format)
            for start_cell, data in zip(rngs, headers)
        }

    if xl_tbl.validation_arrays is not None:
        for k, v in xl_tbl.validation_arrays.items():
            if v is not None:
                rng = xl_tbl.rng_arrays[k]
                worksheet.data_validation(*rng, options=v)

    for c in conditional_formats:
        worksheet.conditional_format(*c)

    # apply header border
    cell_format = workbook.add_format(dict(valign="top") | header_border)
    set_header_border(None, cell_format)

    # write column labels
    x, y = xl_tbl.xy
    x += 1  # for metadata row
    write_array(*(x, y), column_labels[0:hd], header_label_cell_format)
    if is_t:
        # set empty table headers to be white
        y += hd
        write_array(
            *(x, y),
            column_labels[hd : len(column_labels)],
            header_white_cell_format,
        )

    # write array comments
    for k, v in xl_tbl.comment_arrays.items():
        cell = xl_tbl.xy_arrays[k]
        worksheet.write_comment(xl_rowcol_to_cell(*cell), *v)

    worksheet.freeze_panes(*freeze_panes)
    worksheet.autofit()
    worksheet.hide_gridlines(xl_tbl.hide_gridlines)
    # write metadata
    worksheet.write(*xl_tbl.xy, xl_tbl.metadata, header_label_cell_format)
    # worksheet.add_table(*xl_tbl.tbl_range, options)
    return worksheet


import xlsxwriter as xw
import pandas as pd
from pandas.io.json import build_table_schema


def write_sheet(
    workbook: xw.Workbook,
    data: list[dict],
    gridschema: ty.Union[dict, DataGridSchema, BaseModel, ty.Type[BaseModel]],
) -> tuple[xw.worksheet.Worksheet, XlTableWriter]:
    gridschema = coerce_schema(gridschema)
    data = convert_list_records_to_dict_arrays(data)
    xl_tbl = XlTableWriter(data=data, gridschema=gridschema)
    return write_table(workbook, xl_tbl), xl_tbl


def write_sheets(
    workbook: xw.Workbook,
    datas: list[list[dict]],
    gridschemas: list[ty.Union[dict, DataGridSchema, BaseModel, ty.Type[BaseModel]]],
) -> tuple[list[xw.worksheet.Worksheet], list[XlTableWriter]]:
    return zip(
        *[
            write_sheet(workbook, data, schema)
            for data, schema in zip(datas, gridschemas)
        ]
    )


def wb_from_json(
    data: list[dict], schema: dict, fpth: ty.Optional[pathlib.Path] = None
) -> tuple[xw.Workbook, XlTableWriter, xw.worksheet.Worksheet]:
    if fpth is None:
        fpth = pathlib.Path(schema.get("title") + ".xlsx")
    workbook = xw.Workbook(str(fpth))
    worksheet, xl_tbl = write_sheet(workbook, data=data, gridschema=schema)
    return workbook, xl_tbl, worksheet


def wb_from_jsons(
    datas: list[list[dict]],
    schemas: list[ty.Union[dict, DataGridSchema, BaseModel]],
    fpth: pathlib.Path,
) -> tuple[xw.Workbook, XlTableWriter, xw.worksheet.Worksheet]:
    workbook = xw.Workbook(str(fpth))
    # schemas = coerce_lengths(len(datas), schemas)
    worksheets, xl_tbls = write_sheets(workbook, datas, schemas)
    return workbook, worksheets, xl_tbls


def from_json(
    data: dict,
    schema: ty.Union[dict, DataGridSchema, BaseModel],
    fpth: ty.Optional[pathlib.Path] = None,
    is_transposed: ty.Optional[bool] = None,
):
    gridschema = coerce_schema(schema)
    if is_transposed is not None:
        gridschema.is_transposed = is_transposed
    if fpth is None:
        fpth = pathlib.Path(gridschema.title + ".xlsx")
    workbook, xl_tbl, worksheet = wb_from_json(data, gridschema, fpth=fpth)
    workbook.close()
    return fpth


def from_jsons(
    datas: list[list[dict]],
    gridschemas: list[ty.Union[dict, DataGridSchema, BaseModel]],
    fpth: pathlib.Path = None,
):
    if fpth is None:
        fpth = pathlib.Path("output" + ".xlsx")
    workbook, worksheets, xl_tbls = wb_from_jsons(datas, gridschemas, fpth)
    workbook.close()
    return fpth


from frictionless import Resource
from frictionless.resources import TableResource


def wb_from_dataframe(
    dataframe: pd.DataFrame, fpth: pathlib.Path, schema: ty.Optional[dict] = None
) -> tuple[xw.Workbook, XlTableWriter, xw.worksheet.Worksheet]:

    schema = (lambda s, df: build_table_schema(df) if s is None else s)(
        schema, dataframe
    )
    if "title" not in schema.keys():
        schema["title"] = fpth.stem
    data = dataframe.reset_index().to_dict(orient="records")
    return wb_from_json(data, schema, fpth)


def coerce_lengths(length: int, *args: ty.Union[ty.Any, list]):
    return [
        (lambda a: length * [a] if not isinstance(a, list) else a)(a) for a in args
    ]  # coerce fixed attributes into list of equal length to lead


def ensure_titles_in_schemas(schemas):
    return [
        (lambda n, s: s | {"title": f"Sheet{n}"} if "title" not in s else s)(n + 1, s)
        for n, s in enumerate(schemas)
    ]


def wb_from_dataframes(
    dataframes: list[pd.DataFrame],
    fpth: pathlib.Path,
    schemas: ty.Optional[ty.Union[dict, list[dict]]] = None,
    titles: list[str] = None,
) -> tuple[xw.Workbook, list[XlTableWriter], list[xw.worksheet.Worksheet]]:
    # resource = Resource(dataframe)
    # data = resource.read_rows()
    # TODO: use frictionless to get data and schema ?
    #       ^ https://github.com/frictionlessdata/frictionless-py/issues/1678

    (schemas,) = coerce_lengths(len(dataframes), schemas)
    schemas = [
        (lambda s, df: build_table_schema(df) if s is None else s)(schema, dataframe)
        for schema, dataframe in zip(schemas, dataframes)
    ]
    if titles is not None:
        schemas = [s | {"title": t} for s, t in zip(schemas, titles)]
    else:
        schemas = ensure_titles_in_schemas(schemas)

    datas = [
        dataframe.reset_index().fillna("").to_dict(orient="records")
        for dataframe in dataframes
    ]
    workbook = xw.Workbook(str(fpth))
    worksheets, xl_tbls = write_sheets(workbook, datas, schemas)

    return workbook, worksheets, xl_tbls


def from_dataframe(
    dataframe: pd.DataFrame, fpth: pathlib.Path, schema=None
) -> pathlib.Path:
    workbook, xl_tbl, worksheet = wb_from_dataframe(dataframe, fpth, schema)
    workbook.close()
    return fpth


def from_dataframes(
    dataframes: list[pd.DataFrame],
    fpth: pathlib.Path,
    schemas: ty.Optional[ty.Union[dict, list[dict]]] = None,
    titles: list[str] = None,
) -> pathlib.Path:
    workbook, xl_tbls, worksheets = wb_from_dataframes(
        dataframes, fpth, schemas, titles
    )
    workbook.close()
    return fpth


def get_data_and_dgschema(
    pyd_obj: ty.Type[BaseModel],
) -> tuple[dict[str, list], dict]:
    schema = pyd_obj.model_json_schema(mode="serialization")
    data = pyd_obj.model_dump(mode="json")
    return data, schema


def from_pydantic_object(
    pydantic_object: ty.Type[BaseModel], fpth: pathlib.Path = None
) -> pathlib.Path:
    data, schema = get_data_and_dgschema(pydantic_object)
    return from_json(data, schema, fpth=fpth)


def from_pydantic_objects(
    pydantic_objects: list[ty.Type[BaseModel]], fpth: pathlib.Path
) -> pathlib.Path:
    datas, schemas = zip(
        *[
            get_data_and_dgschema(pydantic_object)
            for pydantic_object in pydantic_objects
        ]
    )
    return from_jsons(datas, schemas, fpth=fpth)
