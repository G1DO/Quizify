#!/bin/bash
# Build Lambda deployment package
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
LAMBDA_DIR="$PROJECT_DIR/lambda"

echo "=== Building Lambda Package ==="

cd "$LAMBDA_DIR"

# Clean up
rm -f lambda_code.zip

# Create zip with all Python files
echo "Creating deployment package..."
zip -r lambda_code.zip *.py

# Show result
ZIP_SIZE=$(du -h lambda_code.zip | cut -f1)
echo ""
echo "=== Build Complete ==="
echo "Output: $LAMBDA_DIR/lambda_code.zip"
echo "Size: $ZIP_SIZE"
