# DynamoDB table for storing generated questions
resource "aws_dynamodb_table" "questions" {
  name         = "${local.name_prefix}-questions"
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "question_id"

  attribute {
    name = "question_id"
    type = "S"
  }

  attribute {
    name = "upload_id"
    type = "S"
  }

  attribute {
    name = "created_at"
    type = "S"
  }

  # Global Secondary Index for querying by upload_id
  global_secondary_index {
    name            = "upload_id-created_at-index"
    hash_key        = "upload_id"
    range_key       = "created_at"
    projection_type = "ALL"
  }

  tags = {
    Name = "${local.name_prefix}-questions"
  }
}

# DynamoDB table for tracking uploads
resource "aws_dynamodb_table" "uploads" {
  name         = "${local.name_prefix}-uploads"
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "upload_id"

  attribute {
    name = "upload_id"
    type = "S"
  }

  attribute {
    name = "created_at"
    type = "S"
  }

  # Global Secondary Index for listing uploads by date
  global_secondary_index {
    name            = "created_at-index"
    hash_key        = "created_at"
    projection_type = "ALL"
  }

  tags = {
    Name = "${local.name_prefix}-uploads"
  }
}
