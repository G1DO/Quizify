"""Local Flask server for Quizify."""
import os
import uuid
from pathlib import Path
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from werkzeug.utils import secure_filename

from text_extractor import extract_text, TextExtractionError
from question_generator import generate_questions, QuestionGenerationError
from database import (
    save_upload, update_upload_status, save_questions,
    get_upload_by_id, get_questions_by_upload_id, list_uploads
)

app = Flask(__name__, static_folder='static')
CORS(app)

UPLOAD_FOLDER = Path(__file__).parent / 'uploads'
UPLOAD_FOLDER.mkdir(exist_ok=True)

ALLOWED_EXTENSIONS = {'pdf', 'docx', 'doc', 'txt'}


def allowed_file(filename):
    """Check if file extension is allowed."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint."""
    return jsonify({'status': 'healthy'})


@app.route('/upload', methods=['POST'])
def upload_file():
    """Upload and process a file."""
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400

    if not allowed_file(file.filename):
        return jsonify({'error': f'Invalid file type. Allowed: {", ".join(ALLOWED_EXTENSIONS)}'}), 400

    try:
        # Generate upload ID
        upload_id = str(uuid.uuid4())
        filename = secure_filename(file.filename)

        # Save file
        file_path = UPLOAD_FOLDER / f"{upload_id}_{filename}"
        file.save(file_path)

        # Save upload record
        save_upload(upload_id, filename, status='processing')

        # Process in background (for now, process immediately)
        try:
            # Extract text
            text = extract_text(file_path=str(file_path))

            if len(text) < 50:
                raise TextExtractionError("Extracted text is too short. Please upload a document with more content.")

            # Generate questions
            questions_data = generate_questions(text)

            # Save questions
            save_questions(upload_id, filename, questions_data)

            # Update upload status
            update_upload_status(upload_id, 'completed', topic=questions_data.get('topic'))

            return jsonify({
                'success': True,
                'upload_id': upload_id,
                'message': 'Questions generated successfully'
            })

        except (TextExtractionError, QuestionGenerationError) as e:
            update_upload_status(upload_id, 'failed', error=str(e))
            return jsonify({'error': str(e)}), 400

    except Exception as e:
        return jsonify({'error': f'Processing failed: {str(e)}'}), 500


@app.route('/questions/<upload_id>', methods=['GET'])
def get_questions(upload_id):
    """Get questions for a specific upload."""
    upload = get_upload_by_id(upload_id)
    if not upload:
        return jsonify({'error': 'Upload not found'}), 404

    questions = get_questions_by_upload_id(upload_id)

    # Separate MCQs and short questions
    mcqs = [q for q in questions if q.get('type') == 'MCQ']
    short_questions = [q for q in questions if q.get('type') == 'SHORT']

    return jsonify({
        'upload_id': upload_id,
        'status': upload['status'],
        'filename': upload['filename'],
        'topic': upload.get('topic', ''),
        'error': upload.get('error_message'),
        'mcqs': mcqs,
        'short_questions': short_questions,
        'total_questions': len(questions)
    })


@app.route('/uploads', methods=['GET'])
def get_uploads():
    """List all uploads."""
    uploads = list_uploads()
    return jsonify({
        'uploads': uploads,
        'count': len(uploads)
    })


@app.route('/')
def index():
    """Serve frontend."""
    return send_from_directory('static', 'index.html')


@app.route('/<path:path>')
def serve_static(path):
    """Serve static files."""
    return send_from_directory('static', path)


if __name__ == '__main__':
    # Check for Gemini API key
    if not os.environ.get('GEMINI_API_KEY'):
        print("⚠️  Warning: GEMINI_API_KEY environment variable not set!")
        print("   Set it with: export GEMINI_API_KEY='your_key_here'")
        print()

    print("=" * 50)
    print("🚀 Quizify Local Server")
    print("=" * 50)
    print(f"📁 Upload folder: {UPLOAD_FOLDER}")
    print(f"🌐 Server: http://localhost:5000")
    print()
    print("Press Ctrl+C to stop")
    print("=" * 50)

    app.run(debug=True, host='0.0.0.0', port=5000)
