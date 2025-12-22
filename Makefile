setup_venv:
	poetry install --no-root

install_dev: setup_venv

isort:
	poetry run isort src

black:
	poetry run black --config pyproject.toml src

flake8:
	poetry run flake8 src

format: isort black

mypy:
	poetry run mypy --incremental --install-types --show-error-codes --pretty src

test:
	poetry run pytest src

test_cov:
	poetry run coverage run -m pytest src --cov-config=.coveragerc --junit-xml=coverage/junit/test-results.xml --cov-report=html --cov-report=xml
	poetry run coverage html -d coverage/html
	poetry run coverage xml -o coverage/coverage.xml
	poetry run coverage report --show-missing

compile_env:
	poetry lock --no-update

build: isort black flake8 mypy test
