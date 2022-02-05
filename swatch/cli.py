"""
CLI wrapper for swatch package
"""
from __future__ import annotations

import logging
import sys
from argparse import ArgumentParser
from argparse import FileType
from argparse import Namespace
from typing import Sequence
from typing import Tuple

if sys.version_info < (3, 8):   # pragma: no cover
    import importlib_metadata
else:   # pragma: no cover
    import importlib.metadata as importlib_metadata

from swatch.swatch import convert_aco_file_to_csv, convert_csv_file_to_aco

ParsedArgs = Tuple[ArgumentParser, Namespace]


def parse_args(args: Sequence[str] | None = None) -> ParsedArgs:
    """Define CLI parameters"""

    parser = ArgumentParser(
        prog='swatch',
        description='Adobe Color Swatch generator and parser',
    )
    parser.add_argument(
        '-V', '--version',
        action='version',
        version=f'%(prog)s {importlib_metadata.version("adobe_color_swatch")}',
    )
    subparsers = parser.add_subparsers(dest='sub_command')

    # create the parser for the "extract" command
    extract_parser = subparsers.add_parser(
        'extract',
        help='extract help',
        description='Extract .aco input file to a .csv output file',
    )
    extract_parser.add_argument(
        '-i',
        '--input',
        help='input file',
        type=FileType('rb'),
        required=True,
    )
    extract_parser.add_argument(
        '-o',
        '--output',
        help='output file',
        type=FileType('w'),
        required=True,
    )
    extract_parser.add_argument(
        '-v',
        '--verbose',
        help='increase output verbosity',
        action='store_true',
    )

    # create the parser for the "generate" command
    generate_parser = subparsers.add_parser(
        'generate',
        help='generate help',
        description='Generate .aco output file based on .csv input file',
    )
    generate_parser.add_argument(
        '-i',
        '--input',
        help='input file',
        type=FileType(
            'r',
        ),
        required=True,
    )
    generate_parser.add_argument(
        '-o',
        '--output',
        help='output file',
        type=FileType('wb'),
        required=True,
    )
    generate_parser.add_argument(
        '-v',
        '--verbose',
        help='increase output verbosity',
        action='store_true',
    )

    return parser, parser.parse_args(args)


def main(argv: Sequence[str] | None = None) -> int:   # pragma: no cover
    """main function"""

    parser, args = parse_args(argv)

    if args.sub_command is not None:
        if args.verbose:
            log_level = logging.DEBUG
        else:
            log_level = logging.INFO

        logging.basicConfig(level=log_level, format='%(message)s', handlers=[])

        if args.sub_command == 'extract':
            convert_aco_file_to_csv(args.input, args.output)

        if args.sub_command == 'generate':
            convert_csv_file_to_aco(args.input, args.output)

        return 0

    parser.print_help()
    return 1


if __name__ == '__main__':
    exit(main())
