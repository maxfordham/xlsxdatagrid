# std libs
import importlib.util
import sys
import json
import typing as ty
from pathlib import Path
from datetime import timezone
from tempfile import TemporaryDirectory

# 3rd party
from python_calamine import CalamineWorkbook, CalamineSheet
from datamodel_code_generator import InputFileType, generate, DataModelType
from pydantic import BaseModel, create_model, AwareDatetime
from stringcase import snakecase

# local
from xlsxdatagrid.xlsxdatagrid import DataGridMetaData


def fix_enum_hack(output):
    # HACK: delete once issue resolved: https://github.com/koxudaxi/datamodel-code-generator/issues/2091
    def fix_enums(s):
        if "(Enum):" in s:
            li_enums.append(s.replace("class ", "").replace("(Enum):", ""))
            s = s.replace("(Enum):", "Enum(Enum):")
        return s

    def fix_enum_defs(s):
        for k, v in di_replace.items():
            if k in s:
                return s.replace(k, v)
        return s

    li_enums = []

    li = output.read_text().split("\n")
    li = [fix_enums(s) for s in li]
    di_replace = {}
    for x in li_enums:
        di_replace[f": {x}"] = f": {x}Enum"
        di_replace[f": Optional[{x}]"] = f": Optional[{x}Enum]"
    if len(di_replace) > 0:
        li = [fix_enum_defs(s) for s in li]

    output.write_text("\n".join(li))


def pydantic_model_from_json_schema(json_schema: str) -> ty.Type[BaseModel]:
    load = json_schema["title"].replace(" ", "") if "title" in json_schema else "Model"
    # TODO: refactor this when title vs name vs code has been sorted out...

    with TemporaryDirectory() as temporary_directory_name:
        temporary_directory = Path(temporary_directory_name)
        file_path = "model.py"
        module_name = file_path.split(".")[0]
        output = Path(temporary_directory / file_path)
        generate(
            json.dumps(json_schema),
            input_file_type=InputFileType.JsonSchema,
            input_filename="example.json",
            output=output,
            output_model_type=DataModelType.PydanticV2BaseModel,
            capitalise_enum_members=True,
        )
        fix_enum_hack(
            output
        )  # TODO: remove this once resolved: https://github.com/koxudaxi/datamodel-code-generator/issues/2091
        spec = importlib.util.spec_from_file_location(module_name, output)
        module = importlib.util.module_from_spec(spec)
        sys.modules[module_name] = module
        spec.loader.exec_module(module)
    return getattr(module, load)


def read_metadata(s: str) -> DataGridMetaData:
    s = s.replace("#", "")
    li = [l.split("=") for l in s.split(" - ")]
    di = {snakecase(l[0]): l[1] for l in li}
    return DataGridMetaData(**di)


def process_data(
    data: list[dict], metadata: DataGridMetaData, *, empty_string_to_none=True
) -> tuple[list[dict], DataGridMetaData]:
    hd = metadata.header_depth
    is_t = metadata.is_transposed
    if is_t:
        data = list(map(list, zip(*data)))

    # else:
    header_names = [d[0] for d in data[0:hd]]
    data = [d[1:] for d in data]
    if empty_string_to_none:
        data = [[(lambda _: None if _ == "" else _)(_) for _ in d] for d in data]

    headers = {h: data[n] for n, h in enumerate(header_names)}
    header = headers[header_names[-1]]
    metadata.datagrid_index_name = list(headers.keys())
    metadata.header = list(headers.values())

    data = data[len(header_names) :]
    data = [dict(zip(header, d)) for d in data]

    return data, metadata


def read_data(data) -> tuple[list[dict], DataGridMetaData]:
    if data[0][0][0] != "#":
        raise ValueError(
            "the first row must be a metadata string beginning with the char '#'"
        )
    metadata = read_metadata(data[0][0])
    data = data[1:]
    return process_data(data, metadata)


def get_jsonschema(metadata: DataGridMetaData) -> dict:
    pass


def make_datetime_tz_aware(data, pydantic_model):

    def field_is_aware_datetime(field):
        if hasattr(field.annotation, "__args__"):
            if AwareDatetime in field.annotation.__args__:
                return True
            else:
                return False
        elif isinstance(field.annotation, AwareDatetime):
            return True
        else:
            return False

    row_model = pydantic_model.model_fields["root"].annotation.__args__[0]
    keys = [k for k, v in row_model.model_fields.items() if field_is_aware_datetime(v)]
    if len(keys) > 0:
        return [d | {k: d[k].replace(tzinfo=timezone.utc) for k in keys} for d in data]
    else:
        return data


# def parse_timedelta(data, pydantic_model):

#     def field_timedelta(field):
#         if hasattr(field.annotation, "__args__"):
#             if timedelta in field.annotation.__args__:
#                 return True
#             else:
#                 return False
#         elif isinstance(field.annotation, timedelta):
#             return True
#         else:
#             return False

#     row_model = pydantic_model.model_fields["root"].annotation.__args__[0]
#     timedeltas = {k: v for k, v in row_model.model_fields.items() if field_timedelta(v)}
#     if len(timedeltas) > 0:
#         keys = list(timedeltas.keys())
#         return [d | {k: timedelta(d[k]) for k in keys} for d in data]
#     else:
#         return data
from jsonref import replace_refs
from xlsxdatagrid.xlsxdatagrid import get_duration
from datetime import timedelta
import requests


def parse_timedelta(data, json_schema):

    pr = replace_refs(json_schema)["items"]["properties"]
    keys = [k for k, v in pr.items() if "format" in v and v["format"] == "duration"]

    if len(keys) > 0:
        return [d | {k: get_duration(d[k]) for k in keys} for d in data]
    else:
        return data


def get_timedelta_fields(schema: dict) -> list[str]:
    pr = replace_refs(schema)["items"]["properties"]
    return [k for k, v in pr.items() if "format" in v and v["format"] == "duration"]


def update_timedelta_fields(model: BaseModel, timedelta_fields: list[str]) -> BaseModel:
    """returns a new pydantic model where serialization validators have been added to dates,
    datetimes and durations for compatibility with excel"""
    deltas = {
        k: (timedelta, (lambda obj: obj.default if hasattr(obj, "default") else ...)(v))
        for k, v in model.model_fields.items()
        if k in timedelta_fields
    } | {"__base__": model}
    return create_model(model.__name__ + "New", **deltas)


def update_timedelta(model: BaseModel, timedelta_fields: list[str]) -> BaseModel:
    """returns a new pydantic model where serialization validators have been added to dates, datetimes and durations for compatibility with excel of array items"""
    assert len(model.model_fields) == 1
    assert list(model.model_fields.keys()) == ["root"]
    item_model = model.model_fields["root"].annotation.__args__[0]
    new_item_model = update_timedelta_fields(item_model, timedelta_fields)
    new_model = create_model(
        model.__name__ + "New",
        **{"root": (ty.List[new_item_model], ...)} | {"__base__": model},
    )
    return new_model


def get_jsonschema(metadata: DataGridMetaData) -> dict:
    if metadata.schema_url is not None:
        return requests.get(metadata.schema_url).json()
    return None


import pandas as pd


# def read_worksheet(
#     workbook: pd.ExcelFile,
#     worksheet: str,
#     get_jsonschema: ty.Optional[ty.Callable[[DataGridMetaData], dict]] = get_jsonschema,
#     return_pydantic_model: bool = False,
# ) -> tuple[list[[dict, ty.Type[BaseModel]]], DataGridMetaData]:


#     metadata = read_metadata(workbook.parse(worksheet, nrows=0).columns[0])
#     data = worksheet.to_python(skip_empty_area=True)
#     process_data(data, metadata)


def read_worksheet(
    worksheet: CalamineSheet,
    get_jsonschema: ty.Optional[ty.Callable[[DataGridMetaData], dict]] = None,
    *,
    return_pydantic_model: bool = False,
) -> list[dict]:

    data = worksheet.to_python(skip_empty_area=True)
    data, metadata = read_data(data)
    if get_jsonschema is not None:
        json_schema = get_jsonschema(metadata)
        if json_schema is not None:
            timedelta_fields = get_timedelta_fields(json_schema)
            pydantic_model = pydantic_model_from_json_schema(json_schema)
            if len(timedelta_fields) > 0:
                pydantic_model = update_timedelta(pydantic_model, timedelta_fields)
                # ^ HACK: convert timedelta manually as generater pydantic model can't manage...
                #   REF: https://github.com/koxudaxi/datamodel-code-generator/issues/1624

            data = make_datetime_tz_aware(data, pydantic_model)
            # ^ HACK: assume utc time for all datetimes as excel doesn't support tz...
            # data = parse_timedelta(data, json_schema)
            # ^ HACK: convert timedelta manually as generater pydantic model can't manage...
            if return_pydantic_model:
                return pydantic_model.model_validate(data), metadata
            else:
                return (
                    pydantic_model.model_validate(data).model_dump(mode="json"),
                    metadata,
                )
        else:
            return data, metadata
    else:
        return data, metadata


import pandas as pd


def read_excel(
    path,
    get_jsonschema: ty.Optional[
        ty.Callable[[DataGridMetaData], ty.Type[BaseModel]]
    ] = None,
):
    workbook = CalamineWorkbook.from_path(path)
    sheet = workbook.sheet_names[0]
    worksheet = workbook.get_sheet_by_name(sheet)
    return read_worksheet(worksheet, get_jsonschema)
