.ONESHELL:
ENV_PREFIX=.venv/bin/
PROJECT_NAME=src/soundevent

.PHONY: help
help:             ## Show the help.
	@echo "Usage: make <target>"
	@echo ""
	@echo "Targets:"
	@fgrep "##" Makefile | fgrep -v fgrep


.PHONY: show
show:             ## Show the current environment.
	@echo "Current environment:"
	@echo "Running using $(ENV_PREFIX)"
	@$(ENV_PREFIX)python -V
	@$(ENV_PREFIX)python -m site

.PHONY: install
install:          ## Install the project in dev mode.
	@echo "Don't forget to run 'make virtualenv' if you got errors."
	$(ENV_PREFIX)pip install -e .[test]

.PHONY: fmt
fmt:              ## Format code using black & isort.
	$(ENV_PREFIX)isort $(PROJECT_NAME)/
	$(ENV_PREFIX)black $(PROJECT_NAME)/
	$(ENV_PREFIX)black tests/

.PHONY: lint
lint:             ## Run ruff, black, mypy linters.
	$(ENV_PREFIX)ruff $(PROJECT_NAME)/
	$(ENV_PREFIX)black --check $(PROJECT_NAME)/
	$(ENV_PREFIX)black --check tests/
	$(ENV_PREFIX)mypy $(PROJECT_NAME)/

.PHONY: test
test: lint        ## Run tests and generate coverage report.
	$(ENV_PREFIX)pytest -v --cov-config .coveragerc --cov=$(PROJECT_NAME)/ -l --tb=short --maxfail=1 tests/
	$(ENV_PREFIX)coverage xml
	$(ENV_PREFIX)coverage html

.PHONY: tox
tox:
	$(ENV_PREFIX)tox

.PHONY: watch
watch:            ## Run tests on every change.
	ls **/**.py | entr $(ENV_PREFIX)pytest -s -vvv -l --tb=long --maxfail=1 tests/

.PHONY: clean
clean:            ## Clean unused files.
	@find src/ -name '*.pyc' -exec rm -f  \;
	@find src/ -name '__pycache__' -exec rm -rf {} \;
	@find src/ -name 'Thumbs.db' -exec rm -f {} \;
	@find src/ -name '*~' -exec rm -f {} \;
	@rm -rf .cache
	@rm -rf .pytest_cache
	@rm -rf .mypy_cache
	@rm -rf build
	@rm -rf dist
	@rm -rf *.egg-info
	@rm -rf htmlcov
	@rm -rf .tox/
	@rm -rf docs/_build

.PHONY: docs
docs:             ## Build the documentation.
	@echo "building documentation ..."
	@$(ENV_PREFIX)mkdocs build
	URL="site/index.html"; xdg-open $$URL || sensible-browser $$URL || x-www-browser $$URL || gnome-open $$URL

.PHONY: docs-serve
docs-serve:             ## Build the documentation and watch for changes.
	@echo "building documentation ..."
	URL="http://localhost:8000/soundevent/"; xdg-open $$URL || sensible-browser $$URL || x-www-browser $$URL || gnome-open $$URL
	@$(ENV_PREFIX)mkdocs serve

.PHONY: init
init:             ## Initialize the project based on an application template.
	@./.github/init.sh
