"""Main Lambda handler for Quizify."""
import json
import os
import urllib.parse

from s3_client import download_file_to_tmp, generate_presigned_url, get_object_content
from text_extractor import extract_text, TextExtractionError
from question_generator import generate_questions, QuestionGenerationError
from dynamodb_client import (
    save_upload,
    update_upload_status,
    save_questions,
    get_questions_by_upload_id,
    get_upload_by_id,
    list_uploads
)
from utils import get_file_extension


UPLOADS_BUCKET = os.environ.get('UPLOADS_BUCKET', '')


def lambda_handler(event, context):
    """Main entry point - routes to appropriate handler."""
    print(f"Received event: {json.dumps(event)}")

    # S3 trigger event
    if 'Records' in event and event['Records']:
        record = event['Records'][0]
        if record.get('eventSource') == 'aws:s3':
            return handle_s3_event(event)

    # API Gateway event
    if 'requestContext' in event:
        return handle_api_event(event)

    # Direct invocation (for testing)
    if 'action' in event:
        return handle_direct_event(event)

    return error_response(400, "Unknown event type")


def handle_s3_event(event):
    """Process uploaded file from S3 trigger."""
    try:
        record = event['Records'][0]
        bucket = record['s3']['bucket']['name']
        key = urllib.parse.unquote_plus(record['s3']['object']['key'])

        print(f"Processing file: s3://{bucket}/{key}")

        # Extract upload_id from key (uploads/{upload_id}/{filename})
        key_parts = key.split('/')
        if len(key_parts) < 3 or key_parts[0] != 'uploads':
            print(f"Skipping non-upload file: {key}")
            return {'statusCode': 200, 'body': 'Skipped'}

        upload_id = key_parts[1]
        filename = key_parts[2]

        # Save upload record
        save_upload(upload_id, filename, key, status='processing')

        # Download and extract text
        print("Downloading file...")
        file_content = get_object_content(bucket, key)

        print("Extracting text...")
        text = extract_text(file_content=file_content, filename=filename)
        print(f"Extracted {len(text)} characters")

        if len(text) < 50:
            raise TextExtractionError("Extracted text is too short. Please upload a document with more content.")

        # Generate questions
        print("Generating questions...")
        questions_data = generate_questions(text)
        print(f"Generated {len(questions_data.get('mcqs', []))} MCQs and {len(questions_data.get('short_questions', []))} short questions")

        # Save questions to DynamoDB
        print("Saving questions...")
        saved = save_questions(upload_id, filename, questions_data)
        print(f"Saved {len(saved)} questions")

        # Update upload status
        update_upload_status(upload_id, 'completed', topic=questions_data.get('topic'))

        return {
            'statusCode': 200,
            'body': json.dumps({
                'message': 'Questions generated successfully',
                'upload_id': upload_id,
                'questions_count': len(saved)
            })
        }

    except TextExtractionError as e:
        print(f"Text extraction error: {str(e)}")
        if 'upload_id' in locals():
            update_upload_status(upload_id, 'failed', error=str(e))
        return error_response(400, f"Text extraction failed: {str(e)}")

    except QuestionGenerationError as e:
        print(f"Question generation error: {str(e)}")
        if 'upload_id' in locals():
            update_upload_status(upload_id, 'failed', error=str(e))
        return error_response(500, f"Question generation failed: {str(e)}")

    except Exception as e:
        print(f"Unexpected error: {str(e)}")
        if 'upload_id' in locals():
            update_upload_status(upload_id, 'failed', error=str(e))
        return error_response(500, f"Processing failed: {str(e)}")


def handle_api_event(event):
    """Handle API Gateway requests."""
    method = event.get('httpMethod', event.get('requestContext', {}).get('http', {}).get('method', ''))
    path = event.get('path', event.get('rawPath', ''))

    print(f"API Request: {method} {path}")

    # GET /presigned-url
    if '/presigned-url' in path and method == 'GET':
        return get_presigned_url_handler(event)

    # GET /questions/{upload_id}
    if '/questions/' in path and method == 'GET':
        return get_questions_handler(event)

    # GET /uploads
    if path.endswith('/uploads') and method == 'GET':
        return list_uploads_handler(event)

    # GET /health
    if '/health' in path:
        return success_response({'status': 'healthy'})

    return error_response(404, f"Not found: {method} {path}")


def handle_direct_event(event):
    """Handle direct Lambda invocations (for testing)."""
    action = event.get('action')

    if action == 'generate_presigned_url':
        filename = event.get('filename', 'test.pdf')
        result = generate_presigned_url(filename)
        return success_response(result)

    if action == 'get_questions':
        upload_id = event.get('upload_id')
        if not upload_id:
            return error_response(400, "upload_id required")
        questions = get_questions_by_upload_id(upload_id)
        return success_response({'questions': questions})

    return error_response(400, f"Unknown action: {action}")


def get_presigned_url_handler(event):
    """Generate presigned URL for file upload."""
    # Get filename from query parameters
    params = event.get('queryStringParameters') or {}
    filename = params.get('filename', 'document.pdf')

    # Validate file extension
    extension = get_file_extension(filename)
    allowed = ['pdf', 'docx', 'doc', 'txt']
    if extension not in allowed:
        return error_response(400, f"Invalid file type. Allowed: {', '.join(allowed)}")

    result = generate_presigned_url(filename)

    return success_response(result)


def get_questions_handler(event):
    """Get questions for a specific upload."""
    # Extract upload_id from path
    path = event.get('path', event.get('rawPath', ''))
    path_params = event.get('pathParameters') or {}

    upload_id = path_params.get('upload_id')
    if not upload_id:
        # Try to extract from path
        parts = path.split('/')
        if 'questions' in parts:
            idx = parts.index('questions')
            if idx + 1 < len(parts):
                upload_id = parts[idx + 1]

    if not upload_id:
        return error_response(400, "upload_id required")

    # Get upload status
    upload = get_upload_by_id(upload_id)
    if not upload:
        return error_response(404, f"Upload not found: {upload_id}")

    # Get questions
    questions = get_questions_by_upload_id(upload_id)

    # Separate MCQs and short questions
    mcqs = [q for q in questions if q.get('type') == 'MCQ']
    short_questions = [q for q in questions if q.get('type') == 'SHORT']

    return success_response({
        'upload_id': upload_id,
        'status': upload.get('status', 'unknown'),
        'filename': upload.get('filename', ''),
        'topic': upload.get('topic', ''),
        'error': upload.get('error_message'),
        'mcqs': mcqs,
        'short_questions': short_questions,
        'total_questions': len(questions)
    })


def list_uploads_handler(event):
    """List all uploads."""
    uploads = list_uploads()

    return success_response({
        'uploads': uploads,
        'count': len(uploads)
    })


def success_response(data: dict):
    """Create a success response."""
    return {
        'statusCode': 200,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Headers': 'Content-Type,Authorization',
            'Access-Control-Allow-Methods': 'GET,POST,PUT,DELETE,OPTIONS'
        },
        'body': json.dumps(data, default=str)
    }


def error_response(status_code: int, message: str):
    """Create an error response."""
    return {
        'statusCode': status_code,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Headers': 'Content-Type,Authorization',
            'Access-Control-Allow-Methods': 'GET,POST,PUT,DELETE,OPTIONS'
        },
        'body': json.dumps({'error': message})
    }
