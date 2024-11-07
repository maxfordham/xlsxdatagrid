import os
import pathlib

import pytest

FDIR_EXAMPLES = pathlib.Path(__file__).parent / "xlsxwriter-examples"


@pytest.fixture()
def move_dir():
    FDIR_EXAMPLES.mkdir(exist_ok=True)
    os.chdir(FDIR_EXAMPLES)


@pytest.mark.skip()
def test_write_chart(move_dir):
    #######################################################################
    #
    # An example of creating Excel Line charts with Python and XlsxWriter.
    #
    # SPDX-License-Identifier: BSD-2-Clause
    # Copyright 2013-2024, John McNamara, jmcnamara@cpan.org
    #
    import xlsxwriter

    workbook = xlsxwriter.Workbook("chart_line.xlsx")
    worksheet = workbook.add_worksheet()
    bold = workbook.add_format({"bold": 1})

    # Add the worksheet data that the charts will refer to.
    headings = ["Number", "Batch 1", "Batch 2"]
    data = [
        [2, 3, 4, 5, 6, 7],
        [10, 40, 50, 20, 10, 50],
        [30, 60, 70, 50, 40, 30],
    ]

    worksheet.write_row("A1", headings, bold)
    worksheet.write_column("A2", data[0])
    worksheet.write_column("B2", data[1])
    worksheet.write_column("C2", data[2])

    # Create a new chart object. In this case an embedded chart.
    chart1 = workbook.add_chart({"type": "line"})

    # Configure the first series.
    chart1.add_series(
        {
            "name": "=$B$1",
            "categories": "=Sheet1!$A$2:$A$7",
            "values": "=Sheet1!$B$2:$B$7",
        }
    )

    # Add a chart title and some axis labels.
    chart1.set_title({"name": "Results of sample analysis"})
    chart1.set_x_axis({"name": "Test number"})
    chart1.set_y_axis({"name": "Sample length (mm)"})

    # Set an Excel chart style. Colors with white outline and shadow.
    chart1.set_style(10)

    # Insert the chart into the worksheet (with an offset).
    worksheet.insert_chart("D2", chart1, {"x_offset": 25, "y_offset": 10})

    #######################################################################

    workbook.close()


@pytest.mark.skip()
def test_protected(move_dir):
    import xlsxwriter

    workbook = xlsxwriter.Workbook("protection.xlsx")
    worksheet = workbook.add_worksheet()

    # Create some cell formats with protection properties.
    unlocked = workbook.add_format({"locked": False})
    hidden = workbook.add_format({"hidden": True})

    # Format the columns to make the text more visible.
    worksheet.set_column("A:A", 40)

    # Turn worksheet protection on.
    worksheet.protect()

    # Write a locked, unlocked and hidden cell.
    worksheet.write("A1", "Cell B1 is locked. It cannot be edited.")
    worksheet.write("A2", "Cell B2 is unlocked. It can be edited.")
    worksheet.write("A3", "Cell B3 is hidden. The formula isn't visible.")

    worksheet.write_formula("B1", "=1+2")  # Locked by default.
    worksheet.write_formula("B2", "=1+2", unlocked)
    worksheet.write_formula("B3", "=1+2", hidden)

    workbook.close()
