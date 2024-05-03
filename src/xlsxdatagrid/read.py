from python_calamine import CalamineWorkbook
import typing as ty
from pydantic import BaseModel


def read_metadata(s):
    s = s.replace("#", "")
    li = [l.split("=") for l in s.split(" - ")]
    return {l[0]: l[1] for l in li}


def process_data(data, metadata):
    hd = int(metadata.get("HeaderDepth"))
    is_t = eval(metadata.get("IsTransposed"))
    if is_t:
        data = list(map(list, zip(*data)))

    # else:
    header_names = [d[0] for d in data[0:hd]]
    data = [d[1:] for d in data]
    headers = {h: data[n] for n, h in enumerate(header_names)}
    header = headers[header_names[-1]]
    metadata["Headers"] = headers

    data = data[len(header_names) :]
    data = [dict(zip(header, d)) for d in data]

    return data, metadata


def read_data(data):
    if data[0][0][0] != "#":
        raise ValueError(
            "the first row must be a metadata string beginning with the char '#'"
        )
    metadata = read_metadata(data[0][0])
    data = data[1:]
    return process_data(data, metadata)


def load_data(data, metadata, loader: ty.Callable[[str], ty.Type[BaseModel]]):
    name = metadata.get("Schema")
    model = loader(name)
    if model is not None:
        return model.model_validate(data)
    else:
        return data


def read_excel(path, model_loader=None):
    workbook = CalamineWorkbook.from_path(path)
    sheet = workbook.sheet_names[0]
    data = workbook.get_sheet_by_name(sheet).to_python(skip_empty_area=True)
    data, metadata = read_data(data)
    if model_loader is not None:
        return load_data(data, metadata, model_loader)
    else:
        return data
