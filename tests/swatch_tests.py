import pytest
from contextlib import nullcontext as does_not_raise
from src.swatch import ValidationError, validate_color_space, raw_color_to_hex, hex_color_to_raw

@pytest.mark.parametrize(
    "color_space_id,expected",
    [
        (0, does_not_raise()),
        (1, does_not_raise()),
        (2, does_not_raise()),
        (3, pytest.raises(ValidationError, match="unsupported color space: Pantone matching system")),
        (4, pytest.raises(ValidationError, match="unsupported color space: Focoltone colour system")),
        (5, pytest.raises(ValidationError, match="unsupported color space: Trumatch color")),
        (6, pytest.raises(ValidationError, match="unsupported color space: Toyo 88 colorfinder 1050")),
        (7, pytest.raises(ValidationError, match="unsupported color space: Lab")),
        (8, does_not_raise()),
        (9, pytest.raises(ValidationError, match="unsupported color space: space id 9")),
        (10, pytest.raises(ValidationError, match="unsupported color space: HKS colors")),
    ],
)
def test_validate_color_space(color_space_id, expected):
    # expect
    with expected:
        validate_color_space(color_space_id)

@pytest.mark.parametrize(
    "color_space_id,expected",
    [
        (0, does_not_raise()),
        (1, does_not_raise()),
        (2, does_not_raise()),
        (3, pytest.raises(ValidationError, match="unsupported color space: space id 3")),
        (4, pytest.raises(ValidationError, match="unsupported color space: space id 4")),
        (5, pytest.raises(ValidationError, match="unsupported color space: space id 5")),
        (6, pytest.raises(ValidationError, match="unsupported color space: space id 6")),
        (7, pytest.raises(ValidationError, match="unsupported color space: space id 7")),
        (8, does_not_raise()),
        (9, pytest.raises(ValidationError, match="unsupported color space: space id 9")),
        (10, pytest.raises(ValidationError, match="unsupported color space: space id 10")),
    ],
)
def test_raw_color_to_hex_with_validation(color_space_id, expected):
    # expect
    with expected:
        raw_color_to_hex(color_space_id, 10000, 0, 0, 0)

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
def test_raw_color_to_hex_for_rgb_invalid_values(component_1, component_2, component_3, component_4):
    # expect
    with pytest.raises(ValidationError, match=r"invalid RGB value:"):
        raw_color_to_hex(0, component_1, component_2, component_3, component_4)

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
def test_raw_color_to_hex_for_hsb_invalid_values(component_1, component_2, component_3, component_4):
    # expect
    with pytest.raises(ValidationError, match=r"invalid HSB value:"):
        raw_color_to_hex(1, component_1, component_2, component_3, component_4)

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
def test_raw_color_to_hex_for_cmyk_invalid_values(component_1, component_2, component_3, component_4):
    # expect
    with pytest.raises(ValidationError, match=r"invalid CMYK value:"):
        raw_color_to_hex(2, component_1, component_2, component_3, component_4)

@pytest.mark.parametrize(
    "component_1,component_2,component_3,component_4",
    [
        (-1, 0, 0, 0),
        (10001, 0, 0, 0),
        (65536, 0, 0, 0),
    ],
)
def test_raw_color_to_hex_for_grayscale_invalid_values(component_1, component_2, component_3, component_4):
    # expect
    with pytest.raises(ValidationError, match=r"invalid Grayscale value:"):
        raw_color_to_hex(8, component_1, component_2, component_3, component_4)

@pytest.mark.parametrize(
    "color_space_id,component_1,component_2,component_3,component_4,expected",
    [
        (0, 65535, 0, 0, 0, '#FFFF00000000'),
        (1, 0, 65535, 65535, 0, '#0000FFFFFFFF'),
        (2, 0, 65535, 65535, 65535, '#0000FFFFFFFFFFFF'),
        (8, 10000, 0, 0, 0, '#2710'),
    ],
)
def test_raw_color_to_hex_for_supported_color_space(color_space_id, component_1, component_2, component_3, component_4, expected):
    # expect
    assert raw_color_to_hex(color_space_id, component_1, component_2, component_3, component_4) == expected

@pytest.mark.parametrize(
    "color_hex,exception,expected",
    [
        ('#000000', does_not_raise(), [0, 0, 0, 0]),
        ('#0F0F0F', does_not_raise(), [3855, 3855, 3855, 0]),
        ('#FFFFFF', does_not_raise(), [65535, 65535, 65535, 0]),
        ('000000000000', does_not_raise(), [0, 0, 0, 0]),
        ('0F0F0F0F0F0F', does_not_raise(), [3855, 3855, 3855, 0]),
        ('FFFFFFFFFFFF', does_not_raise(), [65535, 65535, 65535, 0]),
        ('# ', pytest.raises(ValidationError, match=r"unsupported color format:"), []),
        ('F0F', pytest.raises(ValidationError, match=r"unsupported color format:"), []),
        ('F0F0F', pytest.raises(ValidationError, match=r"unsupported color format:"), []),
        ('F0F0F0F0F0F', pytest.raises(ValidationError, match=r"unsupported color format:"), []),
        ('F0F0F0F0F0F0F', pytest.raises(ValidationError, match=r"unsupported color format:"), []),
    ],
)
def test_hex_color_to_raw_for_rgb(color_hex, exception, expected):
    # expect
    with exception:
        assert hex_color_to_raw(0, color_hex) == expected

@pytest.mark.parametrize(
    "color_hex,exception,expected",
    [
        ('#000000', does_not_raise(), [0, 0, 0, 0]),
        ('#0F0F0F', does_not_raise(), [3855, 3855, 3855, 0]),
        ('#FFFFFF', does_not_raise(), [65535, 65535, 65535, 0]),
        ('000000000000', does_not_raise(), [0, 0, 0, 0]),
        ('0F0F0F0F0F0F', does_not_raise(), [3855, 3855, 3855, 0]),
        ('FFFFFFFFFFFF', does_not_raise(), [65535, 65535, 65535, 0]),
        ('# ', pytest.raises(ValidationError, match=r"unsupported color format:"), []),
        ('F0F', pytest.raises(ValidationError, match=r"unsupported color format:"), []),
        ('F0F0F', pytest.raises(ValidationError, match=r"unsupported color format:"), []),
        ('F0F0F0F0F0F', pytest.raises(ValidationError, match=r"unsupported color format:"), []),
        ('F0F0F0F0F0F0F', pytest.raises(ValidationError, match=r"unsupported color format:"), []),
    ],
)
def test_hex_color_to_raw_for_hsb(color_hex, exception, expected):
    # expect
    with exception:
        assert hex_color_to_raw(1, color_hex) == expected

@pytest.mark.parametrize(
    "color_hex,exception,expected",
    [
        ('#00000000', does_not_raise(), [0, 0, 0, 0]),
        ('#0F0F0F0F', does_not_raise(), [3855, 3855, 3855, 3855]),
        ('#FFFFFFFF', does_not_raise(), [65535, 65535, 65535, 65535]),
        ('0000000000000000', does_not_raise(), [0, 0, 0, 0]),
        ('0F0F0F0F0F0F0F0F', does_not_raise(), [3855, 3855, 3855, 3855]),
        ('FFFFFFFFFFFFFFFF', does_not_raise(), [65535, 65535, 65535, 65535]),
        ('# ', pytest.raises(ValidationError, match=r"unsupported color format:"), []),
        ('F0F0F0F', pytest.raises(ValidationError, match=r"unsupported color format:"), []),
        ('F0F0F0F0F', pytest.raises(ValidationError, match=r"unsupported color format:"), []),
        ('F0F0F0F0F0F0F0F', pytest.raises(ValidationError, match=r"unsupported color format:"), []),
        ('F0F0F0F0F0F0F0F0F', pytest.raises(ValidationError, match=r"unsupported color format:"), []),
    ],
)
def test_hex_color_to_raw_for_cmyk(color_hex, exception, expected):
    # expect
    with exception:
        assert hex_color_to_raw(2, color_hex) == expected

@pytest.mark.parametrize(
    "color_hex,exception,expected",
    [
        ('#00', does_not_raise(), [0, 0, 0, 0]),
        ('#0F', does_not_raise(), [3855, 0, 0, 0]),
        ('#26', does_not_raise(), [9766, 0, 0, 0]),
        ('0000', does_not_raise(), [0, 0, 0, 0]),
        ('0F0F', does_not_raise(), [3855, 0, 0, 0]),
        ('2710', does_not_raise(), [10000, 0, 0, 0]),
        ('# ', pytest.raises(ValidationError, match=r"unsupported color format:"), []),
        ('F0F0F0F', pytest.raises(ValidationError, match=r"unsupported color format:"), []),
        ('F0F0F0F0F', pytest.raises(ValidationError, match=r"unsupported color format:"), []),
        ('F0F0F0F0F0F0F0F', pytest.raises(ValidationError, match=r"unsupported color format:"), []),
        ('F0F0F0F0F0F0F0F0F', pytest.raises(ValidationError, match=r"unsupported color format:"), []),
    ],
)
def test_hex_color_to_raw_for_grayscale(color_hex, exception, expected):
    # expect
    with exception:
        assert hex_color_to_raw(8, color_hex) == expected
