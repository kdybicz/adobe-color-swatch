[![Tests](https://github.com/kdybicz/adobe-color-swatch/actions/workflows/tests.yml/badge.svg)](https://github.com/kdybicz/adobe-color-swatch/actions/workflows/tests.yml)

# Adobe Color Swatch Generator

## Description

`swatch.py` is a Python 3 command line interface created to extract Color Swatch data from `.aco` files and output them into a simple `.csv`.
It can also work in revers, so generate an `.aco` file based on data from a `.csv` file.

## Installation

```
pip3 install git+https://github.com/kdybicz/adobe-color-swatch
```

## Usage

### Extract `.aco`

```
usage: swatch.py extract [-h] -i INPUT -o OUTPUT [-v]

Extract .aco input file to a .csv output file

optional arguments:
  -h, --help            show this help message and exit
  -i INPUT, --input INPUT
                        input file
  -o OUTPUT, --output OUTPUT
                        output file
  -v, --verbose         increase output verbosity
```

### Generate `.aco`

```
usage: swatch.py generate [-h] -i INPUT -o OUTPUT [-v]

generate .aco output file based on .csv input file

optional arguments:
  -h, --help            show this help message and exit
  -i INPUT, --input INPUT
                        input file
  -o OUTPUT, --output OUTPUT
                        output file
  -v, --verbose         increase output verbosity
```

## Specification

`.aco` file format parser and generator were created based on
[Adobe Color Swatch File Format Specification](https://www.adobe.com/devnet-apps/photoshop/fileformatashtml/#50577411_pgfId-1055819).
Script is supporting read and write for Version 1 and 2 of the Color Swatch format.

`.csv` file is using simple, arbitrary format:

```
name,space_id,color
RGB Magenta 16-bit,0,#FF00FF
RGB Magenta 32-bit,0,#FFFF0000FFFF
CMYK Magenta 16-bit,2,#FF00FFFF
CMYK Magenta 32-bit,2,#FFFF0000FFFFFFFF
75% Gray,8,#1D4C
```

### Color space IDs

Supported color spaces

| ID | Name       | Color information                                                                  |
|:--:|:----------:|:-----------------------------------------------------------------------------------|
| 0  | RGB        | Supports 16 and 32 bit channels, so accordingly 6 or 12 bytes of color information |
| 1  | HSB        | Supports 16 and 32 bit channels, so accordingly 6 or 12 bytes of color information |
| 2  | CMYK       | Supports 16 and 32 bit channels, so accordingly 8 or 16 bytes of color information |
| 8  | Grayscale  | Supports 16 and 32 bit channel, so accordingly 2 or 4 bytes of color information   |

NOT supported color spaces

| ID | Name                     |
|:--:|:------------------------:|
| 3  | Pantone matching system  |
| 4  | Focoltone colour system  |
| 5  | Trumatch color           |
| 6  | Toyo 88 colorfinder 1050 |
| 7  | Lab                      |
| 10 | HKS colors               |

## Debugging

To validate that the `.aco` file generation is working properly I decided on the following flow:
* export few default Color Swatches from Adobe Photoshop 2022
* extract them to `.csv` files and make sure data in that files are matching to what I can see in Adobe Photoshop
* generate new `.aco` files from `.csv` acquired in the previous step
* compare original `.aco` files with ones regenerated from `.csv` using:
```
hexdump examples/utf.aco > utf.aco.hex
hexdump utf-new.aco > utf-new.aco.hex
diff utf.aco.hex utf-new.aco.hex -y
```
* import new `.aco` files into Adobe Photoshop and compare with original Swatches

### Notes

I'm aware that in the original `.aco` files there are some additional bytes at the end of the files, bytes which will not be present in the generate version. These bytes might be related to [Custom color spaces](https://www.adobe.com/devnet-apps/photoshop/fileformatashtml/#50577411_28552), but those are not supported by my script.

Nevertheless I was able to successfully import generated `.aco` files back into the Adobe Photoshop and use them in my work!
