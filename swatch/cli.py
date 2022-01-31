"""
CLI wrapper for swatch package
"""
from argparse import ArgumentParser, FileType, Namespace
import logging
import sys
from typing import Tuple

from swatch.swatch import extract_aco, generate_aco

def arguments() -> Tuple[ArgumentParser, Namespace]:
    """Define CLI parameters"""

    parser = ArgumentParser(
        description="Adobe Color Swatch generator and parser"
    )
    subparsers = parser.add_subparsers(dest="sub_command")

    # create the parser for the "extract" command
    extract_parser = subparsers.add_parser(
        "extract",
        help="extract help",
        description="Extract .aco input file to a .csv output file"
    )
    extract_parser.add_argument(
        "-i",
        "--input",
        help="input file",
        type=FileType("rb"),
        required=True
    )
    extract_parser.add_argument(
        "-o",
        "--output",
        help="output file",
        type=FileType("w"),
        required=True
    )
    extract_parser.add_argument(
        "-v",
        "--verbose",
        help="increase output verbosity",
        action="store_true")

    # create the parser for the "generate" command
    generate_parser = subparsers.add_parser(
        "generate",
        help="generate help",
        description="generate .aco output file based on .csv input file"
    )
    generate_parser.add_argument(
        "-i",
        "--input",
        help="input file",
        type=FileType(
        "r"),
        required=True
    )
    generate_parser.add_argument(
        "-o",
        "--output",
        help="output file",
        type=FileType("wb"),
        required=True
    )
    generate_parser.add_argument(
        "-v",
        "--verbose",
        help="increase output verbosity",
        action="store_true"
    )

    return parser, parser.parse_args()

def main() -> None:
    """main function"""

    parser, args = arguments()

    if args.sub_command is not None:
        if args.verbose:
            log_level = logging.DEBUG
        else:
            log_level = logging.INFO

        logging.basicConfig(level=log_level, format='%(message)s', handlers=[])

        if args.sub_command == "extract":
            return extract_aco(args.input, args.output)

        if args.sub_command == "generate":
            return generate_aco(args.input, args.output)

    parser.print_help()
    sys.exit(1)
