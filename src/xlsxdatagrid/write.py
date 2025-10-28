import csv
import io
import pathlib
import typing as ty
from datetime import date, datetime

from pydantic import BaseModel

from xlsxdatagrid.xlsxdatagrid import (
    DataGridSchema,
    coerce_schema,
    generate_metadata_string,
)


def csv_from_string(
    csv_string: str,
    schema: dict | DataGridSchema | BaseModel | ty.Type[BaseModel],
    include_metadata: bool = True,
    include_header_titles: bool = True,
    string_delimiter: str = "\t",
    fpth: ty.Optional[pathlib.Path] = None,
    is_transposed: bool = False,
):
    """Convert a CSV string to a CSV file with optional schema metadata and header names."""

    # Parse the CSV string
    rows = list(csv.reader(io.StringIO(csv_string), delimiter=string_delimiter))
    if not rows:
        return None

    # Handle header inclusion/exclusion
    if not include_header_titles:
        if is_transposed:
            rows = rows[1:]
        else:
            rows = [row[1:] for row in rows if len(row) > 1]

    # Prepare schema and optional metadata
    gridschema = coerce_schema(schema)
    metadata = generate_metadata_string(gridschema) if include_metadata else None

    # Define output file path
    fpth = fpth or pathlib.Path(f"{gridschema.title}.csv")

    # Write the output file
    with fpth.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        if metadata:
            writer.writerow([metadata])
        writer.writerows(rows)

    return fpth
