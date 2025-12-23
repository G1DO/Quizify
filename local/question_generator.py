"""Question generation using Google Gemini API."""
import os
import json
import re
from typing import Optional


class QuestionGenerationError(Exception):
    """Error during question generation."""
    pass


def initialize_gemini():
    """Initialize Gemini client."""
    try:
        import google.generativeai as genai

        api_key = os.environ.get('GEMINI_API_KEY')
        if not api_key:
            raise QuestionGenerationError("GEMINI_API_KEY environment variable not set")

        genai.configure(api_key=api_key)
        return genai.GenerativeModel('models/gemini-2.5-flash')

    except ImportError:
        raise QuestionGenerationError("google-generativeai library not available")


def generate_questions(
    text: str,
    num_mcqs: int = 5,
    num_short: int = 5,
    topic: Optional[str] = None
) -> dict:
    """Generate MCQs and short questions from text.

    Args:
        text: The source text to generate questions from
        num_mcqs: Number of MCQs to generate
        num_short: Number of short questions to generate
        topic: Optional topic override (auto-detected if not provided)

    Returns:
        dict with 'mcqs', 'short_questions', and 'topic' keys
    """
    model = initialize_gemini()

    # Truncate text if too long (Gemini has token limits)
    max_chars = 30000
    if len(text) > max_chars:
        text = text[:max_chars] + "\n\n[Text truncated due to length...]"

    prompt = f"""You are an expert exam question generator for educational purposes.

Analyze the following study notes and generate high-quality exam questions.

REQUIREMENTS:
1. Generate exactly {num_mcqs} Multiple Choice Questions (MCQs)
2. Generate exactly {num_short} Short Answer Questions
3. Questions should test understanding, not just memorization
4. MCQs should have 4 options each (A, B, C, D)
5. Identify the main topic from the content

IMPORTANT: Respond ONLY with valid JSON in this exact format:
{{
    "topic": "Main Topic Name",
    "mcqs": [
        {{
            "question": "The question text?",
            "options": ["A) First option", "B) Second option", "C) Third option", "D) Fourth option"],
            "correct_answer": "A",
            "explanation": "Brief explanation of why this is correct"
        }}
    ],
    "short_questions": [
        {{
            "question": "The short answer question?",
            "expected_points": ["Key point 1", "Key point 2"],
            "difficulty": "medium"
        }}
    ]
}}

STUDY NOTES:
{text}

Remember: Output ONLY valid JSON, no additional text or markdown."""

    try:
        response = model.generate_content(prompt)
        return parse_gemini_response(response.text, topic)

    except Exception as e:
        raise QuestionGenerationError(f"Gemini API error: {str(e)}")


def parse_gemini_response(response_text: str, override_topic: Optional[str] = None) -> dict:
    """Parse Gemini response and extract questions.

    Args:
        response_text: Raw text response from Gemini
        override_topic: Optional topic to use instead of detected one

    Returns:
        Parsed question data
    """
    # Try to extract JSON from the response
    text = response_text.strip()

    # Remove markdown code blocks if present
    if text.startswith('```'):
        # Find the end of the code block
        lines = text.split('\n')
        # Remove first line (```json or ```)
        if lines[0].startswith('```'):
            lines = lines[1:]
        # Remove last line if it's ```
        if lines and lines[-1].strip() == '```':
            lines = lines[:-1]
        text = '\n'.join(lines)

    # Try to find JSON object in the text
    json_match = re.search(r'\{[\s\S]*\}', text)
    if json_match:
        text = json_match.group()

    try:
        data = json.loads(text)
    except json.JSONDecodeError as e:
        raise QuestionGenerationError(f"Failed to parse Gemini response as JSON: {str(e)}\nResponse: {response_text[:500]}")

    # Validate and normalize the response
    result = {
        'topic': override_topic or data.get('topic', 'General'),
        'mcqs': [],
        'short_questions': []
    }

    # Process MCQs
    for mcq in data.get('mcqs', []):
        if not isinstance(mcq, dict):
            continue
        if 'question' not in mcq or 'options' not in mcq:
            continue

        result['mcqs'].append({
            'question': mcq['question'],
            'options': mcq.get('options', []),
            'correct_answer': mcq.get('correct_answer', ''),
            'explanation': mcq.get('explanation', '')
        })

    # Process short questions
    for sq in data.get('short_questions', []):
        if not isinstance(sq, dict):
            continue
        if 'question' not in sq:
            continue

        result['short_questions'].append({
            'question': sq['question'],
            'expected_points': sq.get('expected_points', sq.get('expected_answer_points', [])),
            'difficulty': sq.get('difficulty', 'medium')
        })

    if not result['mcqs'] and not result['short_questions']:
        raise QuestionGenerationError("No valid questions were generated")

    return result
