# API Gateway HTTP API
resource "aws_apigatewayv2_api" "main" {
  name          = "${local.name_prefix}-api"
  protocol_type = "HTTP"

  cors_configuration {
    allow_origins = ["*"] # Restrict in production
    allow_methods = ["GET", "POST", "PUT", "DELETE", "OPTIONS"]
    allow_headers = ["Content-Type", "Authorization", "X-Requested-With"]
    max_age       = 300
  }
}

# API Gateway stage
resource "aws_apigatewayv2_stage" "main" {
  api_id      = aws_apigatewayv2_api.main.id
  name        = "$default"
  auto_deploy = true

  access_log_settings {
    destination_arn = aws_cloudwatch_log_group.api_gateway.arn
    format = jsonencode({
      requestId      = "$context.requestId"
      ip             = "$context.identity.sourceIp"
      requestTime    = "$context.requestTime"
      httpMethod     = "$context.httpMethod"
      routeKey       = "$context.routeKey"
      status         = "$context.status"
      responseLength = "$context.responseLength"
    })
  }
}

# Lambda integration
resource "aws_apigatewayv2_integration" "lambda" {
  api_id             = aws_apigatewayv2_api.main.id
  integration_type   = "AWS_PROXY"
  integration_uri    = aws_lambda_function.processor.invoke_arn
  integration_method = "POST"
}

# Route: GET /presigned-url
resource "aws_apigatewayv2_route" "presigned_url" {
  api_id    = aws_apigatewayv2_api.main.id
  route_key = "GET /presigned-url"
  target    = "integrations/${aws_apigatewayv2_integration.lambda.id}"
}

# Route: GET /questions/{upload_id}
resource "aws_apigatewayv2_route" "get_questions" {
  api_id    = aws_apigatewayv2_api.main.id
  route_key = "GET /questions/{upload_id}"
  target    = "integrations/${aws_apigatewayv2_integration.lambda.id}"
}

# Route: GET /uploads (list all uploads)
resource "aws_apigatewayv2_route" "list_uploads" {
  api_id    = aws_apigatewayv2_api.main.id
  route_key = "GET /uploads"
  target    = "integrations/${aws_apigatewayv2_integration.lambda.id}"
}

# Route: GET /health
resource "aws_apigatewayv2_route" "health" {
  api_id    = aws_apigatewayv2_api.main.id
  route_key = "GET /health"
  target    = "integrations/${aws_apigatewayv2_integration.lambda.id}"
}

# CloudWatch Log Group for API Gateway
resource "aws_cloudwatch_log_group" "api_gateway" {
  name              = "/aws/apigateway/${local.name_prefix}-api"
  retention_in_days = 14
}
