#!/usr/bin/env python3

import argparse
import logging
import traceback
import sys

parser = argparse.ArgumentParser(
    description='Adobe Color Swatch generator and parser'
)
subparsers = parser.add_subparsers(help='sub-command help', dest="subCommand")

# create the parser for the "extract" command
parser_a = subparsers.add_parser('extract', help="extract help",
  description="Extract .aco input file to a .csv output file"
)
parser_a.add_argument("-i", "--input", help="input file", type=argparse.FileType("rb"), required=True)
parser_a.add_argument("-o", "--output", help="output file", type=argparse.FileType("w"), required=True)
parser_a.add_argument("-v", "--verbose", help="increase output verbosity", action="store_true")

# create the parser for the "generate" command
parser_b = subparsers.add_parser('generate', help='generate help', description="generate .aco output file based on .csv input file")
parser_b.add_argument("-i", "--input", help="input file", type=argparse.FileType("r"), required=True)
parser_b.add_argument("-o", "--output", help="output file", type=argparse.FileType("wb"), required=True)
parser_b.add_argument("-v", "--verbose", help="increase output verbosity", action="store_true")

parser.add_argument("-v", "--verbose", help="increase output verbosity", action="store_true")

args = parser.parse_args()
if args.verbose:
    LEVEL = logging.DEBUG
else:
    LEVEL = logging.INFO

logging.basicConfig(level=LEVEL, format='%(message)s', handlers=[])
logger = logging.getLogger("__name__")

h1 = logging.StreamHandler(sys.stdout)
h1.setLevel(LEVEL)
h1.addFilter(lambda record: record.levelno <= logging.INFO)
logger.addHandler(h1)

h2 = logging.StreamHandler(sys.stderr)
h2.setLevel(logging.WARNING)
logger.addHandler(h2)

class ValidationError(Exception):
    def __init__(self, message):
        self.message = message
    def __str__(self):
        return repr(self.message)

def validate_color_space(color_space_id: int):
    """Validate provided color space id.

    Args:
        color_space_id: color space if to be checked.

    Raises:
        ValidationError: Is raised if provided color space is not supported.
    """
    if color_space_id in [0, 1, 2, 8]:
        return
    elif color_space_id == 3:
        raise ValidationError("unsupported color space: Pantone matching system")
    elif color_space_id == 4:
        raise ValidationError("unsupported color space: Focoltone colour system")
    elif color_space_id == 5:
        raise ValidationError("unsupported color space: Trumatch color")
    elif color_space_id == 6:
        raise ValidationError("unsupported color space: Toyo 88 colorfinder 1050")
    elif color_space_id == 7:
        raise ValidationError("unsupported color space: Lab")
    elif color_space_id == 10:
        raise ValidationError("unsupported color space: HKS colors")
    else:
        raise ValidationError(f'unsupported color space: space id {color_space_id}')

def raw_color_to_hex(color_space_id: int, component_1: int, component_2: int, component_3: int, component_4: int):
    """Combines provided color data in a HEX string representation of that color.

    RGB
        The first three components represent red, green and blue. Fourth should be 0.
        They are full unsigned 16-bit values as in Apple's RGBColor data structure. Pure red = 65535, 0, 0.

    HSB
        The first three components represent hue, saturation and brightness.
        They are full unsigned 16-bit values as in Apple's HSVColor data structure. Pure red = 0, 65535, 65535.

    CMYK
        The four components represent cyan, magenta, yellow and black. They are full unsigned 16-bit values.
        0 = 100% ink. For example, pure cyan = 0, 65535, 65535, 65535.

    Grayscale
        The first component represent the gray value, from 0...10000.

    Args:
        color_space_id: color space if to be checked.
        component_1: first channel of the color for specified color space.
        component_2: second channel of the color for specified color space.
        component_3: third channel of the color for specified color space.
        component_4: fourth channel of the color for specified color space.

    Returns:
        A HEX string representation of the color.

    Raises:
        ValidationError: Is raised if color components exceed expected values for
            provided `color_space_id`.
    """
    if color_space_id == 0:
        if not 0 <= component_1 <= 65535 or not 0 <= component_2 <= 65535 or not 0 <= component_3 <= 65535 or component_4 != 0:
            raise ValidationError(f'invalid RGB value: {component_1}, {component_2}, {component_3}, {component_4}')

        return f'#{component_1:04X}{component_2:04X}{component_3:04X}'
    if color_space_id == 1:
        if not 0 <= component_1 <= 65535 or not 0 <= component_2 <= 65535 or not 0 <= component_3 <= 65535 or component_4 != 0:
            raise ValidationError(f'invalid HSB value: {component_1}, {component_2}, {component_3}, {component_4}')

        return f'#{component_1:04X}{component_2:04X}{component_3:04X}'
    elif color_space_id == 2:
        if not 0 <= component_1 <= 65535 or not 0 <= component_2 <= 65535 or not 0 <= component_3 <= 65535 or not 0 <= component_4 <= 65535:
            raise ValidationError(f'invalid CMYK value: {component_1}, {component_2}, {component_3}, {component_4}')

        return f'#{component_1:04X}{component_2:04X}{component_3:04X}{component_4:04X}'
    elif color_space_id == 8:
        if not 0 <= component_1 <= 10000 or component_2 != 0 or component_3 != 0 or component_4 != 0:
            raise ValidationError(f'invalid Grayscale value: {component_1}, {component_2}, {component_3}, {component_4}')

        return f'#{component_1:04X}'
    else:
        raise ValidationError(f'unsupported color space: space id {color_space_id}')

def hex_color_to_raw(color_space_id: int, color_hex = ""):
    """Parses provided HEX string representation of a color into four element list of color components.

    RGB
        Supports both 8-bit and 16-bit per color channel, expects three channels only. Leading `#` is optional
        Pure red = #FFFF00000000.

    HSB
        Supports both 8-bit and 16-bit per color channel, expects three channels only. Leading `#` is optional
        Pure red = #00FFFF.

    CMYK
        Supports both 8-bit and 16-bit per color channel, expects four channels. Leading `#` is optional
        Pure cyan = 0000FFFFFFFFFFFF.

    Grayscale
        Supports both 8-bit and 16-bit for greay value, expects only one channel. Leading `#` is optional
        Pure black = #2710.

    Args:
        color_space_id: color space if to be checked.
        color_hex: HEX string representation of a color.

    Returns:
        A four element list of color components.

    Raises:
        ValidationError: Is raised if color components exceed expected values for
            provided `color_space_id`.
    """
    color_hex = color_hex.lstrip('#')

    if len(color_hex.strip()) == 0:
        raise ValidationError(f'unsupported color format: {color_hex}')

    if color_space_id in [0, 1]:
        if len(color_hex) == 6:
            # * 257 to convert to 32-bit color space
            return [int(color_hex[0:2], base=16) * 257, int(color_hex[2:4], base=16) * 257, int(color_hex[4:6], base=16) * 257, 0]
        elif len(color_hex) == 12:
            return [int(color_hex[0:4], base=16), int(color_hex[4:8], base=16), int(color_hex[8:12], base=16), 0]
        else:
            raise ValidationError(f'unsupported color format: {color_hex}')
    elif color_space_id == 2:
        if len(color_hex) == 8:
            # * 257 to convert to 32-bit color space
            return [int(color_hex[0:2], base=16) * 257, int(color_hex[2:4], base=16) * 257, int(color_hex[4:6], base=16) * 257, int(color_hex[6:8], base=16) * 257]
        elif len(color_hex) == 16:
            return [int(color_hex[0:4], base=16), int(color_hex[4:8], base=16), int(color_hex[8:12], base=16), int(color_hex[12:16], base=16)]
        else:
            raise ValidationError(f'unsupported color format: {color_hex}')
    elif color_space_id == 8:
        if len(color_hex) == 2:
            # * 257 to convert to 32-bit color space
            gray = int(color_hex[0:2], base=16) * 257
        elif len(color_hex) == 4:
            gray = int(color_hex[0:4], base=16)
        else:
            raise ValidationError(f'unsupported color format: {color_hex}')

        if gray > 10000:
            raise ValidationError(f'invalid grayscale value: {color_hex}')

        return [gray, 0, 0, 0]
    else:
        raise ValidationError(f'unsupported color space: space id {color_space_id}')

def parse_aco(file):
    colors = []

    try:
        # Version 1
        logger.debug("\nParsing version 1 section")

        version_byte = int.from_bytes(file.read(2), "big")
        if version_byte != 1:
            raise ValidationError("Version byte should be 1")

        color_count = int.from_bytes(file.read(2), "big")
        logger.debug("Colors found: %d", color_count)

        for idx in range(color_count):
            color_space_id = int.from_bytes(file.read(2), "big")
            validate_color_space(color_space_id)

            component_1 = int.from_bytes(file.read(2), "big")
            component_2 = int.from_bytes(file.read(2), "big")
            component_3 = int.from_bytes(file.read(2), "big")
            component_4 = int.from_bytes(file.read(2), "big")

            logger.debug(" - ID: %d", idx)
            logger.debug("   Color space: %d", color_space_id)
            logger.debug("   Components: %d %d %d %d", component_1, component_2, component_3, component_4)

        # Version 2
        logger.debug("\nParsing version 2 section")

        version_byte = int.from_bytes(file.read(2), "big")
        if version_byte != 2:
            raise ValidationError("Version byte should be 2")

        color_count = int.from_bytes(file.read(2), "big")
        logger.debug("Colors found: %d", color_count)

        for idx in range(color_count):
            color_space_id = int.from_bytes(file.read(2), "big")
            validate_color_space(color_space_id)

            component_1 = int.from_bytes(file.read(2), "big")
            component_2 = int.from_bytes(file.read(2), "big")
            component_3 = int.from_bytes(file.read(2), "big")
            component_4 = int.from_bytes(file.read(2), "big")

            name_length = int.from_bytes(file.read(4), "big")
            name_bytes = file.read(name_length * 2 - 2) # - 2 is for omiting termination character
            name = name_bytes.decode("utf-16-be")

            # droping the string termination character
            file.read(2)

            color_hex = raw_color_to_hex(color_space_id, component_1, component_2, component_3, component_4)

            logger.debug(" - ID: %d", idx)
            logger.debug("   Color name: %d", name)
            logger.debug("   Color space: %d", color_space_id)
            logger.debug("   Color: %d", color_hex)

            color = [name, color_space_id, color_hex]

            colors.append(color)

    except ValidationError as err:
        logger.error("\nError while parsing .aco file: %s", err.message)

    finally:
        file.close()

    return colors

def save_csv(colors_data, file):
    try:
        file.write("name,space_id,color")
        file.write("\n")

        for color_data in colors_data:
            name = color_data[0]
            file.write(name)
            file.write(",")

            color_space_id = str(color_data[1])
            file.write(color_space_id)
            file.write(",")

            color_hex = str(color_data[2])
            file.write(color_hex)
            file.write("\n")

    except OSError:
        logger.error("\nError while saving .csv file")
        logger.error(traceback.format_exc())

    finally:
        file.close()

def extract_aco(input_file, output_file):
    print("\nExtracting \"%s\" to \"%s\"", input_file.name, output_file.name)

    colors_data = parse_aco(input_file)

    save_csv(colors_data, output_file)

def parse_csv(file):
    colors = []

    try:
        # Parse
        logger.debug("\nParsing file")

        header = file.readline()
        if header != "name,space_id,color\n":
            raise ValidationError("Invalid file header")

        color_lines = file.readlines()

        logger.debug("Colors found: %d", len(color_lines))

        for color_line in color_lines:
            line_elements = color_line.split(",")
            if len(line_elements) != 3:
                raise ValidationError("Color line should contain 3 elements")

            name = line_elements[0]
            if len(name.strip()) == 0:
                raise ValidationError("Color name must be provided")

            color_space_id = int(line_elements[1])

            color_hex = line_elements[2].strip()

            logger.debug(" - Color name: %d", name)
            logger.debug("   Color space: %d", color_space_id)
            logger.debug("   Color: %d", color_hex)

            color_components = hex_color_to_raw(color_space_id, color_hex)

            color = [name, color_space_id, color_components[0], color_components[1], color_components[2], color_components[3]]

            colors.append(color)

    except ValidationError as err:
        logger.info("\nError while parsing .csv file: %s", err.message)

    finally:
        file.close()

    return colors

def save_aco(colors_data, file):
    try:
        # Version 1
        version = 1
        file.write(version.to_bytes(2, "big"))

        color_count = len(colors_data)
        file.write(color_count.to_bytes(2, "big"))

        for color_data in colors_data:
            color_space_id = color_data[1]
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
            color_space_id = color_data[1]
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
        logger.error("\nError while saving .aco file")
        logger.error(traceback.format_exc())

    finally:
        file.close()

def generate_aco(input_file, output_file):
    logger.info("\nGenerating \"%s\" to \"%s\"", input_file.name, output_file.name)

    colors_data = parse_csv(input_file)

    save_aco(colors_data, output_file)

def main():
    extracting = args.subCommand == 'extract'
    generating = args.subCommand == 'generate'

    if extracting is False and generating is False:
        parser.print_help()
        sys.exit(2)

    input_file = args.input
    output_file = args.output

    try:
        if extracting is False:
            extract_aco(input_file, output_file)
        else:
            generate_aco(input_file, output_file)
    except (OSError, ValidationError):
        logger.critical("\nUnexpected error")
        logger.critical(traceback.format_exc())

if __name__ == "__main__":
    main()
