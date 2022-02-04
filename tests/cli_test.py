# pylint: disable=missing-function-docstring,missing-module-docstring,too-many-arguments
import re

import pytest

from swatch.cli import parse_args

def test_version(capsys):
  # when
  with pytest.raises(SystemExit):
    parse_args(["--version"])
  # then
  captured = capsys.readouterr().out
  assert re.match(r"swatch \d.\d.\d", captured)

def test_help_for_no_args(capsys):
  # when
  parse_args([])
  # then
  assert True

def test_help_for_h(capsys):
  # when
  with pytest.raises(SystemExit):
    parse_args(['-h'])
  # then
  captured = capsys.readouterr().out
  assert re.search(r"Adobe Color Swatch generator and parser", captured)
  assert re.search(r"-h, --help +show this help message and exit", captured)


# Tests: extract
def test_help_for_extract_with_no_args(capsys):
  # when
  with pytest.raises(SystemExit):
    parse_args(['extract'])
  # then
  captured = capsys.readouterr().err
  assert re.search(r"usage: swatch extract \[-h\] -i INPUT -o OUTPUT \[-v\]", captured)
  assert re.search(r"swatch extract: error: the following arguments are required: -i/--input, -o/--output", captured)

def test_help_for_extract_with_h(capsys):
  # when
  with pytest.raises(SystemExit):
    parse_args(['extract', '-h'])
  # then
  captured = capsys.readouterr().out
  assert re.search(r"Extract \.aco input file to a \.csv output file", captured)
  assert re.search(r"usage: swatch extract \[-h\] -i INPUT -o OUTPUT \[-v\]", captured)
  
def test_extract_success_with_verbose(tmpdir):
  # given
  input = tmpdir.join("in.aco")
  input.write_binary(b'Binary file contents')
  output = tmpdir.join("out.csv")
  
  # when
  _, arguments = parse_args(['extract', '-i', input.strpath, '-o', output.strpath, '-v'])
  # then
  assert arguments.sub_command == "extract"
  assert arguments.verbose
  assert arguments.input.name == input.strpath
  assert arguments.output.name == output.strpath
  
def test_extract_success_without_verbose(tmpdir):
  # given
  input = tmpdir.join("in.aco")
  input.write_binary(b'Binary file contents')
  output = tmpdir.join("out.csv")
  
  # when
  _, arguments = parse_args(['extract', '-i', input.strpath, '-o', output.strpath])
  # then
  assert arguments.sub_command == "extract"
  assert not arguments.verbose
  assert arguments.input.name == input.strpath
  assert arguments.output.name == output.strpath
  
def test_extract_help_for_missing_input(capsys, tmpdir):
  # given
  output = tmpdir.join("out.csv")
  
  # when
  with pytest.raises(SystemExit):
    parse_args(['extract', '-o', output.strpath])
  # then
  captured = capsys.readouterr().err
  assert re.search(r"usage: swatch extract \[-h\] -i INPUT -o OUTPUT \[-v\]", captured)
  assert re.search(r"swatch extract: error: the following arguments are required: -i/--input", captured)
  
def test_extract_help_for_missing_output(capsys, tmpdir):
  # given
  input = tmpdir.join("in.aco")
  input.write_binary(b'Binary file contents')
  
  # when
  with pytest.raises(SystemExit):
    parse_args(['extract', '-i', input.strpath])
  # then
  captured = capsys.readouterr().err
  assert re.search(r"usage: swatch extract \[-h\] -i INPUT -o OUTPUT \[-v\]", captured)
  assert re.search(r"swatch extract: error: the following arguments are required: -o/--output", captured)


# Tests: generate
def test_help_for_generate_with_no_args(capsys):
  # when
  with pytest.raises(SystemExit):
    parse_args(['generate'])
  # then
  captured = capsys.readouterr().err
  assert re.search(r"usage: swatch generate \[-h\] -i INPUT -o OUTPUT \[-v\]", captured)
  assert re.search(r"swatch generate: error: the following arguments are required: -i/--input, -o/--output", captured)

def test_help_for_generate_with_h(capsys):
  # when
  with pytest.raises(SystemExit):
    parse_args(['generate', '-h'])
  captured = capsys.readouterr().out
  assert re.search(r"Generate \.aco output file based on \.csv input file", captured)
  assert re.search(r"usage: swatch generate \[-h\] -i INPUT -o OUTPUT \[-v\]", captured)
  
def test_generate_success_with_verbose(tmpdir):
  # given
  input = tmpdir.join("in.csv")
  input.write('Text file contents')
  output = tmpdir.join("out.aco")
  
  # when
  _, arguments = parse_args(['generate', '-i', input.strpath, '-o', output.strpath, '-v'])
  # then
  assert arguments.sub_command == "generate"
  assert arguments.verbose
  assert arguments.input.name == input.strpath
  assert arguments.output.name == output.strpath
  
def test_generate_success_without_verbose(tmpdir):
  # given
  input = tmpdir.join("in.csv")
  input.write('Text file contents')
  output = tmpdir.join("out.aco")
  
  # when
  _, arguments = parse_args(['generate', '-i', input.strpath, '-o', output.strpath])
  # then
  assert arguments.sub_command == "generate"
  assert not arguments.verbose
  assert arguments.input.name == input.strpath
  assert arguments.output.name == output.strpath
  
def test_generate_help_for_missing_input(capsys, tmpdir):
  # given
  output = tmpdir.join("out.aco")
  
  # when
  with pytest.raises(SystemExit):
    parse_args(['generate', '-o', output.strpath])
  # then
  captured = capsys.readouterr().err
  assert re.search(r"usage: swatch generate \[-h\] -i INPUT -o OUTPUT \[-v\]", captured)
  assert re.search(r"swatch generate: error: the following arguments are required: -i/--input", captured)
  
def test_generate_help_for_missing_output(capsys, tmpdir):
  # given
  input = tmpdir.join("in.csv")
  input.write('Text file contents')
  
  # when
  with pytest.raises(SystemExit):
    parse_args(['generate', '-i', input.strpath])
  # then
  captured = capsys.readouterr().err
  assert re.search(r"usage: swatch generate \[-h\] -i INPUT -o OUTPUT \[-v\]", captured)
  assert re.search(r"swatch generate: error: the following arguments are required: -o/--output", captured)
