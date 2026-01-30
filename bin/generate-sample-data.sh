#!/bin/bash
# Generate Sample Context Files for Testing
# Creates representative sample context files demonstrating different migration scenarios

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

echo "Generating sample context files..."
echo "Project root: $PROJECT_ROOT"

# Change to project root
cd "$PROJECT_ROOT"

# Check if python3 is available
if ! command -v python3 &> /dev/null; then
    echo "Error: python3 is not installed or not in PATH."
    exit 1
fi

# Run the generator script
python3 tests/generate_sample_data.py "$@"

echo ""
echo "Sample files are in: examples/context_files/"
