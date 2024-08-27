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
	$(ENV_PREFIX)ruff format $(PROJECT_NAME)/
	$(ENV_PREFIX)ruff format tests/

.PHONY: lint-pyright
lint-pyright:
	$(ENV_PREFIX)pyright $(PROJECT_NAME)/

.PHONY: lint-ruff
lint-ruff:
	$(ENV_PREFIX)ruff check $(PROJECT_NAME)/
	$(ENV_PREFIX)ruff check tests/

.PHONY: lint
lint: lint-pyright lint-ruff

.PHONY: test-watch
test-watch:    ## Run tests and generate coverage report.
	$(ENV_PREFIX)ptw --runner "$(ENV_PREFIX)coverage run -m pytest -l --tb=long tests/" $(PROJECT_NAME)/ tests/

.PHONY: test
test:    ## Run tests and generate coverage report.
	$(ENV_PREFIX)pytest -s -vvv -l --tb=long --maxfail=1 tests/

.PHONY: coverage
coverage:    ## Run tests and generate coverage report.
	$(ENV_PREFIX)coverage run -m pytest tests/

.PHONY: coverage-report
coverage-report: coverage
	$(ENV_PREFIX)coverage html
	xdg-open http://localhost:8000
	$(ENV_PREFIX)python -m http.server --directory htmlcov

.PHONY: tox
tox:
	$(ENV_PREFIX)tox

.PHONY: clean
clean:            ## Clean unused files.
	@find src/ -name '*.pyc' -exec rm -f  \;
	@find src/ -name '__pycache__' -exec rm -rf {} \;
	@find src/ -name 'Thumbs.db' -exec rm -f {} \;
	@find src/ -name '*~' -exec rm -f {} \;
	@rm -rf __pycache__
	@rm -rf .cache
	@rm -rf .mypy_cache
	@rm -rf .ruff_cache
	@rm -rf .virtual_documents
	@rm -rf .ipynb_checkpoints
	@rm -rf .pytest_cache

.PHONY: clean-build
clean-build:
	@rm -rf build
	@rm -rf dist
	@rm -rf *.egg-info
	@rm -rf .pdm-build

.PHONY: clean-test
clean-test:
	@rm -rf .tox/
	@rm -rf .pytest_cache
	@rm -rf .hypothesis

.PHONY: clean-coverage
clean-coverage:
	@rm -rf htmlcov
	@rm -rf .coverage
	@rm -rf coverage.xml

.PHONY: clean-docs
clean-docs:
	@rm -rf site/
	@rm -rf docs/_build
	@rm -rf docs/generated

.PHONY: clean-all
clean-all: clean clean-build clean-test clean-coverage clean-docs

.PHONY: docs
docs:             ## Build the documentation.
	@echo "building documentation ..."
	@$(ENV_PREFIX)mkdocs build
	URL="site/index.html"; xdg-open $$URL || sensible-browser $$URL || x-www-browser $$URL || gnome-open $$URL

.PHONY: docs-serve
docs-serve:             ## Build the documentation and watch for changes.
	@echo "building documentation ..."
	@$(ENV_PREFIX)mkdocs serve --open
