# pylint: disable=missing-function-docstring,missing-module-docstring,too-many-arguments
from contextlib import nullcontext as does_not_raise
from pathlib import Path
from unittest import mock
import pytest
from swatch.swatch import ColorSpace, ValidationError, \
    hex_color_to_raw, parse_aco, parse_csv, raw_color_to_hex, validate_color_space

@pytest.mark.parametrize(
    "color_space,expected",
    [
        (ColorSpace.RGB, does_not_raise()),
        (ColorSpace.HSB, does_not_raise()),
        (ColorSpace.CMYK, does_not_raise()),
        (ColorSpace.PANTONE, pytest.raises(
            ValidationError, match="unsupported color space: Pantone matching system")
        ),
        (ColorSpace.FOCOLTONE, pytest.raises(
            ValidationError, match="unsupported color space: Focoltone colour system")
        ),
        (ColorSpace.TRUMATCH, pytest.raises(
            ValidationError, match="unsupported color space: Trumatch color")
        ),
        (ColorSpace.TOYO, pytest.raises(
            ValidationError, match="unsupported color space: Toyo 88 colorfinder 1050")
        ),
        (ColorSpace.LAB, pytest.raises(
            ValidationError, match="unsupported color space: Lab")
        ),
        (ColorSpace.GRAYSCALE, does_not_raise()),
        (ColorSpace.HKS, pytest.raises(
            ValidationError, match="unsupported color space: HKS colors")
        ),
    ],
)
def test_validate_color_space(color_space, expected):
    # expect
    with expected:
        validate_color_space(color_space)

@pytest.mark.parametrize(
    "color_space,expected",
    [
        (ColorSpace.RGB, does_not_raise()),
        (ColorSpace.HSB, does_not_raise()),
        (ColorSpace.CMYK, does_not_raise()),
        (ColorSpace.PANTONE, pytest.raises(
            ValidationError, match="unsupported color space: Pantone matching system")
        ),
        (ColorSpace.FOCOLTONE, pytest.raises(
            ValidationError, match="unsupported color space: Focoltone colour system")
        ),
        (ColorSpace.TRUMATCH, pytest.raises(
            ValidationError, match="unsupported color space: Trumatch color")
        ),
        (ColorSpace.TOYO, pytest.raises(
            ValidationError, match="unsupported color space: Toyo 88 colorfinder 1050")
        ),
        (ColorSpace.LAB, pytest.raises(
            ValidationError, match="unsupported color space: Lab")
        ),
        (ColorSpace.GRAYSCALE, does_not_raise()),
        (ColorSpace.HKS, pytest.raises(
            ValidationError, match="unsupported color space: HKS colors")
        ),
    ],
)
def test_raw_color_to_hex_with_validation(color_space, expected):
    # expect
    with expected:
        raw_color_to_hex(color_space, 10000, 0, 0, 0)

@pytest.mark.parametrize(
    "component_1,component_2,component_3,component_4",
    [
        (-1, 0, 0, 0),
        (65536, 0, 0, 0),
        (0, -1, 0, 0),
        (0, 65536, 0, 0),
        (0, 0, -1, 0),
        (0, 0, 65536, 0),
        (0, 0, 0, 1),
    ],
)
def test_raw_color_to_hex_for_rgb_invalid_values(
    component_1, component_2, component_3, component_4
):
    # expect
    with pytest.raises(ValidationError, match=r"invalid RGB value:"):
        raw_color_to_hex(
            ColorSpace.RGB, component_1, component_2, component_3, component_4
        )

@pytest.mark.parametrize(
    "component_1,component_2,component_3,component_4",
    [
        (-1, 0, 0, 0),
        (65536, 0, 0, 0),
        (0, -1, 0, 0),
        (0, 65536, 0, 0),
        (0, 0, -1, 0),
        (0, 0, 65536, 0),
        (0, 0, 0, 1),
    ],
)
def test_raw_color_to_hex_for_hsb_invalid_values(
    component_1, component_2, component_3, component_4
):
    # expect
    with pytest.raises(ValidationError, match=r"invalid HSB value:"):
        raw_color_to_hex(
            ColorSpace.HSB, component_1, component_2, component_3, component_4
        )

@pytest.mark.parametrize(
    "component_1,component_2,component_3,component_4",
    [
        (-1, 0, 0, 0),
        (65536, 0, 0, 0),
        (0, -1, 0, 0),
        (0, 65536, 0, 0),
        (0, 0, -1, 0),
        (0, 0, 65536, 0),
        (0, 0, 0, -1),
        (0, 0, 0, 65536),
    ],
)
def test_raw_color_to_hex_for_cmyk_invalid_values(
    component_1, component_2, component_3, component_4
):
    # expect
    with pytest.raises(ValidationError, match=r"invalid CMYK value:"):
        raw_color_to_hex(
            ColorSpace.CMYK, component_1, component_2, component_3, component_4
        )

@pytest.mark.parametrize(
    "component_1,component_2,component_3,component_4",
    [
        (-1, 0, 0, 0),
        (10001, 0, 0, 0),
        (65536, 0, 0, 0),
    ],
)
def test_raw_color_to_hex_for_grayscale_invalid_values(
    component_1, component_2, component_3, component_4
):
    # expect
    with pytest.raises(ValidationError, match=r"invalid Grayscale value:"):
        raw_color_to_hex(
            ColorSpace.GRAYSCALE, component_1, component_2, component_3, component_4
        )

@pytest.mark.parametrize(
    "color_space,component_1,component_2,component_3,component_4,expected",
    [
        (ColorSpace.RGB, 65535, 0, 0, 0, '#FFFF00000000'),
        (ColorSpace.HSB, 0, 65535, 65535, 0, '#0000FFFFFFFF'),
        (ColorSpace.CMYK, 0, 65535, 65535, 65535, '#0000FFFFFFFFFFFF'),
        (ColorSpace.GRAYSCALE, 10000, 0, 0, 0, '#2710'),
    ],
)
def test_raw_color_to_hex_for_supported_color_space(
    color_space, component_1, component_2, component_3, component_4, expected
):
    # expect
    assert raw_color_to_hex(
        color_space, component_1, component_2, component_3, component_4
    ) == expected

@pytest.mark.parametrize(
    "color_hex,exception,expected",
    [
        ('#000000', does_not_raise(), [0, 0, 0, 0]),
        ('#0F0F0F', does_not_raise(), [3855, 3855, 3855, 0]),
        ('#FFFFFF', does_not_raise(), [65535, 65535, 65535, 0]),
        ('000000000000', does_not_raise(), [0, 0, 0, 0]),
        ('0F0F0F0F0F0F', does_not_raise(), [3855, 3855, 3855, 0]),
        ('FFFFFFFFFFFF', does_not_raise(), [65535, 65535, 65535, 0]),
        ('# ', pytest.raises(
            ValidationError, match=r"unsupported color format:"), []
        ),
        ('F0F', pytest.raises(
            ValidationError, match=r"unsupported color format:"), []
        ),
        ('F0F0F', pytest.raises(
            ValidationError, match=r"unsupported color format:"), []
        ),
        ('F0F0F0F0F0F', pytest.raises(
            ValidationError, match=r"unsupported color format:"), []
        ),
        ('F0F0F0F0F0F0F', pytest.raises(
            ValidationError, match=r"unsupported color format:"), []
        ),
    ],
)
def test_hex_color_to_raw_for_rgb(color_hex, exception, expected):
    # expect
    with exception:
        assert hex_color_to_raw(ColorSpace.RGB, color_hex) == expected

@pytest.mark.parametrize(
    "color_hex,exception,expected",
    [
        ('#000000', does_not_raise(), [0, 0, 0, 0]),
        ('#0F0F0F', does_not_raise(), [3855, 3855, 3855, 0]),
        ('#FFFFFF', does_not_raise(), [65535, 65535, 65535, 0]),
        ('000000000000', does_not_raise(), [0, 0, 0, 0]),
        ('0F0F0F0F0F0F', does_not_raise(), [3855, 3855, 3855, 0]),
        ('FFFFFFFFFFFF', does_not_raise(), [65535, 65535, 65535, 0]),
        ('# ', pytest.raises(
            ValidationError, match=r"unsupported color format:"), []
        ),
        ('F0F', pytest.raises(
            ValidationError, match=r"unsupported color format:"), []
        ),
        ('F0F0F', pytest.raises(
            ValidationError, match=r"unsupported color format:"), []
        ),
        ('F0F0F0F0F0F', pytest.raises(
            ValidationError, match=r"unsupported color format:"), []
        ),
        ('F0F0F0F0F0F0F', pytest.raises(
            ValidationError, match=r"unsupported color format:"), []
        ),
    ],
)
def test_hex_color_to_raw_for_hsb(color_hex, exception, expected):
    # expect
    with exception:
        assert hex_color_to_raw(ColorSpace.HSB, color_hex) == expected

@pytest.mark.parametrize(
    "color_hex,exception,expected",
    [
        ('#00000000', does_not_raise(), [0, 0, 0, 0]),
        ('#0F0F0F0F', does_not_raise(), [3855, 3855, 3855, 3855]),
        ('#FFFFFFFF', does_not_raise(), [65535, 65535, 65535, 65535]),
        ('0000000000000000', does_not_raise(), [0, 0, 0, 0]),
        ('0F0F0F0F0F0F0F0F', does_not_raise(), [3855, 3855, 3855, 3855]),
        ('FFFFFFFFFFFFFFFF', does_not_raise(), [65535, 65535, 65535, 65535]),
        ('# ', pytest.raises(
            ValidationError, match=r"unsupported color format:"), []
        ),
        ('F0F0F0F', pytest.raises(
            ValidationError, match=r"unsupported color format:"), []
        ),
        ('F0F0F0F0F', pytest.raises(
            ValidationError, match=r"unsupported color format:"), []
        ),
        ('F0F0F0F0F0F0F0F', pytest.raises(
            ValidationError, match=r"unsupported color format:"), []
        ),
        ('F0F0F0F0F0F0F0F0F', pytest.raises(
            ValidationError, match=r"unsupported color format:"), []
        ),
    ],
)
def test_hex_color_to_raw_for_cmyk(color_hex, exception, expected):
    # expect
    with exception:
        assert hex_color_to_raw(ColorSpace.CMYK, color_hex) == expected

@pytest.mark.parametrize(
    "color_hex,exception,expected",
    [
        ('#00', does_not_raise(), [0, 0, 0, 0]),
        ('#0F', does_not_raise(), [3855, 0, 0, 0]),
        ('#26', does_not_raise(), [9766, 0, 0, 0]),
        ('0000', does_not_raise(), [0, 0, 0, 0]),
        ('0F0F', does_not_raise(), [3855, 0, 0, 0]),
        ('2710', does_not_raise(), [10000, 0, 0, 0]),
        ('#2711', pytest.raises(
            ValidationError, match=r"invalid grayscale value: 2711"), []
        ),
        ('# ', pytest.raises(
            ValidationError, match=r"unsupported color format:"), []
        ),
        ('F0F0F0F', pytest.raises(
            ValidationError, match=r"unsupported color format:"), []
        ),
        ('F0F0F0F0F', pytest.raises(
            ValidationError, match=r"unsupported color format:"), []
        ),
        ('F0F0F0F0F0F0F0F', pytest.raises(
            ValidationError, match=r"unsupported color format:"), []
        ),
        ('F0F0F0F0F0F0F0F0F', pytest.raises(
            ValidationError, match=r"unsupported color format:"), []
        ),
    ],
)
def test_hex_color_to_raw_for_grayscale(color_hex, exception, expected):
    # expect
    with exception:
        assert hex_color_to_raw(ColorSpace.GRAYSCALE, color_hex) == expected

@pytest.mark.parametrize(
    "color_space,expected",
    [
        (ColorSpace.PANTONE, pytest.raises(
            ValidationError, match="unsupported color space: Pantone matching system")
        ),
        (ColorSpace.FOCOLTONE, pytest.raises(
            ValidationError, match="unsupported color space: Focoltone colour system")
        ),
        (ColorSpace.TRUMATCH, pytest.raises(
            ValidationError, match="unsupported color space: Trumatch color")
        ),
        (ColorSpace.TOYO, pytest.raises(
            ValidationError, match="unsupported color space: Toyo 88 colorfinder 1050")
        ),
        (ColorSpace.LAB, pytest.raises(
            ValidationError, match="unsupported color space: Lab")
        ),
        (ColorSpace.HKS, pytest.raises(
            ValidationError, match="unsupported color space: HKS colors")
        ),
    ],
)
def test_hex_color_to_raw_for_unsupported(color_space, expected):
    # expect
    with expected:
        hex_color_to_raw(color_space, "#000000")

def test_parse_aco_succeed():
    # given
    base_path = Path(__file__).parent
    file_path = (base_path / "../examples/utf.aco").resolve()

    # when
    with open(file_path, "rb") as file:
        color_data = parse_aco(file)
    # then
    assert color_data == [
        ["Zażółć gęślą jaźń", ColorSpace.HSB, "#2A2AA8A8E3E3"],
        ["チェリー", ColorSpace.HSB,"#F2F2EAEAAFAF"],
        ["a", ColorSpace.HSB, "#F2F20000FFFF"]
    ]

def test_parse_aco_does_not_fail_on_invalid_file():
    # given
    base_path = Path(__file__).parent
    file_path = (base_path / "../examples/utf.csv").resolve()

    # when
    with open(file_path, "rb") as file:
        color_data = parse_aco(file)
    # then
    assert not color_data

def test_parse_csv_succeed():
    # given
    base_path = Path(__file__).parent
    file_path = (base_path / "../examples/utf.csv").resolve()

    # when
    with open(file_path, "r", encoding="utf-8") as file:
        color_data = parse_csv(file)
    # then
    assert color_data == [
        ["Zażółć gęślą jaźń", ColorSpace.HSB, 10794, 43176, 58339, 0],
        ["チェリー", ColorSpace.HSB, 62194, 60138, 44975, 0],
        ["a", ColorSpace.HSB,  62194, 0, 65535, 0]
    ]

@mock.patch("builtins.open", create=True)
def test_parse_csv_does_not_fail_on_invalid_file(file):
    # expect
    assert not parse_csv(file)
