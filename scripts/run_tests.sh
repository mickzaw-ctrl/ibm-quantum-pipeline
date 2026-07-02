#!/bin/bash
# run_tests.sh - Run all tests

set -e

echo "=================================="
echo " IBM Quantum Pipeline - Test Suite"
echo "=================================="
echo ""

# Add src to path
export PYTHONPATH="src:$PYTHONPATH"

# Run pytest
echo "Running pytest..."
python -m pytest tests/ -v --tb=short

echo ""
echo "=================================="
echo " All tests completed!"
echo "=================================="