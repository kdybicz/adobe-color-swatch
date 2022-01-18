#!/usr/bin/env python3

import traceback
import sys, getopt

def validate_color_space(color_space_id):
  if color_space_id in [0, 1, 2, 8]:
    return
  elif color_space_id == 3:
    print("not supported: Pantone matching system")
  elif color_space_id == 4:
    print("not supported: Focoltone colour system")
  elif color_space_id == 5:
    print("not supported: Trumatch color")
  elif color_space_id == 6:
    print("not supported: Toyo 88 colorfinder 1050")
  elif color_space_id == 7:
    print("not supported: Lab")
  elif color_space_id == 10:
    print("not supported: HKS colors")
  else:
    print("not supported: unknown color space id:", color_space_id)
  
  sys.exit(2)

def raw_color_to_hex(color_space_id, component_1, component_2, component_3, component_4):
  if color_space_id in [0, 1]:
    return format(component_1, '04X') + format(component_2, '04X') + format(component_3, '04X')
  elif color_space_id == 2:
    return format(component_1, '04X') + format(component_2, '04X') + format(component_3, '04X') + format(component_4, '04X')
  elif color_space_id == 8:
    return format(component_1, '04X')
  else:
    print("not supported: unknown color space id:", color_space_id)
    sys.exit(2)

def hex_color_to_raw(color_space_id, color_hex):
  if color_space_id in [0, 1]:
    if len(color_hex) == 6:
      # * 257 to convert to 32-bit color space
      return [int(color_hex[0:2], base=16) * 257, int(color_hex[2:4], base=16) * 257, int(color_hex[4:6], base=16) * 257, 0]
    elif len(color_hex) == 12:
      return [int(color_hex[0:4], base=16), int(color_hex[4:8], base=16), int(color_hex[8:12], base=16), 0]
    else:
      print("unsupported color format:", color_hex, len(color_hex))
      sys.exit(2)
  elif color_space_id == 2:
    if len(color_hex) == 8:
      # * 257 to convert to 32-bit color space
      return [int(color_hex[0:2], base=16) * 257, int(color_hex[2:4], base=16) * 257, int(color_hex[4:6], base=16) * 257, int(color_hex[6:8], base=16) * 257]
    elif len(color_hex) == 16:
      return [int(color_hex[0:4], base=16), int(color_hex[4:8], base=16), int(color_hex[8:12], base=16), int(color_hex[12:16], base=16)]
    else:
      print("unsupported color format:", color_hex)
      sys.exit(2)
  elif color_space_id == 8:
    if len(color_hex) == 2:
      # * 257 to convert to 32-bit color space
      return [int(color_hex[0:2], base=16) * 257, 0, 0, 0]
    elif len(color_hex) == 4:
      return [int(color_hex[0:4], base=16), 0, 0, 0]
    else:
      print("unsupported color format:", color_hex)
      sys.exit(2)
  else:
    print("not supported: unknown color space id:", color_space_id)
    sys.exit(2)


def parse_aco(inputFile):
  colors = []

  try:
    file = open(inputFile, "rb")

    # Version 1
    # print("")
    # print("Parsing version 1 section")

    version_byte = int.from_bytes(file.read(2), "big")
    assert version_byte == 1, "Version byte should be 1"

    color_count = int.from_bytes(file.read(2), "big")
    # print("Colors found:", color_count)

    for x in range(color_count):
      color_space_id = int.from_bytes(file.read(2), "big")
      validate_color_space(color_space_id)

      component_1 = int.from_bytes(file.read(2), "big")
      component_2 = int.from_bytes(file.read(2), "big")
      component_3 = int.from_bytes(file.read(2), "big")
      component_4 = int.from_bytes(file.read(2), "big")

      # print(" - ID:", x)
      # print("   Color space:", color_space_id)
      # print("  ", component_1, component_2, component_3, component_4)

    # Version 2
    print("")
    print("Parsing version 2 section")

    version_byte = int.from_bytes(file.read(2), "big")
    assert version_byte == 2, "Version byte should be 2"

    color_count = int.from_bytes(file.read(2), "big")
    print("Colors found:", color_count)

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

      print(" - ID:", x)
      print("   Color name:", name)
      print("   Color space:", color_space_id)
      print("   Color:", color_hex)

      color = [name, color_space_id, color_hex]

      colors.append(color)

  except:
    print("")
    print("Error while parsing .aco file")
    print(traceback.format_exc())

  finally:
    file.close()
  
  return colors

def save_csv(colors_data, outputFile):
  try:
    file = open(outputFile, "w", encoding="utf-8")
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
    print("")
    print("Error while saving .csv file")
    print(traceback.format_exc())

  finally:
    file.close()

def extract_aco(inputFile, outputFile):
  print("")
  print("")
  print("Extracting", inputFile, "to", outputFile)
  
  colors_data = parse_aco(inputFile)
  
  save_csv(colors_data, outputFile)

def parse_csv(inputFile):
  colors = []

  try:
    file = open(inputFile, "r", encoding="utf-8")

    # Parse
    print("")
    print("Parsing file")

    header = file.readline()
    assert header == "name,space_id,color\n", "Invalid file header"

    color_lines = file.readlines()

    print("Colors found:", len(color_lines))

    for color_line in color_lines:
      line_elements = color_line.split(",")
      assert len(line_elements) == 3, "Color line should contain 3 elements"

      name = line_elements[0]
      assert len(name.strip()) > 0, "Color name must be provided"

      color_space_id = int(line_elements[1])

      color_hex = line_elements[2].strip()

      print(" - Color name:", name)
      print("   Color space:", color_space_id)
      print("   Color:", color_hex)

      color_components = hex_color_to_raw(color_space_id, color_hex)

      color = [name, color_space_id, color_components[0], color_components[1], color_components[2], color_components[3]]

      colors.append(color)

  except:
    print("")
    print("Error while parsing .csv file")
    print(traceback.format_exc())

  finally:
    file.close()
  
  return colors

def save_aco(colors_data, outputFile):
  try:
    file = open(outputFile, "wb")

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
    print("")
    print("Error while saving .aco file")
    print(traceback.format_exc())

  finally:
    file.close()

def generate_aco(inputFile, outputFile):
  print("")
  print("")
  print("Generating", inputFile, "to", outputFile)

  colors_data = parse_csv(inputFile)

  save_aco(colors_data, outputFile)

def print_help():
    print("swatch.py --extract --input swatch.aco --output swatch.csv")
    print("swatch.py -e -i swatch.aco -o swatch.csv")
    print("swatch.py --generate --input swatch.csv --output swatch.aco")
    print("swatch.py -g -i swatch.csv -o swatch.aco")

def main(argv):
    try:
        opts, args = getopt.getopt(argv,"hegi:o:",["help", "extract", "generate", "input=", "output="])
    except getopt.GetoptError:
        print_help()
        sys.exit(2)
    
    extracting = False
    generating = False
    inputFile = None
    outputFile = None

    for opt, arg in opts:
        if opt in ("-h", "--help"):
            print_help()
            sys.exit()
        elif opt in ("-e", "--extract"):
          extracting = True
        elif opt in ("-g", "--generate"):
          generating = True
        elif opt in ("-i", "--input"):
          inputFile = arg
        elif opt in ("-o", "--output"):
          outputFile = arg
    
    if inputFile == None or outputFile == None:
      print_help()
      sys.exit(2)
    
    if extracting == True and generating == True:
      print_help()
      sys.exit(2)
    
    if extracting == False and generating == False:
      print_help()
      sys.exit(2)

    if extracting == True:
      extract_aco(inputFile, outputFile)
    else:
      generate_aco(inputFile, outputFile)

if __name__ == "__main__":
    main(sys.argv[1:])
