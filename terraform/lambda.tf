# Lambda layer for Python dependencies
resource "aws_lambda_layer_version" "dependencies" {
  layer_name          = "${local.name_prefix}-dependencies"
  description         = "Python dependencies for Quizify (PyPDF2, python-docx, google-generativeai)"
  compatible_runtimes = ["python3.11"]

  s3_bucket = aws_s3_bucket.lambda_artifacts.id
  s3_key    = aws_s3_object.lambda_layer.key

  depends_on = [aws_s3_object.lambda_layer]
}

# Upload Lambda layer zip to S3
resource "aws_s3_object" "lambda_layer" {
  bucket = aws_s3_bucket.lambda_artifacts.id
  key    = "layers/quizify_layer.zip"
  source = "${path.module}/../lambda_layer/quizify_layer.zip"
  etag   = filemd5("${path.module}/../lambda_layer/quizify_layer.zip")
}

# Upload Lambda code to S3
resource "aws_s3_object" "lambda_code" {
  bucket = aws_s3_bucket.lambda_artifacts.id
  key    = "code/lambda_code.zip"
  source = "${path.module}/../lambda/lambda_code.zip"
  etag   = filemd5("${path.module}/../lambda/lambda_code.zip")
}

# Lambda function
resource "aws_lambda_function" "processor" {
  function_name = "${local.name_prefix}-processor"
  role          = aws_iam_role.lambda_role.arn
  handler       = "handler.lambda_handler"
  runtime       = "python3.11"
  timeout       = 300 # 5 minutes for AI processing
  memory_size   = 512

  s3_bucket = aws_s3_bucket.lambda_artifacts.id
  s3_key    = aws_s3_object.lambda_code.key

  source_code_hash = filebase64sha256("${path.module}/../lambda/lambda_code.zip")

  layers = [aws_lambda_layer_version.dependencies.arn]

  environment {
    variables = {
      GEMINI_API_KEY   = var.gemini_api_key
      DYNAMODB_TABLE   = aws_dynamodb_table.questions.name
      UPLOADS_TABLE    = aws_dynamodb_table.uploads.name
      UPLOADS_BUCKET   = aws_s3_bucket.uploads.id
      AWS_REGION_NAME  = var.aws_region
    }
  }

  depends_on = [
    aws_iam_role_policy.lambda_logs,
    aws_iam_role_policy.lambda_s3,
    aws_iam_role_policy.lambda_dynamodb
  ]
}

# Permission for S3 to invoke Lambda
resource "aws_lambda_permission" "s3_invoke" {
  statement_id  = "AllowS3Invoke"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.processor.function_name
  principal     = "s3.amazonaws.com"
  source_arn    = aws_s3_bucket.uploads.arn
}

# Permission for API Gateway to invoke Lambda
resource "aws_lambda_permission" "api_gateway" {
  statement_id  = "AllowAPIGatewayInvoke"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.processor.function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_apigatewayv2_api.main.execution_arn}/*/*"
}

# CloudWatch Log Group for Lambda
resource "aws_cloudwatch_log_group" "lambda" {
  name              = "/aws/lambda/${aws_lambda_function.processor.function_name}"
  retention_in_days = 14
}
