"""DynamoDB client operations for Quizify."""
import os
import boto3
from boto3.dynamodb.conditions import Key
from utils import generate_uuid, get_timestamp


dynamodb = boto3.resource('dynamodb')

QUESTIONS_TABLE = os.environ.get('DYNAMODB_TABLE', 'quizify-dev-questions')
UPLOADS_TABLE = os.environ.get('UPLOADS_TABLE', 'quizify-dev-uploads')


def get_questions_table():
    """Get the questions DynamoDB table."""
    return dynamodb.Table(QUESTIONS_TABLE)


def get_uploads_table():
    """Get the uploads DynamoDB table."""
    return dynamodb.Table(UPLOADS_TABLE)


def save_upload(upload_id: str, filename: str, s3_key: str, status: str = 'processing') -> dict:
    """Save upload metadata to DynamoDB.

    Args:
        upload_id: Unique upload identifier
        filename: Original filename
        s3_key: S3 object key
        status: Upload status (processing, completed, failed)

    Returns:
        The saved upload item
    """
    table = get_uploads_table()
    timestamp = get_timestamp()

    item = {
        'upload_id': upload_id,
        'filename': filename,
        's3_key': s3_key,
        'status': status,
        'created_at': timestamp,
        'updated_at': timestamp
    }

    table.put_item(Item=item)
    return item


def update_upload_status(upload_id: str, status: str, topic: str = None, error: str = None) -> None:
    """Update the status of an upload.

    Args:
        upload_id: Upload identifier
        status: New status
        topic: Detected topic (if completed)
        error: Error message (if failed)
    """
    table = get_uploads_table()
    timestamp = get_timestamp()

    update_expr = 'SET #status = :status, updated_at = :updated_at'
    expr_values = {
        ':status': status,
        ':updated_at': timestamp
    }
    expr_names = {'#status': 'status'}

    if topic:
        update_expr += ', topic = :topic'
        expr_values[':topic'] = topic

    if error:
        update_expr += ', error_message = :error'
        expr_values[':error'] = error

    table.update_item(
        Key={'upload_id': upload_id},
        UpdateExpression=update_expr,
        ExpressionAttributeValues=expr_values,
        ExpressionAttributeNames=expr_names
    )


def save_questions(upload_id: str, filename: str, questions_data: dict) -> list:
    """Save generated questions to DynamoDB.

    Args:
        upload_id: Upload identifier
        filename: Source filename
        questions_data: Dict containing 'mcqs', 'short_questions', and 'topic'

    Returns:
        List of saved question items
    """
    table = get_questions_table()
    timestamp = get_timestamp()
    topic = questions_data.get('topic', 'General')
    saved_items = []

    # Save MCQs
    for mcq in questions_data.get('mcqs', []):
        question_id = generate_uuid()
        item = {
            'question_id': question_id,
            'upload_id': upload_id,
            'type': 'MCQ',
            'topic': topic,
            'question': mcq['question'],
            'options': mcq.get('options', []),
            'correct_answer': mcq.get('correct_answer', ''),
            'explanation': mcq.get('explanation', ''),
            'filename': filename,
            'created_at': timestamp
        }
        table.put_item(Item=item)
        saved_items.append(item)

    # Save short questions
    for sq in questions_data.get('short_questions', []):
        question_id = generate_uuid()
        item = {
            'question_id': question_id,
            'upload_id': upload_id,
            'type': 'SHORT',
            'topic': topic,
            'question': sq['question'],
            'expected_points': sq.get('expected_points', []),
            'difficulty': sq.get('difficulty', 'medium'),
            'filename': filename,
            'created_at': timestamp
        }
        table.put_item(Item=item)
        saved_items.append(item)

    return saved_items


def get_questions_by_upload_id(upload_id: str) -> list:
    """Get all questions for a specific upload.

    Args:
        upload_id: Upload identifier

    Returns:
        List of question items
    """
    table = get_questions_table()

    response = table.query(
        IndexName='upload_id-created_at-index',
        KeyConditionExpression=Key('upload_id').eq(upload_id)
    )

    return response.get('Items', [])


def get_upload_by_id(upload_id: str) -> dict:
    """Get upload metadata by ID.

    Args:
        upload_id: Upload identifier

    Returns:
        Upload item or None
    """
    table = get_uploads_table()

    response = table.get_item(Key={'upload_id': upload_id})
    return response.get('Item')


def list_uploads(limit: int = 50) -> list:
    """List recent uploads.

    Args:
        limit: Maximum number of uploads to return

    Returns:
        List of upload items sorted by date (newest first)
    """
    table = get_uploads_table()

    response = table.scan(Limit=limit)
    items = response.get('Items', [])

    # Sort by created_at descending
    items.sort(key=lambda x: x.get('created_at', ''), reverse=True)

    return items[:limit]
