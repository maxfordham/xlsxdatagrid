from xlsxdatagrid.read import read_excel
from .constants import PATH_XL, PATH_XL_TRANSPOSED
from .test_xlsxdatagrid import TestArray, TestArrayTransposed
import typing as ty
from pydantic import BaseModel
import pytest


def model_loader(name):
    if name in globals():
        return globals()[name]
    else:
        return None


@pytest.mark.parametrize("path", [PATH_XL, PATH_XL_TRANSPOSED])
def test_read_excel(path):
    obj = read_excel(path, model_loader=model_loader)
    assert obj.model_json_schema()["datagrid_index_name"] == (
        "section",
        "title",
        "name",
    )
    assert isinstance(obj.model_dump(), list)
    print("done")
