# Quizify Local Version

Run Quizify completely on your local machine with no cloud costs!

## Features

- Upload PDF, DOCX, or TXT files
- AI-powered question generation using Google Gemini
- SQLite database (no cloud database needed)
- Local file storage
- Simple web interface

## Prerequisites

1. Python 3.11+
2. Google Gemini API key (free tier available)

## Setup

1. **Get a Gemini API key** from [Google AI Studio](https://ai.google.dev/)

2. **Set the API key**:
   ```bash
   export GEMINI_API_KEY='your_api_key_here'
   ```

3. **Run the server**:
   ```bash
   ./run.sh
   ```

   Or manually:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   python3 app.py
   ```

4. **Open your browser**: http://localhost:5000

## Usage

1. Click "Browse Files" or drag and drop a file
2. Click "Generate Questions"
3. Wait 20-60 seconds for AI to generate questions
4. View and study the generated MCQs and short questions!

## Project Structure

```
local/
├── app.py                  # Flask server
├── database.py             # SQLite database
├── text_extractor.py       # Extract text from files
├── question_generator.py   # Gemini AI integration
├── static/                 # Frontend files
│   ├── index.html
│   ├── app.js
│   └── style.css
├── uploads/                # Uploaded files
├── quizify.db              # SQLite database
├── requirements.txt
├── run.sh                  # Startup script
└── README.md
```

## Testing

Try it with the test file:
```bash
# The test file is at ../test_notes.txt
# Upload it through the web interface
```

## Troubleshooting

### "GEMINI_API_KEY not set"
- Make sure you exported the API key in your current terminal session
- Run: `export GEMINI_API_KEY='your_key_here'`

### "Port 5000 already in use"
- Stop any other services using port 5000
- Or change the port in `app.py` (last line)

### Questions not generating
- Check the console for error messages
- Verify your Gemini API key is correct
- Make sure the uploaded file has enough text content (>50 characters)

## Deploying to AWS Later

Once you've tested locally and everything works:
1. Go back to the main Quizify directory
2. Follow the deployment instructions in the main README.md
3. Your code is ready to deploy!

## Cost

- **Local version**: 100% FREE (only uses Gemini free tier)
- **No cloud costs** - everything runs on your machine
