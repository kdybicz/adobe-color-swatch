pipenv          := pipenv run

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
	$(pipenv) pytest
# ; --cov=swatch --cov-report=term-missing --cov-fail-under 95

lint:
	$(pipenv) pylint swatch/ tests/

mypy:
	${pipenv} mypy swatch

check: test lint mypy
