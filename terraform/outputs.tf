output "api_gateway_url" {
  description = "API Gateway endpoint URL"
  value       = aws_apigatewayv2_stage.main.invoke_url
}

output "frontend_bucket" {
  description = "Frontend S3 bucket name"
  value       = aws_s3_bucket.frontend.id
}

output "frontend_url" {
  description = "Frontend website URL (S3 - HTTP only)"
  value       = aws_s3_bucket_website_configuration.frontend.website_endpoint
}

output "frontend_url_https" {
  description = "Frontend CloudFront URL (HTTPS - Use this for mobile)"
  value       = "https://${aws_cloudfront_distribution.frontend.domain_name}"
}

output "cloudfront_domain" {
  description = "CloudFront domain name"
  value       = aws_cloudfront_distribution.frontend.domain_name
}

output "uploads_bucket" {
  description = "Uploads S3 bucket name"
  value       = aws_s3_bucket.uploads.id
}

output "dynamodb_questions_table" {
  description = "DynamoDB questions table name"
  value       = aws_dynamodb_table.questions.name
}

output "dynamodb_uploads_table" {
  description = "DynamoDB uploads table name"
  value       = aws_dynamodb_table.uploads.name
}

output "lambda_function_name" {
  description = "Lambda function name"
  value       = aws_lambda_function.processor.function_name
}

output "aws_region" {
  description = "AWS region"
  value       = var.aws_region
}
