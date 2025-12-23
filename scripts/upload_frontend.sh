#!/bin/bash
# Upload frontend files to S3
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
FRONTEND_DIR="$PROJECT_DIR/frontend"
TERRAFORM_DIR="$PROJECT_DIR/terraform"

echo "=== Uploading Frontend ==="

# Get bucket name from Terraform
cd "$TERRAFORM_DIR"
FRONTEND_BUCKET=$(terraform output -raw frontend_bucket 2>/dev/null || echo "")
API_URL=$(terraform output -raw api_gateway_url 2>/dev/null || echo "")

if [ -z "$FRONTEND_BUCKET" ]; then
    echo "Error: Could not get frontend bucket name from Terraform"
    echo "Make sure you have run 'terraform apply' first"
    exit 1
fi

echo "Frontend bucket: $FRONTEND_BUCKET"
echo "API URL: $API_URL"

# Remove trailing slash from API URL if present
API_URL="${API_URL%/}"

# Update config.js with API URL
cd "$FRONTEND_DIR"
cat > config.js << EOF
// Quizify Configuration
// This file is updated automatically by the deployment script
const QUIZIFY_CONFIG = {
    API_URL: '${API_URL}',
    POLL_INTERVAL: 2000,
    MAX_POLL_ATTEMPTS: 60
};
EOF

echo "Updated config.js with API URL"

# Sync frontend files to S3
echo "Syncing files to S3..."
aws s3 sync . "s3://${FRONTEND_BUCKET}/" \
    --exclude ".git/*" \
    --exclude "*.md" \
    --delete

# Get website URL
FRONTEND_URL=$(cd "$TERRAFORM_DIR" && terraform output -raw frontend_url 2>/dev/null || echo "")

echo ""
echo "=== Frontend Uploaded ==="
echo "Website URL: http://${FRONTEND_URL}"
