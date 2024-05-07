from annotated_types import doc
import annotated_types
from pydantic import (
    BaseModel,
    Field,
    ConfigDict,
    computed_field,
    model_validator,
    field_validator,
    ValidationInfo,
)
from typing_extensions import Annotated
from jsonref import replace_refs
from annotated_types import doc
import functools
import typing as ty
from xlsxdatagrid.colours import get_color_pallette
from pydantic_extra_types.color import Color
from typing_extensions import Annotated
from datetime import datetime

# https://specs.frictionlessdata.io//table-schema/
name_doc = """The field descriptor MUST contain a name property.
 This property SHOULD correspond to the name of field/column in the data file (if it has a name).
 As such it SHOULD be unique (though it is possible, but very bad practice, for the data file to have multiple columns with the same name). 
 name SHOULD NOT be considered case sensitive in determining uniqueness. 
 However, since it should correspond to the name of the field in the data file it may be important to preserve case."""


class Constraints(BaseModel):
    minimum: ty.Optional[ty.Union[int, float]] = None
    maximum: ty.Optional[ty.Union[int, float]] = None
    exclusiveMinimum: ty.Optional[bool] = None
    exclusiveMaximum: ty.Optional[bool] = None
    enum: ty.Optional[list[ty.Any]] = None
    maxLength: ty.Optional[int] = None
    minLength: ty.Optional[int] = None


NUMERIC_CONSTRAINTS = [
    l for l in list(Constraints.__annotations__.keys()) if l != "enum"
]
LI_CONSTRAINTS = list(Constraints.__annotations__.keys())
# https://xlsxwriter.readthedocs.io/working_with_data_validation.html#criteria

MAP_TYPES_JSON_XL = {"integer": "integer", "float": "decimal", "date": "date"}

PY2XL = {
    "**": "^",
    "!=": "<>",
    # other simple arithemetic operators the same
}

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

XL_TABLE_COLUMNS_PROPERTIES = (
    "header",
    "header_format",
    "formula",
    "total_string",
    "total_function",
    "total_value",
    "format",
)

# "between",
# "not between"
# ==
# != # not equal to
# >  # greater than
# <  # less than
# >=  # greater than or equal to
# <=  # less than or equal to


# MAP_DATAVALIDATION = {
#     "minimum":
# }


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
    type: str
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


def get_xl_constraints(f: FieldSchema):
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


class FieldSchemaXl(FieldSchema):
    data_validation: dict = {}
    conditional_format: str
    cell_format: dict
    formula: str


# NOT IN USE
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


METADATA_FSTRING: str = (
    "#Schema={title} - HeaderDepth={header_depth} - IsTransposed={is_transposed} - DateTime={now}"
)


class DataGridMetaData(BaseModel):
    template_name: str = ""
    is_transposed: bool = False  # TODO: rename -> display_transposed
    header_depth: int = Field(1, validate_default=True)
    metadata_fstring: ty.Literal[METADATA_FSTRING] = METADATA_FSTRING
    # date_time:

    @computed_field
    def now(self) -> datetime:
        return datetime.now()


class DataGridSchema(DataGridMetaData):
    model_config = ConfigDict(extra="allow")

    title: str  # no spaces
    header_background_color: ty.Optional[Color] = None
    base_row_size: int = 20
    base_column_size: int = 64
    base_row_header_size: int = 64
    base_column_header_size: int = 20
    datagrid_index_name: tuple = ("name",)  # RENAME: header_field_keys
    column_widths: dict[str, float] = {}
    fields: list[FieldSchema]

    @model_validator(mode="after")
    def get_header_depth(self) -> "DataGridSchema":
        self.header_depth = len(self.datagrid_index_name)
        return self

    @computed_field
    def header(self) -> list[ty.Union[str, list[str]]]:
        return [
            [getattr(f, din) for f in self.fields] for din in self.datagrid_index_name
        ]

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
                f.name: [getattr(f, din) for din in self.datagrid_index_name]
                for f in self.fields
            }
        else:
            raise ValueError("incorrect type")

    @computed_field
    def field_names(self) -> list:
        return [f.name for f in self.fields]


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


class XlTableWriter(BaseModel):
    gridschema: DataGridSchema
    data: dict[str, list]
    is_table: bool = True
    header_sections: list = ["section", "category"]  # used to colour code only
    xy: tuple[int, int] = 0, 0  # row, col
    xy_arrays: dict[str, tuple[int, int]] = {"a": (0, 0)}
    rng_arrays: dict[str, tuple[int, int, int, int]] = {"a": (0, 0, 0, 0)}
    xy_headers: list[tuple[int, int]] = [
        (0, 0)
    ]  # ty.Optional[dict[str, tuple[int, int]]] = None
    rng_headers: list[tuple[int, int, int, int]] = [(0, 0, 0, 0)]
    format_headers: list = [None]
    tbl_range: tuple[int, int, int, int] = (0, 0, 0, 0)
    tbl_headers: ty.Optional[list[dict]] = None
    validation_arrays: ty.Optional[dict[str, dict]] = None
    formula_arrays: dict[str, str] = {}
    formats: dict[str, dict] = {}
    conditional_formats: list[dict] = []
    hide_gridlines: Annotated[int, annotated_types.Interval(ge=0, le=2)] = (
        2  # hidden by default
    )
    metadata: str = ""

    @model_validator(mode="after")
    def build(self) -> "XlTableWriter":
        self.metadata = self.gridschema.metadata_fstring.format(
            **self.gridschema.model_dump()
        )
        x, y = self.xy  # start coordinates
        is_t = self.gridschema.is_transposed
        ix_nm = self.gridschema.datagrid_index_name  # column headings
        hd = self.gridschema.header_depth  # header depth
        fd_nns = list(self.data.keys())  # field names
        length = len(self.data[fd_nns[0]]) - 1  # length of data arrays
        self.format_headers = hd * [None]

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
                if hasattr(f, "xl_formula")
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
        return self


def flatten_allOf(di: dict) -> dict:
    if "allOf" in di.keys():
        for _ in di["allOf"]:
            di = {**di, **_}
        return {k: v for k, v in di.items() if k != "allOf"}
    else:
        return di


def get_data_and_schema(pyd_obj: ty.Type[BaseModel]):
    li_constraints = list(Constraints.__annotations__.keys())
    gridschema = replace_refs(pyd_obj.model_json_schema(mode="serialization"))
    gridschema["fields"] = [
        flatten_allOf(v) | {"name": k}
        for k, v in gridschema["items"]["properties"].items()
    ]
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
    data = pyd_obj.model_dump(mode="json")
    data = {k: [dic[k] for dic in data] for k in data[0]}
    return data, DataGridSchema(**gridschema)


def write_table(workbook, xl_tbl: XlTableWriter):
    name = xl_tbl.gridschema.title
    worksheet = workbook.add_worksheet(name=name)
    is_t = xl_tbl.gridschema.is_transposed
    headers = xl_tbl.gridschema.datagrid_index_name
    hd = len(headers)  # header depth
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

    # make table --------------------------

    get_name = lambda n, hd: f"Column{n}" if n >= hd else headers[n]
    column_labels = [
        get_name(n, hd) for n in range(0, len(xl_tbl.gridschema.field_names))
    ]

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
        options = dict(
            style="Table Style Light 1",
            header_row=True,
            first_column=False,
            columns=list(columns.values()),
        )

    options = options | {"name": name}
    worksheet.add_table(*xl_tbl.tbl_range, options)
    # NOTE: if you write a table to excel with a header - the table range includes the header.

    # -------------------------------------
    for k, v in xl_tbl.xy_arrays.items():
        if k not in formula_columns:
            write_array(*v, xl_tbl.data[k])

    if len(xl_tbl.gridschema.datagrid_index_name) > 1:
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
            column_labels[hd : len(column_labels) - (hd + 1)],
            header_white_cell_format,
        )
    worksheet.freeze_panes(*freeze_panes)
    worksheet.autofit()
    worksheet.hide_gridlines(xl_tbl.hide_gridlines)
    # write metadata
    worksheet.write(*xl_tbl.xy, xl_tbl.metadata, header_label_cell_format)
    return None
