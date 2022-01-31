.PHONY: clean-pyc clean-test clean setup test coverage lint mypy check

clean-pyc:
	find . -name '*.pyc' -exec rm -f {} +
	find . -name '*.pyo' -exec rm -f {} +
	find . -name '*~' -exec rm -f {} +
	find . -name '__pycache__' -exec rm -fr {} +

clean-test:
	rm -f .coverage
	rm -f .coverage.*

clean: clean-pyc clean-test

setup:
	pipenv install --dev

test: clean
	pipenv run pytest

coverage: clean
	pipenv run pytest --cov=swatch --cov-report=term-missing --cov-fail-under 95

lint:
	pipenv run pylint swatch/ tests/

mypy:
	pipenv run mypy swatch

check: test lint mypy
