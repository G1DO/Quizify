#!/bin/bash
# Full deployment script for Quizify
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

echo "=========================================="
echo "       Quizify Deployment Script"
echo "=========================================="
echo ""

# Check for required tools
command -v terraform >/dev/null 2>&1 || { echo "Error: terraform is required but not installed."; exit 1; }
command -v aws >/dev/null 2>&1 || { echo "Error: AWS CLI is required but not installed."; exit 1; }
command -v pip >/dev/null 2>&1 || { echo "Error: pip is required but not installed."; exit 1; }
command -v zip >/dev/null 2>&1 || { echo "Error: zip is required but not installed."; exit 1; }

# Check for terraform.tfvars
if [ ! -f "$PROJECT_DIR/terraform/terraform.tfvars" ]; then
    echo "Error: terraform.tfvars not found!"
    echo ""
    echo "Please create terraform/terraform.tfvars with your Gemini API key:"
    echo ""
    echo '  gemini_api_key = "your_api_key_here"'
    echo '  aws_region     = "us-east-1"'
    echo ""
    exit 1
fi

# Step 1: Build Lambda layer
echo "Step 1: Building Lambda layer..."
echo "----------------------------------------"
cd "$PROJECT_DIR/lambda_layer"
./build_layer.sh

# Step 2: Build Lambda code
echo ""
echo "Step 2: Building Lambda code..."
echo "----------------------------------------"
"$SCRIPT_DIR/build_lambda.sh"

# Step 3: Initialize and apply Terraform
echo ""
echo "Step 3: Deploying infrastructure..."
echo "----------------------------------------"
cd "$PROJECT_DIR/terraform"

echo "Initializing Terraform..."
terraform init

echo ""
echo "Planning deployment..."
terraform plan -out=tfplan

echo ""
read -p "Do you want to apply this plan? (y/n) " -n 1 -r
echo ""

if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "Applying Terraform..."
    terraform apply tfplan
    rm tfplan
else
    echo "Deployment cancelled."
    rm tfplan
    exit 0
fi

# Step 4: Upload frontend
echo ""
echo "Step 4: Uploading frontend..."
echo "----------------------------------------"
"$SCRIPT_DIR/upload_frontend.sh"

# Output final information
echo ""
echo "=========================================="
echo "       Deployment Complete!"
echo "=========================================="
echo ""

cd "$PROJECT_DIR/terraform"
echo "API Gateway URL:"
terraform output api_gateway_url
echo ""
echo "Frontend URL:"
echo "http://$(terraform output -raw frontend_url)"
echo ""
echo "To test the API:"
echo "  curl \$(terraform output -raw api_gateway_url)/health"
echo ""
