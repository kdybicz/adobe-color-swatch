from __future__ import annotations

from contextlib import nullcontext as does_not_raise
from pathlib import Path
from unittest import mock

import pytest

from swatch.swatch import __validate_color_space
from swatch.swatch import ColorSpace
from swatch.swatch import HexColor
from swatch.swatch import load_aco_file
from swatch.swatch import load_csv_file
from swatch.swatch import map_to_hex_color
from swatch.swatch import map_to_raw_color
from swatch.swatch import RawColor
from swatch.swatch import ValidationError


@pytest.mark.parametrize(
    'color_space,expected',
    [
        (ColorSpace.RGB, does_not_raise()),
        (ColorSpace.HSB, does_not_raise()),
        (ColorSpace.CMYK, does_not_raise()),
        (
            ColorSpace.PANTONE, pytest.raises(
                ValidationError, match='unsupported color space: Pantone matching system',
            ),
        ),
        (
            ColorSpace.FOCOLTONE, pytest.raises(
                ValidationError, match='unsupported color space: Focoltone colour system',
            ),
        ),
        (
            ColorSpace.TRUMATCH, pytest.raises(
                ValidationError, match='unsupported color space: Trumatch color',
            ),
        ),
        (
            ColorSpace.TOYO, pytest.raises(
                ValidationError, match='unsupported color space: Toyo 88 colorfinder 1050',
            ),
        ),
        (
            ColorSpace.LAB, pytest.raises(
                ValidationError, match='unsupported color space: Lab',
            ),
        ),
        (ColorSpace.GRAYSCALE, does_not_raise()),
        (
            ColorSpace.HKS, pytest.raises(
                ValidationError, match='unsupported color space: HKS colors',
            ),
        ),
    ],
)
def test_validate_color_space(color_space, expected):
    # expect
    with expected:
        __validate_color_space(color_space)


@pytest.mark.parametrize(
    'color_space,expected',
    [
        (ColorSpace.RGB, does_not_raise()),
        (ColorSpace.HSB, does_not_raise()),
        (ColorSpace.CMYK, does_not_raise()),
        (
            ColorSpace.PANTONE, pytest.raises(
                ValidationError, match='unsupported color space: Pantone matching system',
            ),
        ),
        (
            ColorSpace.FOCOLTONE, pytest.raises(
                ValidationError, match='unsupported color space: Focoltone colour system',
            ),
        ),
        (
            ColorSpace.TRUMATCH, pytest.raises(
                ValidationError, match='unsupported color space: Trumatch color',
            ),
        ),
        (
            ColorSpace.TOYO, pytest.raises(
                ValidationError, match='unsupported color space: Toyo 88 colorfinder 1050',
            ),
        ),
        (
            ColorSpace.LAB, pytest.raises(
                ValidationError, match='unsupported color space: Lab',
            ),
        ),
        (ColorSpace.GRAYSCALE, does_not_raise()),
        (
            ColorSpace.HKS, pytest.raises(
                ValidationError, match='unsupported color space: HKS colors',
            ),
        ),
    ],
)
def test_map_to_hex_color_with_validation(color_space, expected):
    # expect
    with expected:
        map_to_hex_color('color', color_space, 10000)


@pytest.mark.parametrize(
    'component_1,component_2,component_3,component_4',
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
def test_map_to_hex_color_for_rgb_invalid_values(
    component_1, component_2, component_3, component_4,
):
    # expect
    with pytest.raises(ValidationError, match=r'invalid RGB value:'):
        map_to_hex_color(
            'color',
            ColorSpace.RGB,
            component_1,
            component_2,
            component_3,
            component_4,
        )


@pytest.mark.parametrize(
    'component_1,component_2,component_3,component_4',
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
def test_map_to_hex_color_for_hsb_invalid_values(
    component_1, component_2, component_3, component_4,
):
    # expect
    with pytest.raises(ValidationError, match=r'invalid HSB value:'):
        map_to_hex_color(
            'color',
            ColorSpace.HSB,
            component_1,
            component_2,
            component_3,
            component_4,
        )


@pytest.mark.parametrize(
    'component_1,component_2,component_3,component_4',
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
def test_map_to_hex_color_for_cmyk_invalid_values(
    component_1, component_2, component_3, component_4,
):
    # expect
    with pytest.raises(ValidationError, match=r'invalid CMYK value:'):
        map_to_hex_color(
            'color',
            ColorSpace.CMYK,
            component_1,
            component_2,
            component_3,
            component_4,
        )


@pytest.mark.parametrize(
    'component_1,component_2,component_3,component_4',
    [
        (-1, 0, 0, 0),
        (10001, 0, 0, 0),
        (65536, 0, 0, 0),
    ],
)
def test_map_to_hex_color_for_grayscale_invalid_values(
    component_1, component_2, component_3, component_4,
):
    # expect
    with pytest.raises(ValidationError, match=r'invalid Grayscale value:'):
        map_to_hex_color(
            'color',
            ColorSpace.GRAYSCALE,
            component_1,
            component_2,
            component_3,
            component_4,
        )


@pytest.mark.parametrize(
    'color_space,component_1,component_2,component_3,component_4,expected',
    [
        (ColorSpace.RGB, 65535, 0, 0, 0, '#FFFF00000000'),
        (ColorSpace.HSB, 0, 65535, 65535, 0, '#0000FFFFFFFF'),
        (ColorSpace.CMYK, 0, 65535, 65535, 65535, '#0000FFFFFFFFFFFF'),
        (ColorSpace.GRAYSCALE, 10000, 0, 0, 0, '#2710'),
    ],
)
def test_map_to_hex_color_for_supported_color_space(
    color_space, component_1, component_2, component_3, component_4, expected,
):
    # expect
    assert map_to_hex_color(
        'color',
        color_space,
        component_1,
        component_2,
        component_3,
        component_4,
    ) == HexColor('color', color_space, expected)


@pytest.mark.parametrize(
    'color_hex,exception,expected',
    [
        ('#000000', does_not_raise(), [0, 0, 0, 0]),
        ('#0F0F0F', does_not_raise(), [3855, 3855, 3855, 0]),
        ('#FFFFFF', does_not_raise(), [65535, 65535, 65535, 0]),
        ('000000000000', does_not_raise(), [0, 0, 0, 0]),
        ('0F0F0F0F0F0F', does_not_raise(), [3855, 3855, 3855, 0]),
        ('FFFFFFFFFFFF', does_not_raise(), [65535, 65535, 65535, 0]),
        (
            '# ', pytest.raises(
                ValidationError, match=r'unsupported color format:',
            ), [],
        ),
        (
            'F0F', pytest.raises(
                ValidationError, match=r'unsupported color format:',
            ), [],
        ),
        (
            'F0F0F', pytest.raises(
                ValidationError, match=r'unsupported color format:',
            ), [],
        ),
        (
            'F0F0F0F0F0F', pytest.raises(
                ValidationError, match=r'unsupported color format:',
            ), [],
        ),
        (
            'F0F0F0F0F0F0F', pytest.raises(
                ValidationError, match=r'unsupported color format:',
            ), [],
        ),
    ],
)
def test_map_to_raw_color_for_rgb(color_hex, exception, expected):
    # expect
    with exception:
        assert map_to_raw_color('color', ColorSpace.RGB, color_hex) == RawColor('color', ColorSpace.RGB, *expected)


@pytest.mark.parametrize(
    'color_hex,exception,expected',
    [
        ('#000000', does_not_raise(), [0, 0, 0, 0]),
        ('#0F0F0F', does_not_raise(), [3855, 3855, 3855, 0]),
        ('#FFFFFF', does_not_raise(), [65535, 65535, 65535, 0]),
        ('000000000000', does_not_raise(), [0, 0, 0, 0]),
        ('0F0F0F0F0F0F', does_not_raise(), [3855, 3855, 3855, 0]),
        ('FFFFFFFFFFFF', does_not_raise(), [65535, 65535, 65535, 0]),
        (
            '# ', pytest.raises(
                ValidationError, match=r'unsupported color format:',
            ), [],
        ),
        (
            'F0F', pytest.raises(
                ValidationError, match=r'unsupported color format:',
            ), [],
        ),
        (
            'F0F0F', pytest.raises(
                ValidationError, match=r'unsupported color format:',
            ), [],
        ),
        (
            'F0F0F0F0F0F', pytest.raises(
                ValidationError, match=r'unsupported color format:',
            ), [],
        ),
        (
            'F0F0F0F0F0F0F', pytest.raises(
                ValidationError, match=r'unsupported color format:',
            ), [],
        ),
    ],
)
def test_map_to_raw_color_for_hsb(color_hex, exception, expected):
    # expect
    with exception:
        assert map_to_raw_color('color', ColorSpace.HSB, color_hex) == RawColor('color', ColorSpace.HSB, *expected)


@pytest.mark.parametrize(
    'color_hex,exception,expected',
    [
        ('#00000000', does_not_raise(), [0, 0, 0, 0]),
        ('#0F0F0F0F', does_not_raise(), [3855, 3855, 3855, 3855]),
        ('#FFFFFFFF', does_not_raise(), [65535, 65535, 65535, 65535]),
        ('0000000000000000', does_not_raise(), [0, 0, 0, 0]),
        ('0F0F0F0F0F0F0F0F', does_not_raise(), [3855, 3855, 3855, 3855]),
        ('FFFFFFFFFFFFFFFF', does_not_raise(), [65535, 65535, 65535, 65535]),
        (
            '# ', pytest.raises(
                ValidationError, match=r'unsupported color format:',
            ), [],
        ),
        (
            'F0F0F0F', pytest.raises(
                ValidationError, match=r'unsupported color format:',
            ), [],
        ),
        (
            'F0F0F0F0F', pytest.raises(
                ValidationError, match=r'unsupported color format:',
            ), [],
        ),
        (
            'F0F0F0F0F0F0F0F', pytest.raises(
                ValidationError, match=r'unsupported color format:',
            ), [],
        ),
        (
            'F0F0F0F0F0F0F0F0F', pytest.raises(
                ValidationError, match=r'unsupported color format:',
            ), [],
        ),
    ],
)
def test_map_to_raw_color_for_cmyk(color_hex, exception, expected):
    # expect
    with exception:
        assert map_to_raw_color('color', ColorSpace.CMYK, color_hex) == RawColor('color', ColorSpace.CMYK, *expected)


@pytest.mark.parametrize(
    'color_hex,exception,expected',
    [
        ('#00', does_not_raise(), [0, 0, 0, 0]),
        ('#0F', does_not_raise(), [3855, 0, 0, 0]),
        ('#26', does_not_raise(), [9766, 0, 0, 0]),
        ('0000', does_not_raise(), [0, 0, 0, 0]),
        ('0F0F', does_not_raise(), [3855, 0, 0, 0]),
        ('2710', does_not_raise(), [10000, 0, 0, 0]),
        (
            '#2711', pytest.raises(
                ValidationError, match=r'invalid grayscale value: 2711',
            ), [],
        ),
        (
            '# ', pytest.raises(
                ValidationError, match=r'unsupported color format:',
            ), [],
        ),
        (
            'F0F0F0F', pytest.raises(
                ValidationError, match=r'unsupported color format:',
            ), [],
        ),
        (
            'F0F0F0F0F', pytest.raises(
                ValidationError, match=r'unsupported color format:',
            ), [],
        ),
        (
            'F0F0F0F0F0F0F0F', pytest.raises(
                ValidationError, match=r'unsupported color format:',
            ), [],
        ),
        (
            'F0F0F0F0F0F0F0F0F', pytest.raises(
                ValidationError, match=r'unsupported color format:',
            ), [],
        ),
    ],
)
def test_map_to_raw_color_for_grayscale(color_hex, exception, expected):
    # expect
    with exception:
        assert map_to_raw_color('color', ColorSpace.GRAYSCALE, color_hex) == RawColor('color', ColorSpace.GRAYSCALE, *expected)


@pytest.mark.parametrize(
    'color_space,expected',
    [
        (
            ColorSpace.PANTONE, pytest.raises(
                ValidationError, match='unsupported color space: Pantone matching system',
            ),
        ),
        (
            ColorSpace.FOCOLTONE, pytest.raises(
                ValidationError, match='unsupported color space: Focoltone colour system',
            ),
        ),
        (
            ColorSpace.TRUMATCH, pytest.raises(
                ValidationError, match='unsupported color space: Trumatch color',
            ),
        ),
        (
            ColorSpace.TOYO, pytest.raises(
                ValidationError, match='unsupported color space: Toyo 88 colorfinder 1050',
            ),
        ),
        (
            ColorSpace.LAB, pytest.raises(
                ValidationError, match='unsupported color space: Lab',
            ),
        ),
        (
            ColorSpace.HKS, pytest.raises(
                ValidationError, match='unsupported color space: HKS colors',
            ),
        ),
    ],
)
def test_map_to_raw_color_for_unsupported(color_space, expected):
    # expect
    with expected:
        map_to_raw_color('color', color_space, '#000000')


def test_load_aco_file_succeed():
    # given
    base_path = Path(__file__).parent
    file_path = (base_path / '../examples/utf.aco').resolve()

    # when
    with open(file_path, 'rb') as file:
        color_data = load_aco_file(file)
    # then
    assert color_data == [
        HexColor('Zażółć gęślą jaźń', ColorSpace.HSB, '#2A2AA8A8E3E3'),
        HexColor('チェリー', ColorSpace.HSB, '#F2F2EAEAAFAF'),
        HexColor('a', ColorSpace.HSB, '#F2F20000FFFF'),
    ]


def test_load_aco_file_does_not_fail_on_invalid_file():
    # given
    base_path = Path(__file__).parent
    file_path = (base_path / '../examples/utf.csv').resolve()

    # when
    with open(file_path, 'rb') as file:
        color_data = load_aco_file(file)
    # then
    assert not color_data


def test_load_csv_file_succeed():
    # given
    base_path = Path(__file__).parent
    file_path = (base_path / '../examples/utf.csv').resolve()

    # when
    with open(file_path, encoding='utf-8') as file:
        color_data = load_csv_file(file)
    # then
    assert color_data == [
        RawColor('Zażółć gęślą jaźń', ColorSpace.HSB, 10794, 43176, 58339, 0),
        RawColor('チェリー', ColorSpace.HSB, 62194, 60138, 44975, 0),
        RawColor('a', ColorSpace.HSB, 62194, 0, 65535, 0),
    ]


@mock.patch('builtins.open', create=True)
def test_load_csv_file_does_not_fail_on_invalid_file(file):
    # expect
    assert not load_csv_file(file)
