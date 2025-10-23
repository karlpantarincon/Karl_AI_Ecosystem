#!/bin/bash

echo "Running system validation..."

# Run tests
echo "Running tests..."
poetry run pytest --cov=corehub --cov=agents --cov-report=term-missing --tb=short -v
if [ $? -ne 0 ]; then
    echo "Tests failed!"
    exit 1
fi
echo "Tests passed."

# Run linting
echo "Running linting..."
poetry run ruff check corehub/ agents/
if [ $? -ne 0 ]; then
    echo "Linting failed!"
    exit 1
fi
echo "Linting passed."

# Run type checking
echo "Running type checking..."
poetry run mypy corehub/ agents/
if [ $? -ne 0 ]; then
    echo "Type checking failed!"
    exit 1
fi
echo "Type checking passed."

echo "All system validations passed successfully!"