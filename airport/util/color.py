import re
import os
from configparser import ConfigParser
from enum import Enum
from PySide6.QtGui import QColor


class ColorType(Enum):
    COLOR_TEXT_NEGATIVE = 0
    COLOR_TEXT_NEUTRAL = 1
    COLOR_TEXT_NORMAL = 2
    COLOR_TEXT_POSITIVE = 3
    COLOR_TEXT_LINK = 4


class SystemColorScheme:
    def __init__(self):
        conf = ConfigParser()

        # attempt to find current KDE color scheme
        if os.path.exists(f"{os.environ['HOME']}/.config/kdeglobals"):
            conf.read(f"{os.environ['HOME']}/.config/kdeglobals")
            self.text_normal = self._parse_rgb(conf["Colors:View"]["ForegroundNormal"])
            self.text_positive = self._parse_rgb(
                conf["Colors:View"]["ForegroundPositive"]
            )
            self.text_neutral = self._parse_rgb(
                conf["Colors:View"]["ForegroundNeutral"]
            )
            self.text_negative = self._parse_rgb(
                conf["Colors:View"]["ForegroundNegative"]
            )
            self.text_link = self._parse_rgb(conf["Colors:View"]["ForegroundLink"])
        # use defaults if no system theme can be found
        else:
            self.text_normal = QColor("white")
            self.text_positive = QColor("green")
            self.text_neutral = QColor("yellow")
            self.text_negative = QColor("red")
            self.text_link = QColor("blue")

    def get_color(self, color_type: int) -> QColor | None:
        """
        Gets a color from the system's color scheme. The parameter `color_type`
        can be any of the `COLOR_*` constants included.

        Parameters
        ----------
        color_type : int
            The `COLOR_*` constant.

        Returns
        -------
        QColor | None
            A QColor object representing the specified color or None if not
            found.
        """
        match color_type:
            case ColorType.COLOR_TEXT_NORMAL:
                return self.text_normal
            case ColorType.COLOR_TEXT_POSITIVE:
                return self.text_positive
            case ColorType.COLOR_TEXT_NEUTRAL:
                return self.text_neutral
            case ColorType.COLOR_TEXT_NEGATIVE:
                return self.text_negative
            case ColorType.COLOR_TEXT_LINK:
                return self.text_link
            case _:
                return None

    def _parse_rgb(self, raw_str: str) -> QColor:
        colors = re.split(r",\s*", raw_str)
        return QColor(int(colors[0]), int(colors[1]), int(colors[2]))
