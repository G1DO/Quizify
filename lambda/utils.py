"""Utility functions for Quizify Lambda."""
import uuid
from datetime import datetime, timezone


def generate_uuid() -> str:
    """Generate a unique identifier."""
    return str(uuid.uuid4())


def get_timestamp() -> str:
    """Get current UTC timestamp in ISO format."""
    return datetime.now(timezone.utc).isoformat()


def get_file_extension(filename: str) -> str:
    """Extract file extension from filename."""
    if '.' not in filename:
        return ''
    return filename.rsplit('.', 1)[-1].lower()


def clean_text(text: str) -> str:
    """Clean extracted text by removing excessive whitespace."""
    # Replace multiple newlines with double newline
    import re
    text = re.sub(r'\n{3,}', '\n\n', text)
    # Replace multiple spaces with single space
    text = re.sub(r' {2,}', ' ', text)
    # Strip leading/trailing whitespace from each line
    lines = [line.strip() for line in text.split('\n')]
    return '\n'.join(lines).strip()
