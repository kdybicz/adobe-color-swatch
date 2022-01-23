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
parser_a = subparsers.add_parser('extract', help="extract help", description="Extract .aco input file to a .csv output file")
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
  level = logging.DEBUG
else:
  level = logging.INFO

logging.basicConfig(level=level, format='%(message)s', handlers=[])
logger = logging.getLogger("__name__")

h1 = logging.StreamHandler(sys.stdout)
h1.setLevel(level)
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

def validate_color_space(color_space_id):
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
    raise ValidationError("unsupported color space: space id {}".format(color_space_id))

def raw_color_to_hex(color_space_id, component_1, component_2, component_3, component_4):
  if color_space_id == 0:
    if not 0 <= component_1 <= 65535 or not 0 <= component_2 <= 65535 or not 0 <= component_3 <= 65535 or component_4 != 0:
      raise ValidationError("invalid RGB value: {}, {}, {}, {}".format(component_1, component_2, component_3, component_4))

    return "#{0:04X}{1:04X}{2:04X}".format(component_1, component_2, component_3)
  if color_space_id == 1:
    if not 0 <= component_1 <= 65535 or not 0 <= component_2 <= 65535 or not 0 <= component_3 <= 65535 or component_4 != 0:
      raise ValidationError("invalid HSB value: {}, {}, {}, {}".format(component_1, component_2, component_3, component_4))

    return "#{0:04X}{1:04X}{2:04X}".format(component_1, component_2, component_3)
  elif color_space_id == 2:
    if not 0 <= component_1 <= 65535 or not 0 <= component_2 <= 65535 or not 0 <= component_3 <= 65535 or not 0 <= component_4 <= 65535:
      raise ValidationError("invalid CMYK value: {}, {}, {}, {}".format(component_1, component_2, component_3, component_4))

    return "#{0:04X}{1:04X}{2:04X}{3:04X}".format(component_1, component_2, component_3, component_4)
  elif color_space_id == 8:
    if not 0 <= component_1 <= 10000 or component_2 != 0 or component_3 != 0 or component_4 != 0:
      raise ValidationError("invalid Grayscale value: {}, {}, {}, {}".format(component_1, component_2, component_3, component_4))

    return "#{0:04X}".format(component_1)
  else:
    raise ValidationError("unsupported color space: space id {}".format(color_space_id))

def hex_color_to_raw(color_space_id, color_hex):
  color_hex = color_hex.lstrip('#')

  if len(color_hex.strip()) == 0:
    raise ValidationError("unsupported color format: {}".format(color_hex))

  if color_space_id in [0, 1]:
    if len(color_hex) == 6:
      # * 257 to convert to 32-bit color space
      return [int(color_hex[0:2], base=16) * 257, int(color_hex[2:4], base=16) * 257, int(color_hex[4:6], base=16) * 257, 0]
    elif len(color_hex) == 12:
      return [int(color_hex[0:4], base=16), int(color_hex[4:8], base=16), int(color_hex[8:12], base=16), 0]
    else:
      raise ValidationError("unsupported color format: {}".format(color_hex))
  elif color_space_id == 2:
    if len(color_hex) == 8:
      # * 257 to convert to 32-bit color space
      return [int(color_hex[0:2], base=16) * 257, int(color_hex[2:4], base=16) * 257, int(color_hex[4:6], base=16) * 257, int(color_hex[6:8], base=16) * 257]
    elif len(color_hex) == 16:
      return [int(color_hex[0:4], base=16), int(color_hex[4:8], base=16), int(color_hex[8:12], base=16), int(color_hex[12:16], base=16)]
    else:
      raise ValidationError("unsupported color format: {}".format(color_hex))
  elif color_space_id == 8:
    if len(color_hex) == 2:
      # * 257 to convert to 32-bit color space
      gray = int(color_hex[0:2], base=16) * 257
    elif len(color_hex) == 4:
      gray = int(color_hex[0:4], base=16)
    else:
      raise ValidationError("unsupported color format: {}".format(color_hex))

    if gray > 10000:
      raise ValidationError("invalid grayscale value: {}".format(color_hex))

    return [gray, 0, 0, 0]
  else:
    raise ValidationError("unsupported color space: space id {}".format(color_space_id))

def parse_aco(file):
  colors = []

  try:
    # Version 1
    logger.debug("\nParsing version 1 section")

    version_byte = int.from_bytes(file.read(2), "big")
    if version_byte != 1:
      raise ValidationError("Version byte should be 1")

    color_count = int.from_bytes(file.read(2), "big")
    logger.debug("Colors found: {}".format(color_count))

    for x in range(color_count):
      color_space_id = int.from_bytes(file.read(2), "big")
      validate_color_space(color_space_id)

      component_1 = int.from_bytes(file.read(2), "big")
      component_2 = int.from_bytes(file.read(2), "big")
      component_3 = int.from_bytes(file.read(2), "big")
      component_4 = int.from_bytes(file.read(2), "big")

      logger.debug(" - ID: {}".format(x))
      logger.debug("   Color space: {}".format(color_space_id))
      logger.debug("   Components: {} {} {} {}".format(component_1, component_2, component_3, component_4))

    # Version 2
    logger.debug("\nParsing version 2 section")

    version_byte = int.from_bytes(file.read(2), "big")
    if version_byte != 2:
      raise ValidationError("Version byte should be 2")

    color_count = int.from_bytes(file.read(2), "big")
    logger.debug("Colors found {}:".format(color_count))

    for x in range(color_count):
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

      logger.debug(" - ID: {}".format(x))
      logger.debug("   Color name: {}".format(name))
      logger.debug("   Color space: {}".format(color_space_id))
      logger.debug("   Color: {}".format(color_hex))

      color = [name, color_space_id, color_hex]

      colors.append(color)

  except ValidationError as e:
    logger.error("\nError while parsing .aco file: {}".format(e.message))

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

  except:
    logger.error("\nError while saving .csv file")
    logger.error(traceback.format_exc())

  finally:
    file.close()

def extract_aco(inputFile, outputFile):
  print("\nExtracting \"{}\" to \"{}\"".format(inputFile.name, outputFile.name))

  colors_data = parse_aco(inputFile)

  save_csv(colors_data, outputFile)

def parse_csv(file):
  colors = []

  try:
    # Parse
    logger.debug("\nParsing file")

    header = file.readline()
    if header != "name,space_id,color\n":
      raise ValidationError("Invalid file header")

    color_lines = file.readlines()

    logger.debug("Colors found: {}".format(len(color_lines)))

    for color_line in color_lines:
      line_elements = color_line.split(",")
      if len(line_elements) != 3:
        raise ValidationError("Color line should contain 3 elements")

      name = line_elements[0]
      if len(name.strip()) == 0:
        raise ValidationError("Color name must be provided")

      color_space_id = int(line_elements[1])

      color_hex = line_elements[2].strip()

      logger.debug(" - Color name: {}".format(name))
      logger.debug("   Color space: {}".format(color_space_id))
      logger.debug("   Color: {}".format(color_hex))

      color_components = hex_color_to_raw(color_space_id, color_hex)

      color = [name, color_space_id, color_components[0], color_components[1], color_components[2], color_components[3]]

      colors.append(color)

  except ValidationError as e:
    logger.info("\nError while parsing .csv file: {}".format(e.message) )

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

  except:
    logger.error("\nError while saving .aco file")
    logger.error(traceback.format_exc())

  finally:
    file.close()

def generate_aco(inputFile, outputFile):
  logger.info("\nGenerating \"{}\" to \"{}\"".format(inputFile.name, outputFile.name))

  colors_data = parse_csv(inputFile)

  save_aco(colors_data, outputFile)

def main():
  extracting = args.subCommand == 'extract'
  generating = args.subCommand == 'generate'

  if extracting == False and generating == False:
    parser.print_help()
    sys.exit(2)

  inputFile = args.input
  outputFile = args.output

  try:
    if extracting == True:
      extract_aco(inputFile, outputFile)
    else:
      generate_aco(inputFile, outputFile)
  except:
    logger.critical("\nUnexpected error")
    logger.critical(traceback.format_exc())

if __name__ == "__main__":
  main()
