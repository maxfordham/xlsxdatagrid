# std libs
import csv
import importlib.util
import json
import sys
import typing as ty
from datetime import date, datetime, time, timedelta, timezone
from io import StringIO
from pathlib import Path
from tempfile import TemporaryDirectory

from casefy import snakecase
from datamodel_code_generator import DataModelType, InputFileType, generate
from pydantic import AwareDatetime, BaseModel, ValidationError

# 3rd party
from python_calamine import CalamineSheet, CalamineWorkbook

# local
from xlsxdatagrid.xlsxdatagrid import DataGridMetaData


def _replace_empty_with_none(value: str) -> ty.Optional[str]:
    """Helper to replace empty strings with None."""
    return None if value == "" else value


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
        spec = importlib.util.spec_from_file_location(module_name, output)
        module = importlib.util.module_from_spec(spec)
        sys.modules[module_name] = module
        spec.loader.exec_module(module)
    return getattr(module, load)


def read_metadata(s: str) -> DataGridMetaData:
    s = s.replace("#", "")
    li = [x.split("=") for x in s.split(" - ")]
    di = {snakecase(x[0]): x[1] for x in li}
    return DataGridMetaData(**di)


def process_data(
    data: list[list[int | float | str | bool | time | date | datetime | timedelta],],
    is_transposed: bool = False,
    header_depth: int = 1,
    empty_string_to_none=True,
) -> list[dict]:
    if is_transposed:
        data = list(map(list, zip(*data)))

    header_names = [d[0] for d in data[0:header_depth]]

    if empty_string_to_none:
        data = [[_replace_empty_with_none(v) for v in row] for row in data]

    headers = {h: data[n] for n, h in enumerate(header_names)}
    header = headers[header_names[-1]]

    data = data[len(header_names) :]
    data = [dict(zip(header, d)) for d in data]

    return data


def process_data_with_metadata(
    data: list[list[int | float | str | bool | time | date | datetime | timedelta],],
    get_datamodel: ty.Optional[
        ty.Callable[[DataGridMetaData], ty.Type[BaseModel]]
    ] = None,
) -> tuple[list[dict], DataGridMetaData]:
    metadata = read_metadata(data[0][0])
    data_without_comments = drop_leading_comments(data)
    processed_data = process_data(
        data_without_comments,
        metadata.is_transposed,
        metadata.header_depth,
        True,
    )
    processed_metadata = process_metadata(metadata, data)
    json_schema = (
        get_datamodel(processed_metadata) if get_datamodel is not None else None
    )
    if json_schema is not None:
        pydantic_model = pydantic_model_from_json_schema(json_schema)
    if pydantic_model is not None:
        processed_data = pydantic_validate_data(processed_data, pydantic_model)
    return processed_data, processed_metadata


def process_metadata(metadata: DataGridMetaData, data: list[dict]) -> DataGridMetaData:
    """Extracts DataGridMetaData from the given data."""
    hd = metadata.header_depth
    is_t = metadata.is_transposed
    if is_t:
        data = list(map(list, zip(*data)))

    header_names = [d[0] for d in data[0:hd]]
    data = [d[1:] for d in data]
    headers = {h: data[n] for n, h in enumerate(header_names)}
    metadata.datagrid_index_name = list(headers.keys())
    metadata.header = list(headers.values())

    return metadata


def get_datamodel(metadata: DataGridMetaData) -> dict:
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
        # HACK: if data is from csv string, run the pydantic validation before adding timezone info
        if type(data[0][keys[0]]) is str:
            data = pydantic_model.model_validate(data).model_dump(
                mode="python", by_alias=True
            )
        return [d | {k: d[k].replace(tzinfo=timezone.utc) for k in keys} for d in data]
    else:
        return data


def drop_leading_comments(data: list[list[str]]) -> list[list[str]]:
    """
    Removes only the initial consecutive lines that start with '#'
    from the list of CSV rows.
    """
    for i, row in enumerate(data):
        # skip empty rows too
        if not row or not row[0].lstrip().startswith("#"):
            return data[i:]  # return from the first non-comment line onward
    return []


def get_list_of_list_from_worksheet(worksheet: CalamineSheet) -> list[list]:
    return worksheet.to_python(skip_empty_area=True)


def get_list_of_list_from_string(
    csv_string: str, delimiter: str = "\t"
) -> list[list[int | float | str | bool | time | date | datetime | timedelta],]:
    csv_file = StringIO(csv_string)
    reader = csv.reader(csv_file, delimiter=delimiter)
    data = [x for x in reader]
    return data


def pydantic_validate_data(
    data, pydantic_model: BaseModel, return_pydantic_model: bool = False
):
    data = make_datetime_tz_aware(data, pydantic_model)
    obj = pydantic_model.model_validate(data)
    if return_pydantic_model:
        return obj
    else:
        return obj.model_dump(mode="json", by_alias=True)


def read_excel_from_metadata(
    path,
    get_datamodel: ty.Optional[
        ty.Callable[[DataGridMetaData], ty.Type[BaseModel]]
    ] = None,
):
    workbook = CalamineWorkbook.from_path(path)
    sheet = workbook.sheet_names[0]
    worksheet = workbook.get_sheet_by_name(sheet)
    data = get_list_of_list_from_worksheet(worksheet)
    return process_data_with_metadata(data, get_datamodel)


def read_list_of_lists(
    data: list[list[int | float | str | bool | time | date | datetime | timedelta],],
    is_transposed: bool = False,
    header_depth: int = 1,
    model: BaseModel | None = None,
) -> list[dict]:
    data = drop_leading_comments(data)
    processed_data = process_data(data, is_transposed, header_depth, True)
    try:
        validated_data = pydantic_validate_data(processed_data, model)
        return validated_data, []
    except ValidationError as exc:
        return [], exc.errors()
    # TODO @Arshadwaqas115: why returning a tuple? better to return data only


def read_excel(
    path,
    is_transposed: bool = False,
    header_depth: int = 1,
    model: BaseModel | None = None,
):
    workbook = CalamineWorkbook.from_path(path)
    sheet = workbook.sheet_names[0]
    worksheet = workbook.get_sheet_by_name(sheet)
    data = get_list_of_list_from_worksheet(worksheet)
    return read_list_of_lists(data, is_transposed, header_depth, model)


def read_csv_string(
    csv_string: str,
    is_transposed: bool = False,
    header_depth: int = 1,
    model: BaseModel | None = None,
    delimiter: str = ",",
) -> list[dict]:
    """Read a CSV string and process it into a list of dicts, optionally validating with a pydantic model. Note: This gets rid of all initial comments in the CSV string before the data begins.

    Args:
        csv_string (str): A csv string (could be a tsv string if delimiter is set to "\t").
        is_transposed (bool, optional): Configure whether the csv string is transposed or not. Defaults to False.
        header_depth (int, optional): The header depth in the csv string. Defaults to 1.
        model (BaseModel | None, optional): The pydantic model. Defaults to None.
        delimiter (str, optional): The delimiter that the data is separated on. Defaults to ",".
        previous_value (list[dict] | None, optional): . Defaults to None.

    Returns:
        _type_: List of dictionaries representing the data rows.
    """

    data = get_list_of_list_from_string(csv_string, delimiter=delimiter)
    return read_list_of_lists(data, is_transposed, header_depth, model)


def read_csv_string_with_metadata(
    csv_string: str,
    get_datamodel: ty.Optional[
        ty.Callable[[DataGridMetaData], ty.Type[BaseModel]]
    ] = None,
    delimiter: str = ",",
):
    data = get_list_of_list_from_string(csv_string, delimiter=delimiter)
    return process_data_with_metadata(data, get_datamodel)
