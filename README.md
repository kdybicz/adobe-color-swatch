[![Tests](https://github.com/kdybicz/adobe-color-swatch/actions/workflows/tests.yml/badge.svg)](https://github.com/kdybicz/adobe-color-swatch/actions/workflows/tests.yml)
[![CodeQL](https://github.com/kdybicz/adobe-color-swatch/actions/workflows/codeql-analysis.yml/badge.svg)](https://github.com/kdybicz/adobe-color-swatch/actions/workflows/codeql-analysis.yml)

# Adobe Color Swatch

## Description

`swatch.py` is a Python 3 command line interface created to extract Color
Swatch data from `.aco` files and save them as a simple `.csv`. It can also
work in revers and generate a `.aco` file based on a `.csv` data file.

## Installation

Install from GitHub repository:
```
pip3 install git+https://github.com/kdybicz/adobe-color-swatch
```

## Usage

### Extract `.aco`

```
usage: swatch extract [-h] -i INPUT -o OUTPUT [-v]

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
usage: swatch generate [-h] -i INPUT -o OUTPUT [-v]

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
Script is supporting both version 1 and 2 of the Color Swatch format.

`.csv` file is using custom format:

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

## Validation

To validate that the `.aco` file generation is working properly I decided on
the following process:
* export few default Color Swatches from Adobe Photoshop 2022
* extract them to `.csv` files and make sure data in that files are matching
  to what is in the Adobe Photoshop
* generate new `.aco` files from `.csv` acquired in the previous step
* compare original `.aco` files with ones regenerated from `.csv` using:
```
hexdump examples/utf.aco > utf.aco.hex
hexdump utf-new.aco > utf-new.aco.hex
diff utf.aco.hex utf-new.aco.hex -y
```
* import new `.aco` files into Adobe Photoshop and compare them with original
  Swatches

### Notes

I'm aware that original `.aco` files contain some additional bytes at the end
of the files. Those bytes which will not be present in `.aco` files generated
by the script. These bytes might be related to
[Custom color spaces](https://www.adobe.com/devnet-apps/photoshop/fileformatashtml/#50577411_28552),
which are not supported by this script.

Nevertheless I was able to successfully import generated `.aco` files back into
the Adobe Photoshop and use them in my work!

## Development

### Testing and linting

For all supported environments:
```
tox --parallel
```
**Note**: running tests for all supported Python versions require to have
Python interpreters  for those versions to be installed.

For particular environment:
```
tox -e py39
```

For running tests in development environment:
```
tox --devenv venv -e py39
. venv/bin/activate
pytest
```

### Local installation

Install a project in editable mode:
```
 pip3 install -e .
```

## Deployment

Building the packages:
```
./venv/bin/python setup.py sdist bdist_wheel
```

Checking if build packages are valid:
```
twine check dist/*
```

Uploading to pypi:
```
twine upload -r pypi dist/*
```
