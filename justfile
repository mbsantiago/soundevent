# Soundevent Project Justfile
#
# This file defines common development tasks.
# To list available tasks (recipes), run:
#   uv run just --list
#
# To execute a specific task, run:
#   uv run just <recipe_name>
#
# Example:
#   uv run just test
#   uv run just format

# --- Variables ---
# Source directory for the main project code
SRC_DIR := "src/soundevent"

# Directory containing tests
TEST_DIR := "tests"

# Directory for documentation source
DOCS_SRC_DIR := "docs"

# Directory where MkDocs builds the documentation site
DOCS_BUILD_DIR := "site"

# Directory for HTML coverage reports
COVERAGE_HTML_DIR := "htmlcov"

default:
    @just --list

# --- Environment & Setup ---

# Display current Python environment and tool versions for debugging
show-env:
    @echo "--- Python Environment ---"
    @python -V
    @python -m site
    @echo "\n--- Tool Versions ---"
    @echo -n "uv: "
    @uv --version
    @echo -n "Ruff: "
    @ruff --version
    @echo -n "Pytest: "
    @pytest --version
    @echo -n "Pyright: "
    @pyright --version || echo "Pyright: Not found or version check failed. Ensure it's installed in the uv environment."
    @echo -n "MkDocs: "
    @mkdocs --version || echo "MkDocs: Not found. Install if needed for docs."
    @echo -n "Coverage.py: "
    @coverage --version || echo "Coverage.py: Not found. Install if needed for coverage."

# --- Auto-Fixing ---

# Apply Ruff formatting to source and test directories
fix-format:
    @echo "Applying Ruff formatting to '{{SRC_DIR}}' and '{{TEST_DIR}}'..."
    ruff format {{SRC_DIR}} {{TEST_DIR}}

# Apply auto-fixes for Ruff linting issues in source and test directories
fix-issues:
    @echo "Applying auto-fixes for Ruff linting issues in '{{SRC_DIR}}' and '{{TEST_DIR}}'..."
    ruff check --fix-only {{SRC_DIR}} {{TEST_DIR}}

# Apply all auto-fixes: formatting and linting issues
fix: fix-format fix-issues
    @echo "All auto-fixes (formatting and linting) applied."

alias fmt := fix-format
alias format := fix-format

# --- Checks ---

# Check type hints in the source directory using Pyright
check-types:
    @echo "Linting '{{SRC_DIR}}' with Pyright..."
    pyright {{SRC_DIR}}

# Check code style and quality in source and test directories using Ruff linter
check-lint:
    @echo "Linting '{{SRC_DIR}}' and '{{TEST_DIR}}' with Ruff..."
    ruff check {{SRC_DIR}} {{TEST_DIR}}

# Check code formatting consistency in source and test directories using Ruff formatter
check-format:
    @echo "Checking '{{SRC_DIR}}' and '{{TEST_DIR}}' formatting with ruff"
    ruff format --check {{SRC_DIR}} {{TEST_DIR}}

# Run all checks
check: check-lint check-format check-types

# --- Testing ---

# Run tests with pytest-watch for continuous testing with coverage
test-watch:
    @echo "Running tests with pytest-watch (auto-reloads on changes)..."
    ptw --runner "coverage run --source={{SRC_DIR}} -m pytest {{TEST_DIR}}" {{SRC_DIR}} {{TEST_DIR}}

# Run tests using tox
test-tox:
    @echo "Running tox..."
    tox

# Run the main unit test suite with pytest
test-suite:
    @echo "Running unit tests in '{{TEST_DIR}}'..."
    pytest {{TEST_DIR}}

# Run tests embedded within the source code's docstrings
test-docstrings:
    @echo "Running docstring tests in '{{SRC_DIR}}'..."
    pytest --doctest-modules {{SRC_DIR}}

# Run both unit tests and docstring tests
test-all:
    @echo "Running all tests"
    pytest --doctest-modules {{SRC_DIR}} {{TEST_DIR}}

# Common alias for running the main test suite
alias test := test-suite

# --- Coverage ---

# Run tests and generate coverage data for the source directory
coverage-run:
    @echo "Running tests with coverage for '{{SRC_DIR}}'..."
    coverage run --source={{SRC_DIR}} -m pytest --doctest-modules {{TEST_DIR}} {{SRC_DIR}}

# Generate HTML coverage report from existing coverage data
coverage-html: coverage-run
    @echo "Generating HTML coverage report in '{{COVERAGE_HTML_DIR}}'..."
    coverage html -d {{COVERAGE_HTML_DIR}}

# Generate XML coverage report from existing coverage data
coverage-xml: coverage-run
    @echo "Generating XML coverage report in '{{COVERAGE_HTML_DIR}}'..."
    coverage xml

# Open the generated HTML coverage report in the default web browser
coverage-open: coverage-html
    @echo "Attempting to open coverage report ('{{COVERAGE_HTML_DIR}}/index.html') in browser..."
    @python -m webbrowser -t "file://$(pwd)/{{COVERAGE_HTML_DIR}}/index.html"

# Serve the HTML coverage report locally on http://localhost:8000
coverage-serve: coverage-html
    @echo "Serving coverage report at http://localhost:8000 (from '{{COVERAGE_HTML_DIR}}'). Press Ctrl+C to stop."
    python -m http.server --directory {{COVERAGE_HTML_DIR}} 8000

# Common alias to generate coverage and open the report
coverage: coverage-open


# --- Cleaning ---

# Clean Python bytecode (.pyc), cache (__pycache__), and other common temporary files
clean-pycache:
    @echo "Cleaning Python bytecode (.pyc) and cache (__pycache__) directories..."
    @find . -type f -name '*.pyc' -delete
    @find . -type d -name '__pycache__' -exec rm -rf {} +
    @echo "Cleaning other common temporary files (e.g., .cache, .mypy_cache, .ruff_cache)..."
    @rm -rf .cache .mypy_cache .ruff_cache .virtual_documents .ipynb_checkpoints Thumbs.db '*~'

# Clean build artifacts (build, dist, .egg-info directories)
clean-build:
    @echo "Cleaning build artifacts (build, dist, .egg-info)..."
    @rm -rf build dist *.egg-info .pdm-build

# Clean test-related artifacts (pytest cache, tox cache, hypothesis database)
clean-test-cache:
    @echo "Cleaning test-related artifacts (.pytest_cache, .tox, .hypothesis)..."
    @rm -rf .pytest_cache .tox .hypothesis

# Clean coverage artifacts (.coverage data file, XML reports, HTML directory)
clean-coverage-files:
    @echo "Cleaning coverage artifacts ('{{COVERAGE_HTML_DIR}}', .coverage, coverage.xml)..."
    @rm -rf {{COVERAGE_HTML_DIR}} .coverage coverage.xml

# Clean documentation build artifacts (MkDocs site, generated files)
clean-docs-build:
    @echo "Cleaning documentation build artifacts ('{{DOCS_BUILD_DIR}}', '{{DOCS_SRC_DIR}}/_build')..."
    @rm -rf {{DOCS_BUILD_DIR}} {{DOCS_SRC_DIR}}/_build {{DOCS_SRC_DIR}}/generated

# Clean all generated files, build artifacts, and caches
clean: clean-pycache clean-build clean-test-cache clean-coverage-files clean-docs-build
    @echo "All clean operations completed."

# --- Documentation ---

# Build the documentation using MkDocs
docs-build:
    @echo "Building documentation with MkDocs (output to '{{DOCS_BUILD_DIR}}')..."
    mkdocs build --site-dir {{DOCS_BUILD_DIR}}

# Build and then open the main documentation page in the browser
docs-open: docs-build
    @echo "Attempting to open documentation ('{{DOCS_BUILD_DIR}}/index.html') in browser..."
    @python -m webbrowser -t "file://$(pwd)/{{DOCS_BUILD_DIR}}/index.html"

# Serve the documentation locally with live reload on http://localhost:8001
docs-serve:
    @echo "Serving documentation with MkDocs at http://localhost:8001 (live reload). Press Ctrl+C to stop."
    mkdocs serve --dev-addr localhost:8001 --site-dir {{DOCS_BUILD_DIR}}

# Common alias to build and open the documentation
docs: docs-open
