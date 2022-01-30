"""
Adobe Color Swatch generator and parser
"""
from enum import Enum, unique
from io import BufferedReader, BufferedWriter, TextIOWrapper
import logging
import sys
import traceback
from typing import List, Optional

log = logging.getLogger("__name__")

message_handler = logging.StreamHandler(sys.stdout)
message_handler.setLevel(logging.DEBUG)
message_handler.addFilter(lambda record: record.levelno <= logging.INFO)
log.addHandler(message_handler)

error_handler = logging.StreamHandler(sys.stderr)
error_handler.setLevel(logging.WARNING)
log.addHandler(error_handler)
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


def raw_color_to_hex(
    color_space: ColorSpace,
    component_1: int,
    component_2: int,
    component_3: int,
    component_4: int
) -> str:
    """Combines provided color data in a HEX string representation of that color.

    RGB
        The first three components represent red, green and blue. Fourth should be 0.
        They are full unsigned 16-bit values as in Apple's RGBColor data structure.
        Pure red = 65535, 0, 0.

    HSB
        The first three components represent hue, saturation and brightness.
        They are full unsigned 16-bit values as in Apple's HSVColor data structure.
        Pure red = 0, 65535, 65535.

    CMYK
        The four components represent cyan, magenta, yellow and black. They are full
        unsigned 16-bit values.
        0 = 100% ink. For example, pure cyan = 0, 65535, 65535, 65535.

    Grayscale
        The first component represent the gray value, from 0...10000.

    Args:
        color_space: color space if to be checked.
        component_1: first channel of the color for specified color space.
        component_2: second channel of the color for specified color space.
        component_3: third channel of the color for specified color space.
        component_4: fourth channel of the color for specified color space.

    Returns:
        A HEX string representation of the color.

    Raises:
        ValidationError: Is raised if color components exceed expected values for
            provided `color_space`.
    """
    if color_space is ColorSpace.RGB:
        if not 0 <= component_1 <= 65535 or not 0 <= component_2 <= 65535 or \
            not 0 <= component_3 <= 65535 or component_4 != 0:
            raise ValidationError(
                f'invalid RGB value: {component_1}, {component_2}, {component_3}, {component_4}' # pylint: disable=line-too-long
            )

        return f'#{component_1:04X}{component_2:04X}{component_3:04X}'
    if color_space is ColorSpace.HSB:
        if not 0 <= component_1 <= 65535 or not 0 <= component_2 <= 65535 or \
            not 0 <= component_3 <= 65535 or component_4 != 0:
            raise ValidationError(
                f'invalid HSB value: {component_1}, {component_2}, {component_3}, {component_4}' # pylint: disable=line-too-long
            )

        return f'#{component_1:04X}{component_2:04X}{component_3:04X}'
    if color_space is ColorSpace.CMYK:
        if not 0 <= component_1 <= 65535 or not 0 <= component_2 <= 65535 or \
            not 0 <= component_3 <= 65535 or not 0 <= component_4 <= 65535:
            raise ValidationError(
                f'invalid CMYK value: {component_1}, {component_2}, {component_3}, {component_4}' # pylint: disable=line-too-long
            )

        return f'#{component_1:04X}{component_2:04X}{component_3:04X}{component_4:04X}'
    if color_space is ColorSpace.GRAYSCALE:
        if not 0 <= component_1 <= 10000 or component_2 != 0 or \
            component_3 != 0 or component_4 != 0:
            raise ValidationError(
                f'invalid Grayscale value: {component_1}, {component_2}, {component_3}, {component_4}' # pylint: disable=line-too-long
            )

        return f'#{component_1:04X}'

    raise ValidationError(f'unsupported color space: {str(color_space)}')

def hex_color_to_raw(
    color_space: ColorSpace,
    color_hex: str = ""
) -> List[int]:
    """Parses provided HEX string representation of a color
    into four element list of color components.

    RGB
        Supports both 8-bit and 16-bit per color channel, expects three channels only.
        Leading `#` is optional. Pure red = #FFFF00000000.

    HSB
        Supports both 8-bit and 16-bit per color channel, expects three channels only.
        Leading `#` is optional. Pure red = #00FFFF.

    CMYK
        Supports both 8-bit and 16-bit per color channel, expects four channels.
        Leading `#` is optional. Pure cyan = 0000FFFFFFFFFFFF.

    Grayscale
        Supports both 8-bit and 16-bit for grey value, expects only one channel.
        Leading `#` is optional. Pure black = #2710.

    Args:
        color_space: color space if to be checked.
        color_hex: HEX string representation of a color.

    Returns:
        A four element list of color components.

    Raises:
        ValidationError: Is raised if color components exceed expected values for
            provided `color_space`.
    """
    color_hex = color_hex.lstrip('#')

    if len(color_hex.strip()) == 0:
        raise ValidationError(f'unsupported color format: {color_hex}')

    if color_space in [ColorSpace.RGB, ColorSpace.HSB]:
        if len(color_hex) == 6:
            # * 257 to convert to 32-bit color space
            return [
                int(color_hex[0:2], base=16) * 257,
                int(color_hex[2:4], base=16) * 257,
                int(color_hex[4:6], base=16) * 257,
                0
            ]

        if len(color_hex) == 12:
            return [
                int(color_hex[0:4], base=16),
                int(color_hex[4:8], base=16),
                int(color_hex[8:12], base=16),
                0
            ]

        raise ValidationError(f'unsupported color format: {color_hex}')

    if color_space is ColorSpace.CMYK:
        if len(color_hex) == 8:
            # * 257 to convert to 32-bit color space
            return [
                int(color_hex[0:2], base=16) * 257,
                int(color_hex[2:4], base=16) * 257,
                int(color_hex[4:6], base=16) * 257,
                int(color_hex[6:8], base=16) * 257
            ]

        if len(color_hex) == 16:
            return [
                int(color_hex[0:4], base=16),
                int(color_hex[4:8], base=16),
                int(color_hex[8:12], base=16),
                int(color_hex[12:16], base=16)
            ]

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

        return [
            gray,
            0,
            0,
            0
        ]

    raise ValidationError(f'unsupported color space: {str(color_space)}')

def parse_aco(file: BufferedReader) -> List: # pylint: disable=too-many-locals)
    """Parses the `.aco` file and returns a list of lists, were each of them contains the name,
    color space id and a HEX string representation of the colors extracted from the Color Swatch
    file.

    Args:
        file: handle to the `.aco` file to be parsed.

    Returns:
        A list of lists, were each of them contains the name, color space id and a HEX string
        representation of the colors extracted from the Color Swatch file.

    Raises:
        ValidationError: Is raised if parsed file contains unexpected data.
    """
    colors = []

    try:
        # Version 1
        log.debug("\nParsing version 1 section")

        version_byte = int.from_bytes(file.read(2), "big")
        if version_byte != 1:
            raise ValidationError("Version byte should be 1")

        color_count = int.from_bytes(file.read(2), "big")
        log.debug("Colors found: %d", color_count)

        for idx in range(color_count):
            color_space = ColorSpace(int.from_bytes(file.read(2), "big"))
            validate_color_space(color_space)

            component_1 = int.from_bytes(file.read(2), "big")
            component_2 = int.from_bytes(file.read(2), "big")
            component_3 = int.from_bytes(file.read(2), "big")
            component_4 = int.from_bytes(file.read(2), "big")

            log.debug(" - ID: %d", idx)
            log.debug("   Color space: %s", color_space)
            log.debug(
            "   Components: %d %d %d %d", component_1, component_2, component_3, component_4
            )

        # Version 2
        log.debug("\nParsing version 2 section")

        version_byte = int.from_bytes(file.read(2), "big")
        if version_byte != 2:
            raise ValidationError("Version byte should be 2")

        color_count = int.from_bytes(file.read(2), "big")
        log.debug("Colors found: %d", color_count)

        for idx in range(color_count):
            color_space = ColorSpace(int.from_bytes(file.read(2), "big"))
            validate_color_space(color_space)

            component_1 = int.from_bytes(file.read(2), "big")
            component_2 = int.from_bytes(file.read(2), "big")
            component_3 = int.from_bytes(file.read(2), "big")
            component_4 = int.from_bytes(file.read(2), "big")

            name_length = int.from_bytes(file.read(4), "big")
            name_bytes = file.read(name_length * 2 - 2) # - 2 to omit termination character
            name = name_bytes.decode("utf-16-be")

            # droping the string termination character
            file.read(2)

            color_hex = raw_color_to_hex(
                color_space, component_1, component_2, component_3, component_4
            )

            log.debug(" - ID: %d", idx)
            log.debug("   Color name: %s", name)
            log.debug("   Color space: %s", color_space)
            log.debug("   Color: %s", color_hex)

            colors.append([name, color_space, color_hex])

    except ValidationError as err:
        log.error("\nError while parsing .aco file: %s", err.message)

    finally:
        file.close()

    return colors

def save_csv(colors_data: List, file: TextIOWrapper) -> None:
    """Saves provided color data into a `.csv` file.

    Args:
        colors_data: list of lists, were each of them contains the name, color space id and
            a HEX string representation of a color.
        file: handle to the `.csv` file to be saved.
    """
    try:
        file.write("name,space_id,color")
        file.write("\n")

        for color_data in colors_data:
            name = color_data[0]
            file.write(name)
            file.write(",")

            color_space = color_data[1]
            color_space_id = str(color_space.value)
            file.write(color_space_id)
            file.write(",")

            color_hex = str(color_data[2])
            file.write(color_hex)
            file.write("\n")

    except OSError:
        log.error("\nError while saving .csv file")
        log.error(traceback.format_exc())

    finally:
        file.close()

def extract_aco(input_file: BufferedReader, output_file: TextIOWrapper) -> None:
    """Extracts data from `.aco` file and stores them in the `.csv` file.

    Args:
        input_file: handle to the `.aco` file to be parsed.
        output_file: handle to the `.csv` file to be saved.
    """
    log.info("\nExtracting \"%s\" to \"%s\"", input_file.name, output_file.name)

    colors_data = parse_aco(input_file)

    save_csv(colors_data, output_file)

def parse_csv(file: TextIOWrapper) -> List:
    """Parses the `.csv` file and returns a list of lists, were each of them contains the name,
    color space id and four color components.

    Args:
        file: handle to the `.csv` file to be parsed.

    Returns:
        A list of lists, were each of them contains the name, color space id and four color
        components.

    Raises:
        ValidationError: Is raised if parsed file contains unexpected data.
    """
    colors = []

    try:
        # Parse
        log.debug("\nParsing file")

        header = file.readline()
        if header != "name,space_id,color\n":
            raise ValidationError("Invalid file header")

        color_lines = file.readlines()

        log.debug("Colors found: %d", len(color_lines))

        for color_line in color_lines:
            line_elements = color_line.split(",")
            if len(line_elements) != 3:
                raise ValidationError("Color line should contain 3 elements")

            name = line_elements[0]
            if len(name.strip()) == 0:
                raise ValidationError("Color name must be provided")

            color_space_id = int(line_elements[1])
            color_space = ColorSpace(color_space_id)

            color_hex = line_elements[2].strip()

            log.debug(" - Color name: %s", name)
            log.debug("   Color space: %s", color_space)
            log.debug("   Color: %s", color_hex)

            color_components = hex_color_to_raw(color_space, color_hex)

            colors.append([
                name,
                color_space,
                color_components[0],
                color_components[1],
                color_components[2],
                color_components[3]
            ])

    except ValidationError as err:
        log.info("\nError while parsing .csv file: %s", err.message)

    finally:
        file.close()

    return colors

def save_aco(colors_data: List, file: BufferedWriter) -> None: # pylint: disable=too-many-locals)
    """Saves provided color data into a `.aco` file.

    Args:
        colors_data: list of lists, were each of them contains the name, color space id and four
        color components.
        file: handle to the `.aco` file to be saved.
    """
    try:
        # Version 1
        version = 1
        file.write(version.to_bytes(2, "big"))

        color_count = len(colors_data)
        file.write(color_count.to_bytes(2, "big"))

        for color_data in colors_data:
            color_space = color_data[1]
            color_space_id = color_space.value
            file.write(color_space_id.to_bytes(2, "big"))

            component_1 = color_data[2]
            file.write(component_1.to_bytes(2, "big"))
            component_2 = color_data[3]
            file.write(component_2.to_bytes(2, "big"))
            component_3 = color_data[4]
            file.write(component_3.to_bytes(2, "big"))
            component_4 = color_data[5]
            file.write(component_4.to_bytes(2, "big"))

        # Version 2
        version = 2
        file.write(version.to_bytes(2, "big"))

        color_count = len(colors_data)
        file.write(color_count.to_bytes(2, "big"))

        for color_data in colors_data:
            color_space = color_data[1]
            color_space_id = color_space.value
            file.write(color_space_id.to_bytes(2, "big"))

            component_1 = color_data[2]
            file.write(component_1.to_bytes(2, "big"))
            component_2 = color_data[3]
            file.write(component_2.to_bytes(2, "big"))
            component_3 = color_data[4]
            file.write(component_3.to_bytes(2, "big"))
            component_4 = color_data[5]
            file.write(component_4.to_bytes(2, "big"))

            color_name = color_data[0]

            color_name_length = len(color_name) + 1 # + 1 is for termination character
            file.write(color_name_length.to_bytes(4, "big"))

            color_name_bytes = bytes(color_name, "utf-16-be")
            file.write(color_name_bytes)

            termination_char = 0
            file.write(termination_char.to_bytes(2, "big"))

    except OSError:
        log.error("\nError while saving .aco file")
        log.error(traceback.format_exc())

    finally:
        file.close()

def generate_aco(input_file: TextIOWrapper, output_file: BufferedWriter) -> None:
    """Generating`.aco` file based on the data from the `.csv` file.

    Args:
        input_file: handle to the `.csv` file to be parsed.
        output_file: handle to the `.aco` file to be saved.
    """
    log.info("\nGenerating \"%s\" to \"%s\"", input_file.name, output_file.name)

    colors_data = parse_csv(input_file)

    save_aco(colors_data, output_file)
