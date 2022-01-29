"""
CLI wrapper for swatch package
"""
from argparse import ArgumentParser, FileType, Namespace
import sys
from typing import Tuple

from swatch.swatch import Swatch

def arguments() -> Tuple[ArgumentParser, Namespace]:
    """Define CLI parameters"""

    parser = ArgumentParser(
        description="Adobe Color Swatch generator and parser"
    )
    subparsers = parser.add_subparsers(dest="subCommand")

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

    if args.subCommand == "extract":
        cli = Swatch(args.verbose)
        cli.extract_aco(args.input, args.output)
    elif args.subCommand == "generate":
        cli = Swatch(args.verbose)
        cli.generate_aco(args.input, args.output)
    else:
        parser.print_help()
        sys.exit(1)
