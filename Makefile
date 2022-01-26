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
# ; --cov=src --cov-report=term-missing --cov-fail-under 95

lint:
	$(pipenv) pylint src --reports=y

mypy:
	${pipenv} mypy src

check: test lint mypy
