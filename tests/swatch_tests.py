# pylint: disable=missing-function-docstring,missing-module-docstring,too-many-arguments
from contextlib import nullcontext as does_not_raise
import pytest
from swatch.swatch import ColorSpace, ValidationError, \
    hex_color_to_raw, raw_color_to_hex, validate_color_space

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
