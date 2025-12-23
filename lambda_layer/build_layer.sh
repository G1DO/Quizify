#!/bin/bash
# Build Lambda layer for Quizify dependencies
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

LAYER_DIR="python"
OUTPUT_ZIP="quizify_layer.zip"

echo "=== Building Quizify Lambda Layer ==="

# Clean up previous builds
rm -rf "$LAYER_DIR" "$OUTPUT_ZIP"

# Create directory structure
mkdir -p "$LAYER_DIR"

# Install dependencies
echo "Installing dependencies..."
pip install \
    -r requirements.txt \
    -t "$LAYER_DIR" \
    --platform manylinux2014_x86_64 \
    --only-binary=:all: \
    --implementation cp \
    --python-version 3.11 \
    --upgrade

# Remove unnecessary files to reduce size
echo "Cleaning up unnecessary files..."
find "$LAYER_DIR" -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
find "$LAYER_DIR" -type d -name "*.dist-info" -exec rm -rf {} + 2>/dev/null || true
find "$LAYER_DIR" -type d -name "tests" -exec rm -rf {} + 2>/dev/null || true
find "$LAYER_DIR" -type f -name "*.pyc" -delete 2>/dev/null || true

# Create zip file
echo "Creating zip file..."
zip -r "$OUTPUT_ZIP" "$LAYER_DIR" -x "*.pyc" -x "*__pycache__*"

# Show result
LAYER_SIZE=$(du -h "$OUTPUT_ZIP" | cut -f1)
echo ""
echo "=== Layer built successfully ==="
echo "Output: $OUTPUT_ZIP"
echo "Size: $LAYER_SIZE"
echo ""
echo "Upload to AWS using Terraform or manually"
