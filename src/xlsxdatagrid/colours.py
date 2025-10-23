import logging

# use cmap (which has Bang Wong built in)
from palettable.tableau import (
    BlueRed_6,
    BlueRed_12,
    GreenOrange_6,
    GreenOrange_12,
    PurpleGray_6,
    PurpleGray_12,
    Tableau_10,
    Tableau_20,
)
from pydantic_extra_types.color import Color

BANG_WONG_COLORS = dict(
    black=Color("RGB(0, 0, 0)"),
    orange=Color("RGB(230, 159, 0)"),
    sky_blue=Color("RGB(86, 180, 233)"),
    bluish_green=Color("RGB(0, 158, 115)"),
    yellow=Color("RGB(240, 228, 66)"),
    blue=Color("RGB(0, 114, 178)"),
    vermillion=Color("RGB(213, 94, 0)"),
    reddish_purple=Color("RGB(204, 121, 167)"),
)


class BangWong_7:
    def __init__(self):
        self.colors = BANG_WONG_COLORS

    @property
    def hex_colors(self):
        return [v.as_hex() for k, v in self.colors.items() if k != "black"]


class BangWong_8:
    def __init__(self):
        self.colors = BANG_WONG_COLORS

    @property
    def hex_colors(self):
        return [v.as_hex() for k, v in self.colors.items()]


XLSXDATAGRID_STANDARD_PALLETTES = {
    ("bangwong", (7, 8)): (BangWong_7(), BangWong_8()),
    ("BlueRed", (6, 12)): (BlueRed_6, BlueRed_12),
    ("PurpleGray", (6, 12)): (PurpleGray_6, PurpleGray_12),
    ("GreenOrange", (6, 12)): (GreenOrange_6, GreenOrange_12),
    ("Tableau", (10, 20)): (Tableau_10, Tableau_20),
}


def get_color_pallette(
    length, palettes_in_use, palettes=XLSXDATAGRID_STANDARD_PALLETTES
):
    _max = list(XLSXDATAGRID_STANDARD_PALLETTES.keys())[-1][1][1]
    _max_pallete = list(palettes.values())[-1][1]
    for k, v in palettes.items():
        if k[0] not in palettes_in_use:
            if length < k[1][0]:
                palettes_in_use += [k[0]]
                return v[0].hex_colors[0:length]
            elif k[1][0] < length <= k[1][1]:
                palettes_in_use += [k[0]]
                return v[1].hex_colors[0:length]
            elif k[1][1] < length <= _max:
                pass
            elif length > _max:
                logging.warning(f"don't have a colour pallette of length: {length}")
                extra = length - _max
                if extra > _max:
                    raise ValueError(
                        f"error selecting colour pallette of length = {length}"
                    )
                else:
                    return _max_pallete.hex_colors + _max_pallete.hex_colors[0:extra]

            else:
                raise ValueError(
                    f"error selecting colour pallette of length = {length}"
                )


def color_variant(hex_color, brightness_offset=1):
    """takes a color like #87c95f and produces a lighter or darker variant

    Reference:
        https://chase-seibert.github.io/blog/2011/07/29/python-calculate-lighterdarker-rgb-colors.html
    """
    if len(hex_color) != 7:
        if len(hex_color) != 4:
            raise Exception(
                "Passed %s into color_variant(), needs to be in #87c95f format."
                % hex_color
            )
        else:
            hex_color = hex_color + hex_color[1:]
    rgb_hex = [hex_color[x : x + 2] for x in [1, 3, 5]]
    new_rgb_int = [int(hex_value, 16) + brightness_offset for hex_value in rgb_hex]
    new_rgb_int = [
        min([255, max([0, i])]) for i in new_rgb_int
    ]  # make sure new values are between 0 and 255
    # hex() produces "0x88", we want just "88"
    return "#" + "".join([hex(i)[2:] for i in new_rgb_int])
