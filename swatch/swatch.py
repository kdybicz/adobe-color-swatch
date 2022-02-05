"""
Adobe Color Swatch generator and parser
"""
from __future__ import annotations

import logging
import sys
import traceback
from enum import Enum
from enum import unique
from typing import BinaryIO
from typing import NamedTuple
from typing import TextIO

log = logging.getLogger('__name__')

message_handler = logging.StreamHandler(sys.stdout)
message_handler.setLevel(logging.DEBUG)
message_handler.addFilter(lambda record: record.levelno <= logging.INFO)
log.addHandler(message_handler)

error_handler = logging.StreamHandler(sys.stderr)
error_handler.setLevel(logging.WARNING)
log.addHandler(error_handler)


@unique
class ColorSpace(Enum):
    """Adobe Color Swatch - Color Space Ids."""
    RGB = (0, 'RGB', True)
    HSB = (1, 'HSB', True)
    CMYK = (2, 'CMYK', True)
    PANTONE = (3, 'Pantone matching system', False)
    FOCOLTONE = (4, 'Focoltone colour system', False)
    TRUMATCH = (5, 'Trumatch color', False)
    TOYO = (6, 'Toyo 88 colorfinder 1050', False)
    LAB = (7, 'Lab', False)
    GRAYSCALE = (8, 'Grayscale', True)
    HKS = (10, 'HKS colors', False)

    def __new__(cls, *args):  # type: ignore
        obj = object.__new__(cls)
        obj._value_ = args[0]
        return obj

    def __init__(
        self, _: int,
        label: str | None = None,
        supported: bool | None = False,
    ):
        self.label = label
        self.supported = supported

    def __str__(self) -> str:
        return self.label if self.label is not None else 'unknown'


class HexColor(NamedTuple):
    name: str
    color_space: ColorSpace
    color_hex: str


class RawColor(NamedTuple):
    name: str
    color_space: ColorSpace
    component_1: int = 0
    component_2: int = 0
    component_3: int = 0
    component_4: int = 0


class ValidationError(Exception):
    """Error raised in case of any data validation problems"""

    def __init__(self, message: str):
        super().__init__()
        self.message = message

    def __str__(self) -> str:
        return repr(self.message)


def validate_color_space(color_space: ColorSpace) -> None:
    """Validate provided `color_space`.

    Args:
        color_space: color space to be checked.

    Raises:
        ValidationError: Is raised if provided color space is not supported.
    """
    if color_space.supported is False:
        raise ValidationError(f'unsupported color space: {str(color_space)}')


def map_to_hex_color(
    name: str,
    color_space: ColorSpace,
    component_1: int = 0,
    component_2: int = 0,
    component_3: int = 0,
    component_4: int = 0,
) -> HexColor:
    """Combines provided color data into a `HexColor` representation
    of that color.

    ColorSpace.RGB
        The first three components represent red, green and blue. Fourth should
        be 0. They are full unsigned 16-bit values as in Apple's RGBColor data
        structure.
        Pure red = 65535, 0, 0.

    ColorSpace.HSB
        The first three components represent hue, saturation and brightness.
        They are full unsigned 16-bit values as in Apple's HSVColor data
        structure.
        Pure red = 0, 65535, 65535.

    ColorSpace.CMYK
        The four components represent cyan, magenta, yellow and black. They are
        full unsigned 16-bit values.
        0 = 100% ink. For example, pure cyan = 0, 65535, 65535, 65535.

    ColorSpace.GRAYSCALE
        The first component represent the gray value, from 0...10000.

    Args:
        name: name of the color
        color_space: color space if to be checked.
        component_1: first channel of the color for specified color space.
        component_2: second channel of the color for specified color space.
        component_3: third channel of the color for specified color space.
        component_4: fourth channel of the color for specified color space.

    Returns:
        A `HexColor` representation of the color.

    Raises:
        ValidationError: Is raised if color components exceed expected values
        for provided `color_space`.
    """
    if color_space is ColorSpace.RGB:
        if not 0 <= component_1 <= 65535 or not 0 <= component_2 <= 65535 or \
                not 0 <= component_3 <= 65535 or component_4 != 0:
            raise ValidationError(
                f'invalid RGB value: {component_1}, {component_2}, {component_3}, {component_4}',  # noqa: E501
            )

        return HexColor(
            name,
            color_space,
            f'#{component_1:04X}{component_2:04X}{component_3:04X}',
        )
    if color_space is ColorSpace.HSB:
        if not 0 <= component_1 <= 65535 or not 0 <= component_2 <= 65535 or \
                not 0 <= component_3 <= 65535 or component_4 != 0:
            raise ValidationError(
                f'invalid HSB value: {component_1}, {component_2}, {component_3}, {component_4}',  # noqa: E501
            )

        return HexColor(
            name,
            color_space,
            f'#{component_1:04X}{component_2:04X}{component_3:04X}',
        )
    if color_space is ColorSpace.CMYK:
        if not 0 <= component_1 <= 65535 or not 0 <= component_2 <= 65535 or \
                not 0 <= component_3 <= 65535 or not 0 <= component_4 <= 65535:
            raise ValidationError(
                f'invalid CMYK value: {component_1}, {component_2}, {component_3}, {component_4}',  # noqa: E501
            )

        return HexColor(
            name,
            color_space,
            f'#{component_1:04X}{component_2:04X}{component_3:04X}{component_4:04X}',  # noqa: E501
        )
    if color_space is ColorSpace.GRAYSCALE:
        if not 0 <= component_1 <= 10000 or component_2 != 0 or \
                component_3 != 0 or component_4 != 0:
            raise ValidationError(
                f'invalid Grayscale value: {component_1}, {component_2}, {component_3}, {component_4}',  # noqa: E501
            )

        return HexColor(
            name,
            color_space,
            f'#{component_1:04X}',
        )

    raise ValidationError(f'unsupported color space: {str(color_space)}')


def map_to_raw_color(
    name: str,
    color_space: ColorSpace,
    color_hex: str = '',
) -> RawColor:
    """Parses provided HEX string representation of a color
    into four element list of color components.

    ColorSpace.RGB
        Supports both 8-bit and 16-bit per color channel, expects three
        channels only.
        Leading `#` is optional. Pure red = #FFFF00000000.

    ColorSpace.HSB
        Supports both 8-bit and 16-bit per color channel, expects three
        channels only.
        Leading `#` is optional. Pure red = #00FFFF.

    ColorSpace.CMYK
        Supports both 8-bit and 16-bit per color channel, expects four
        channels.
        Leading `#` is optional. Pure cyan = 0000FFFFFFFFFFFF.

    ColorSpace.GRAYSCALE
        Supports both 8-bit and 16-bit for grey value, expects only one
        channel.
        Leading `#` is optional. Pure black = #2710.

    Args:
        name: name of the color
        color_space: color space if to be checked.
        color_hex: HEX string representation of a color.

    Returns:
        A `RawColor` representation of a color.

    Raises:
        ValidationError: Is raised if color components exceed expected values
            for provided `color_space`.
    """
    color_hex = color_hex.lstrip('#')

    if len(color_hex.strip()) == 0:
        raise ValidationError(f'unsupported color format: {color_hex}')

    if color_space in [ColorSpace.RGB, ColorSpace.HSB]:
        if len(color_hex) == 6:
            # * 257 to convert to 32-bit color space
            return RawColor(
                name,
                color_space,
                int(color_hex[0:2], base=16) * 257,
                int(color_hex[2:4], base=16) * 257,
                int(color_hex[4:6], base=16) * 257,
            )

        if len(color_hex) == 12:
            return RawColor(
                name,
                color_space,
                int(color_hex[0:4], base=16),
                int(color_hex[4:8], base=16),
                int(color_hex[8:12], base=16),
            )

        raise ValidationError(f'unsupported color format: {color_hex}')

    if color_space is ColorSpace.CMYK:
        if len(color_hex) == 8:
            # * 257 to convert to 32-bit color space
            return RawColor(
                name,
                color_space,
                int(color_hex[0:2], base=16) * 257,
                int(color_hex[2:4], base=16) * 257,
                int(color_hex[4:6], base=16) * 257,
                int(color_hex[6:8], base=16) * 257,
            )

        if len(color_hex) == 16:
            return RawColor(
                name,
                color_space,
                int(color_hex[0:4], base=16),
                int(color_hex[4:8], base=16),
                int(color_hex[8:12], base=16),
                int(color_hex[12:16], base=16),
            )

        raise ValidationError(f'unsupported color format: {color_hex}')

    if color_space is ColorSpace.GRAYSCALE:
        if len(color_hex) == 2:
            # * 257 to convert to 32-bit color space
            gray = int(color_hex[0:2], base=16) * 257
        elif len(color_hex) == 4:
            gray = int(color_hex[0:4], base=16)
        else:
            raise ValidationError(f'unsupported color format: {color_hex}')

        if gray > 10000:
            raise ValidationError(f'invalid grayscale value: {color_hex}')

        return RawColor(
            name,
            color_space,
            gray,
        )

    raise ValidationError(f'unsupported color space: {str(color_space)}')


def load_aco_file(file: BinaryIO) -> list[HexColor]:
    """Parses the `.aco` file and returns a list of lists, were each of them
    contains the name, color space id and a HEX string representation of the
    colors extracted from the Color Swatch file.

    Args:
        file: handle to the `.aco` file to be parsed.

    Returns:
        A list of `HexColor`s, were each of them contains the name, color space
        and a HEX string representation of the colors extracted from the
        Color Swatch file.

    Raises:
        ValidationError: Is raised if parsed file contains unexpected data.
    """
    colors = []

    try:
        # Version 1
        log.debug('\nParsing version 1 section')

        version_byte = int.from_bytes(file.read(2), 'big')
        if version_byte != 1:
            raise ValidationError('Version byte should be 1')

        color_count = int.from_bytes(file.read(2), 'big')
        log.debug('Colors found: %d', color_count)

        for idx in range(color_count):
            color_space = ColorSpace(int.from_bytes(file.read(2), 'big'))
            validate_color_space(color_space)

            component_1 = int.from_bytes(file.read(2), 'big')
            component_2 = int.from_bytes(file.read(2), 'big')
            component_3 = int.from_bytes(file.read(2), 'big')
            component_4 = int.from_bytes(file.read(2), 'big')

            log.debug(' - ID: %d', idx)
            log.debug('   Color space: %s', color_space)
            log.debug('   Components: %d %d %d %d', component_1, component_2, component_3, component_4)  # noqa: E501

        # Version 2
        log.debug('\nParsing version 2 section')

        version_byte = int.from_bytes(file.read(2), 'big')
        if version_byte != 2:
            raise ValidationError('Version byte should be 2')

        color_count = int.from_bytes(file.read(2), 'big')
        log.debug('Colors found: %d', color_count)

        for idx in range(color_count):
            color_space = ColorSpace(int.from_bytes(file.read(2), 'big'))
            validate_color_space(color_space)

            component_1 = int.from_bytes(file.read(2), 'big')
            component_2 = int.from_bytes(file.read(2), 'big')
            component_3 = int.from_bytes(file.read(2), 'big')
            component_4 = int.from_bytes(file.read(2), 'big')

            name_length = int.from_bytes(file.read(4), 'big')
            # - 2 to omit termination character
            name_bytes = file.read(name_length * 2 - 2)
            name = name_bytes.decode('utf-16-be')

            # droping the string termination character
            file.read(2)

            hex_color = map_to_hex_color(
                name,
                color_space,
                component_1,
                component_2,
                component_3,
                component_4,
            )

            log.debug(' - ID: %d', idx)
            log.debug('   Color name: %s', hex_color.name)
            log.debug('   Color space: %s', hex_color.color_space)
            log.debug('   Color: %s', hex_color.color_hex)

            colors.append(hex_color)

    except ValidationError as err:
        log.error('\nError while parsing .aco file: %s', err.message)

    finally:
        file.close()

    return colors


def save_csv_file(colors_data: list[HexColor], file: TextIO) -> None:
    """Saves provided color data into a `.csv` file.

    Args:
        colors_data: list of `HexColor`s, were each of them contains the name,
            color space and a HEX string representation of a color.
        file: handle to the `.csv` file to be saved.
    """
    try:
        file.write('name,space_id,color\n')

        for color_data in colors_data:
            file.write(color_data.name)
            file.write(',')

            color_space_id = str(color_data.color_space.value)
            file.write(color_space_id)
            file.write(',')

            file.write(color_data.color_hex)
            file.write('\n')

    except OSError:
        log.error('\nError while saving .csv file')
        log.error(traceback.format_exc())

    finally:
        file.close()


def convert_aco_file_to_csv(
    input_file: BinaryIO,
    output_file: TextIO,
) -> None:
    """Extracts data from `.aco` file and stores them in the `.csv` file.

    Args:
        input_file: handle to the `.aco` file to be parsed.
        output_file: handle to the `.csv` file to be saved.
    """
    log.info('\nExtracting "%s" to "%s"', input_file.name, output_file.name)

    colors_data = load_aco_file(input_file)

    save_csv_file(colors_data, output_file)


def load_csv_file(file: TextIO) -> list[RawColor]:
    """Parses the `.csv` file and returns a list `RawColor`s, were each of them
    contains the name, color space and four color components.

    Args:
        file: handle to the `.csv` file to be parsed.

    Returns:
        A list of `RawColor`s, were each of them contains the name, color space
        and four color components.

    Raises:
        ValidationError: Is raised if parsed file contains unexpected data.
    """
    colors = []

    try:
        # Parse
        log.debug('\nParsing file')

        header = file.readline()
        if header != 'name,space_id,color\n':
            raise ValidationError('Invalid file header')

        color_lines = file.readlines()

        log.debug('Colors found: %d', len(color_lines))

        for color_line in color_lines:
            line_elements = color_line.split(',')
            if len(line_elements) != 3:
                raise ValidationError('Color line should contain 3 elements')

            name = line_elements[0]
            if len(name.strip()) == 0:
                raise ValidationError('Color name must be provided')

            color_space_id = int(line_elements[1])
            color_space = ColorSpace(color_space_id)

            color_hex = line_elements[2].strip()

            log.debug(' - Color name: %s', name)
            log.debug('   Color space: %s', color_space)
            log.debug('   Color: %s', color_hex)

            raw_color = map_to_raw_color(name, color_space, color_hex)

            colors.append(raw_color)

    except ValidationError as err:
        log.info('\nError while parsing .csv file: %s', err.message)

    finally:
        file.close()

    return colors


def save_aco_file(colors_data: list[RawColor], file: BinaryIO) -> None:
    """Saves provided color data into a `.aco` file.

    Args:
        colors_data: list of `RawColor`s, were each of them contains the name,
            color space and four color components.
        file: handle to the `.aco` file to be saved.
    """
    try:
        # Version 1
        version = 1
        file.write(version.to_bytes(2, 'big'))

        color_count = len(colors_data)
        file.write(color_count.to_bytes(2, 'big'))

        for color_data in colors_data:
            color_space_id = color_data.color_space.value
            file.write(color_space_id.to_bytes(2, 'big'))

            file.write(color_data.component_1.to_bytes(2, 'big'))
            file.write(color_data.component_2.to_bytes(2, 'big'))
            file.write(color_data.component_3.to_bytes(2, 'big'))
            file.write(color_data.component_4.to_bytes(2, 'big'))

        # Version 2
        version = 2
        file.write(version.to_bytes(2, 'big'))

        color_count = len(colors_data)
        file.write(color_count.to_bytes(2, 'big'))

        for color_data in colors_data:
            color_space_id = color_data.color_space.value
            file.write(color_space_id.to_bytes(2, 'big'))

            file.write(color_data.component_1.to_bytes(2, 'big'))
            file.write(color_data.component_2.to_bytes(2, 'big'))
            file.write(color_data.component_3.to_bytes(2, 'big'))
            file.write(color_data.component_4.to_bytes(2, 'big'))

            # + 1 is for termination character
            color_name_length = len(color_data.name) + 1
            file.write(color_name_length.to_bytes(4, 'big'))

            color_name_bytes = bytes(color_data.name, 'utf-16-be')
            file.write(color_name_bytes)

            termination_char = 0
            file.write(termination_char.to_bytes(2, 'big'))

    except OSError:
        log.error('\nError while saving .aco file')
        log.error(traceback.format_exc())

    finally:
        file.close()


def convert_csv_file_to_aco(
    input_file: TextIO,
    output_file: BinaryIO,
) -> None:
    """Generating `.aco` file based on the data from the `.csv` file.

    Args:
        input_file: handle to the `.csv` file to be parsed.
        output_file: handle to the `.aco` file to be saved.
    """
    log.info('\nGenerating "%s" to "%s"', input_file.name, output_file.name)

    colors_data = load_csv_file(input_file)

    save_aco_file(colors_data, output_file)
