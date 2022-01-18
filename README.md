# Adobe Color Swatch Generator

## Description

`swatch.py` is a Python 3 script created to extract Color Swatch data from `.aco` files and output them into a simple `.csv`. It can also work in revers, so generate an `.aco` file based on data from a `.csv` file.

`.aco` file format parser and generator were created based on 
[Adobe Color Swatch File Format Specification](https://www.adobe.com/devnet-apps/photoshop/fileformatashtml/#50577411_pgfId-1055819). Script is supporting read and write for Version 1 and 2 of the Color Swatch format.

`.csv` file is using simple, arbitrary format:

```
name,space_id,color
RGB Magenta,0,FFFF0000FFFF
CMYK Magenta,2,FFFF0000FFFFFFFF
75% Gray,8,1D4C
```

### Color space IDs

Supported color spaces

| ID | Name       |
|:--:|:----------:|
| 0  | RGB        |
| 1  | HSB        |
| 2  | CMYK       |
| 8  | Grayscale  |

NOT supported color spaces

| ID | Name                     |
|:--:|:------------------------:|
| 3  | Pantone matching system  |
| 4  | Focoltone colour system  |
| 5  | Trumatch color           |
| 6  | Toyo 88 colorfinder 1050 |
| 7  | Lab                      |
| 10 | HKS colors               |

## Usage

### Extract `.aco`

```
./swatch.py --extract --input swatch.aco --output swatch.csv
```

or

```
./swatch.py -e -i swatch.aco -o swatch.csv
```

### Generate `.aco`

```
./swatch.py --generate --input swatch.csv --output swatch.aco
```

or

```
./swatch.py -g -i swatch.csv -o swatch.aco
```

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
