# 📚 Quizify - AI-Powered Exam Question Generator

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)
[![Python 3.11](https://img.shields.io/badge/python-3.11-blue.svg)](https://www.python.org/downloads/)
[![Terraform](https://img.shields.io/badge/terraform-1.5+-purple.svg)](https://www.terraform.io/)

> Transform your lecture notes into interactive quiz questions instantly with AI-powered generation.

Quizify is a serverless web application that automatically generates multiple-choice and short-answer questions from your study materials using Google Gemini AI. Perfect for students, educators, and self-learners!

## ✨ Features

- 📄 **Multi-Format Support**: Upload PDF, DOCX, or TXT files
- 🤖 **AI-Powered**: Uses Google Gemini 2.5 Flash for intelligent question generation
- ❓ **Multiple Question Types**:
  - Multiple Choice Questions (MCQs) with 4 options
  - Short Answer Questions with expected key points
- 💡 **Explanations**: Each MCQ includes an explanation for the correct answer
- 🎯 **Interactive Quiz Mode**: Test yourself before revealing answers
- 📱 **Responsive Design**: Works seamlessly on desktop and mobile
- 🔒 **Secure**: HTTPS with CloudFront CDN
- 💾 **History**: View and revisit past uploads
- 💰 **Cost-Effective**: Serverless architecture, pay only for what you use

## 🏗️ Architecture

```
┌─────────┐      HTTPS      ┌────────────┐
│ Browser │ ◄──────────────► │ CloudFront │
└─────────┘                  └──────┬─────┘
                                    │
                                    ▼
                            ┌───────────────┐
                            │  S3 (Static)  │
                            │   Frontend    │
                            └───────────────┘
                                    │
                                    │ CORS
                                    ▼
┌──────────────┐           ┌───────────────┐
│    Gemini    │◄──────────┤  API Gateway  │
│      AI      │           └───────┬───────┘
└──────────────┘                   │
                                   ▼
                           ┌───────────────┐
                           │    Lambda     │
                           │  (Python 3.11)│
                           └───┬───────┬───┘
                               │       │
                ┌──────────────┘       └──────────────┐
                ▼                                     ▼
        ┌───────────────┐                   ┌────────────────┐
        │  S3 (Uploads) │                   │   DynamoDB     │
        │   + Trigger   │                   │   Questions    │
        └───────────────┘                   └────────────────┘
```

### How It Works

1. **Upload**: User uploads a document through the web interface
2. **Presigned URL**: Frontend requests a secure S3 upload URL from API Gateway
3. **S3 Storage**: File is uploaded directly to S3
4. **Lambda Trigger**: S3 triggers Lambda function automatically
5. **Processing**: Lambda extracts text and calls Gemini AI
6. **Question Generation**: Gemini analyzes content and generates questions
7. **Storage**: Questions are saved to DynamoDB
8. **Retrieval**: Frontend polls for results and displays questions

## 🚀 Quick Start

### Prerequisites

- [AWS CLI](https://aws.amazon.com/cli/) configured with credentials
- [Terraform](https://www.terraform.io/downloads) v1.5+
- [Python 3.11](https://www.python.org/downloads/)
- [Google Gemini API Key](https://ai.google.dev/) (free tier available)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/quizify.git
   cd quizify
   ```

2. **Get a Gemini API Key**
   - Visit [Google AI Studio](https://ai.google.dev/)
   - Sign in and create an API key
   - Copy the key for the next step

3. **Configure Terraform**
   ```bash
   cp terraform/terraform.tfvars.example terraform/terraform.tfvars
   ```

   Edit `terraform/terraform.tfvars`:
   ```hcl
   gemini_api_key = "your_actual_api_key_here"
   aws_region     = "us-east-1"
   ```

4. **Deploy to AWS**
   ```bash
   chmod +x scripts/*.sh
   ./scripts/deploy.sh
   ```

   This will:
   - Build Lambda layer with dependencies
   - Package Lambda code
   - Create AWS infrastructure (S3, Lambda, DynamoDB, API Gateway, CloudFront)
   - Upload frontend files

5. **Access Your App**

   After deployment, you'll see:
   ```
   Frontend URL (HTTPS): https://xxxxxx.cloudfront.net
   API URL: https://xxxxxx.execute-api.us-east-1.amazonaws.com/
   ```

   Open the Frontend URL in your browser!

## 📖 Usage

1. **Upload Notes**: Click "Browse Files" or drag & drop your study materials
2. **Generate**: Click "Generate Questions" and wait 20-60 seconds
3. **Study**: Review MCQs and short answer questions
4. **Quiz Mode**: Click on options to reveal answers and explanations
5. **History**: Access past uploads from "Recent Uploads" section

## 🛠️ Development

### Project Structure

```
quizify/
├── lambda/                     # Backend Lambda function
│   ├── handler.py             # Main entry point & routing
│   ├── text_extractor.py      # PDF/DOCX/TXT text extraction
│   ├── question_generator.py  # Gemini AI integration
│   ├── dynamodb_client.py     # Database operations
│   ├── s3_client.py           # S3 presigned URLs
│   └── utils.py               # Helper functions
│
├── lambda_layer/              # Lambda dependencies layer
│   ├── build_layer.sh         # Build script
│   └── requirements.txt       # PyPDF2, python-docx, google-generativeai
│
├── frontend/                  # Web interface
│   ├── index.html            # Main page structure
│   ├── style.css             # Modern styling
│   ├── app.js                # Interactive functionality
│   └── config.js             # Auto-generated API config
│
├── terraform/                # Infrastructure as Code
│   ├── main.tf              # Main configuration
│   ├── providers.tf         # AWS provider
│   ├── variables.tf         # Input variables
│   ├── outputs.tf           # Output values
│   ├── s3.tf                # S3 buckets
│   ├── lambda.tf            # Lambda function & layer
│   ├── dynamodb.tf          # DynamoDB tables
│   ├── api_gateway.tf       # HTTP API
│   ├── cloudfront.tf        # CDN for HTTPS
│   └── iam.tf               # IAM roles & policies
│
├── local/                    # Local development version
│   ├── app.py               # Flask server
│   ├── database.py          # SQLite backend
│   ├── run.sh               # Local startup script
│   └── static/              # Frontend files
│
└── scripts/                  # Deployment automation
    ├── deploy.sh            # Full deployment
    ├── build_lambda.sh      # Package Lambda
    └── upload_frontend.sh   # Sync frontend to S3
```

### Local Development

For quick testing without AWS:

```bash
cd local
export GEMINI_API_KEY='your_key_here'
./run.sh
```

Visit `http://localhost:5000`

### API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/health` | Health check |
| `GET` | `/presigned-url?filename=X` | Get S3 upload URL & upload_id |
| `GET` | `/questions/{upload_id}` | Retrieve generated questions |
| `GET` | `/uploads` | List all past uploads |

### Making Changes

**Update Lambda Code:**
```bash
./scripts/build_lambda.sh
cd terraform && terraform apply
```

**Update Frontend:**
```bash
./scripts/upload_frontend.sh
```

**Clear CloudFront Cache:**
```bash
aws cloudfront create-invalidation \
  --distribution-id YOUR_DIST_ID \
  --paths "/*"
```

## 🤝 Contributing

Contributions are welcome! Please follow these guidelines:

### Getting Started

1. **Fork** the repository
2. **Clone** your fork:
   ```bash
   git clone https://github.com/your-username/quizify.git
   ```
3. **Create a branch**:
   ```bash
   git checkout -b feature/your-feature-name
   ```

### Code Style

- **Python**: Follow PEP 8 guidelines
- **JavaScript**: Use ES6+ features, consistent indentation
- **Terraform**: Use consistent formatting (`terraform fmt`)
- Add comments for complex logic
- Write descriptive commit messages

### Testing

Before submitting:

1. **Test locally** using the local development server
2. **Test Lambda** functions with sample files
3. **Verify** frontend changes in multiple browsers
4. **Check** that existing functionality still works

### Pull Request Process

1. Update README.md if you've added features
2. Ensure all tests pass
3. Update documentation as needed
4. Submit PR with clear description of changes
5. Link any related issues

### Areas for Contribution

- 🎨 **UI/UX improvements**: Better design, animations
- 🌍 **Internationalization**: Multi-language support
- 📊 **Analytics**: Usage statistics, question difficulty analysis
- 🔍 **Search**: Find past questions by topic/keyword
- 📤 **Export**: PDF/CSV export of questions
- 🎓 **Study modes**: Flashcards, spaced repetition
- 🧪 **Testing**: Unit tests, integration tests
- 📱 **Mobile app**: Native iOS/Android apps
- 🔒 **Auth**: User accounts and authentication
- 📈 **Progress tracking**: Study progress and scores

## 💰 Cost Estimation

With AWS Free Tier, this should be **free or very low cost**:

| Service | Free Tier | Typical Monthly Usage |
|---------|-----------|----------------------|
| Lambda | 1M requests, 400K GB-seconds | ~1,000 uploads |
| S3 | 5GB storage, 20K GET requests | Minimal |
| DynamoDB | 25GB storage, 25 read/write units | Minimal |
| API Gateway | 1M requests | ~1,000 uploads |
| CloudFront | 1TB data transfer | Minimal |
| Gemini AI | 60 requests/minute | Free tier |

**Estimated cost after free tier**: $0.50 - $2.00/month for moderate use

## 🔧 Troubleshooting

### Lambda Timeout

**Problem**: Large files timeout during processing

**Solution**: Increase timeout in `terraform/lambda.tf`:
```hcl
timeout = 600  # 10 minutes
```

### Text Extraction Fails

**Problem**: "Failed to extract text"

**Solutions**:
- Ensure PDF isn't password-protected
- Scanned PDFs (images) need OCR - not currently supported
- File must have selectable text

### Questions Not Generating

**Problem**: Upload succeeds but no questions appear

**Solutions**:
1. Check CloudWatch Logs:
   ```bash
   aws logs tail /aws/lambda/quizify-dev-processor --follow
   ```
2. Verify Gemini API key is correct
3. Ensure uploaded text is substantial (>50 characters)
4. Check Gemini API quotas

### CORS Errors

**Problem**: "Failed to fetch" or CORS errors

**Solution**: CloudFront cache may be stale. Invalidate:
```bash
aws cloudfront create-invalidation \
  --distribution-id $(cd terraform && terraform output -raw cloudfront_domain) \
  --paths "/*"
```

## 🔒 Security

- **HTTPS Only**: All traffic encrypted via CloudFront
- **Presigned URLs**: Secure S3 uploads with expiration
- **IAM Policies**: Least-privilege access for Lambda
- **Input Validation**: Files validated before processing
- **No Secrets in Code**: All sensitive data in environment variables

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [Google Gemini](https://ai.google.dev/) for AI question generation
- [AWS Free Tier](https://aws.amazon.com/free/) for hosting
- [Terraform](https://www.terraform.io/) for infrastructure management

## 📧 Contact

For questions or suggestions:
- **Issues**: [GitHub Issues](https://github.com/yourusername/quizify/issues)
- **Discussions**: [GitHub Discussions](https://github.com/yourusername/quizify/discussions)

---

**Made with ❤️ for students everywhere**

*Star ⭐ this repo if you find it helpful!*
