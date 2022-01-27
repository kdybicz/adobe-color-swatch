"""
Set of enums used across the code.
"""

from enum import Enum, unique
from typing import Optional

@unique
class ColorSpace(Enum):
    """
    Adobe Color Swatch - Color Space Ids.
    """
    RGB = (0, "RGB", True)
    HSB = (1, "HSB", True)
    CMYK = (2, "CMYK", True)
    PANTONE = (3, "Pantone matching system", False)
    FOCOLTONE = (4, "Focoltone colour system", False)
    TRUMATCH = (5, "Trumatch color", False)
    TOYO = (6, "Toyo 88 colorfinder 1050", False)
    LAB = (7, "Lab", False)
    GRAYSCALE = (8, "Grayscale", True)
    HKS = (10, "HKS colors", False)

    def __new__(cls, *args): # type: ignore
        obj = object.__new__(cls)
        obj._value_ = args[0]
        return obj

    def __init__(self, _: int, label: Optional[str] = None, supported: Optional[bool] = False):
        self.label = label
        self.supported = supported

    def __str__(self) -> str:
        return self.label if self.label is not None else "unknown"
