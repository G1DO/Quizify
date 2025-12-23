# Contributing to Quizify

First off, thank you for considering contributing to Quizify! 🎉

It's people like you that make Quizify such a great tool for students everywhere.

## Code of Conduct

This project and everyone participating in it is governed by mutual respect. Please be kind and constructive in your interactions.

## How Can I Contribute?

### Reporting Bugs

Before creating bug reports, please check existing issues. When you are creating a bug report, please include as many details as possible:

* **Use a clear and descriptive title**
* **Describe the exact steps to reproduce the problem**
* **Provide specific examples** (file types, sizes, content)
* **Describe the behavior you observed** vs. what you expected
* **Include screenshots** if applicable
* **Include error messages** from browser console or CloudWatch logs

### Suggesting Enhancements

Enhancement suggestions are tracked as GitHub issues. When creating an enhancement suggestion, please include:

* **Use a clear and descriptive title**
* **Provide a detailed description** of the suggested enhancement
* **Explain why this enhancement would be useful**
* **List any similar features** in other applications

### Your First Code Contribution

Unsure where to begin? You can start by looking for issues tagged with:

* `good first issue` - Issues that should only require a few lines of code
* `help wanted` - Issues that may be more involved

### Pull Requests

1. Fork the repo and create your branch from `main`
2. If you've added code, test it thoroughly
3. If you've changed APIs, update the documentation
4. Ensure your code follows the existing style
5. Write a clear commit message
6. Submit your pull request!

## Development Setup

### Local Development

```bash
# Clone your fork
git clone https://github.com/your-username/quizify.git
cd quizify

# Test locally without AWS
cd local
export GEMINI_API_KEY='your_key'
./run.sh

# Visit http://localhost:5000
```

### Testing Changes

**Frontend Changes:**
1. Test in Chrome, Firefox, and Safari
2. Test on mobile (Chrome DevTools device mode)
3. Verify all interactive features work
4. Check console for errors

**Backend Changes:**
1. Test with various file types (PDF, DOCX, TXT)
2. Test with different file sizes
3. Check CloudWatch Logs for errors
4. Verify DynamoDB records are correct

**Infrastructure Changes:**
1. Run `terraform plan` to preview changes
2. Test in a separate AWS account if possible
3. Document any new variables or outputs

## Style Guidelines

### Python Code

* Follow PEP 8
* Use type hints where beneficial
* Add docstrings to functions
* Keep functions focused and small
* Handle errors gracefully

```python
def generate_questions(text: str, num_mcqs: int = 5) -> dict:
    """Generate questions from text using Gemini AI.

    Args:
        text: The source text
        num_mcqs: Number of MCQs to generate

    Returns:
        Dictionary with 'mcqs' and 'short_questions' keys

    Raises:
        QuestionGenerationError: If generation fails
    """
    # Implementation
```

### JavaScript Code

* Use ES6+ features (const/let, arrow functions, async/await)
* Use meaningful variable names
* Add comments for complex logic
* Keep functions small and focused

```javascript
async handleUpload() {
    if (!this.selectedFile) return;

    try {
        // Step 1: Get presigned URL
        const presignedData = await this.getPresignedUrl();

        // Step 2: Upload to S3
        await this.uploadToS3(presignedData);

        // Step 3: Poll for results
        await this.pollForQuestions();
    } catch (error) {
        this.showError(error.message);
    }
}
```

### Terraform Code

* Use consistent formatting (`terraform fmt`)
* Add descriptions to variables
* Group related resources in separate files
* Use variables for configurable values

```hcl
variable "lambda_timeout" {
  description = "Lambda function timeout in seconds"
  type        = number
  default     = 300
}
```

## Commit Messages

* Use the present tense ("Add feature" not "Added feature")
* Use the imperative mood ("Move cursor to..." not "Moves cursor to...")
* Limit the first line to 72 characters
* Reference issues and pull requests

```
Add PDF password protection check

- Detect encrypted PDFs before processing
- Return helpful error message to user
- Add test cases for encrypted files

Fixes #123
```

## Testing

### Manual Testing Checklist

Before submitting a PR:

- [ ] Test file upload with PDF
- [ ] Test file upload with DOCX
- [ ] Test file upload with TXT
- [ ] Test with small file (<100KB)
- [ ] Test with large file (>1MB)
- [ ] Test quiz mode (click answers)
- [ ] Test tab switching
- [ ] Test past uploads list
- [ ] Test on mobile browser
- [ ] Check browser console for errors
- [ ] Check CloudWatch logs (if backend changes)

### Automated Testing

We welcome contributions to add automated tests:

* Unit tests for Python functions
* Integration tests for Lambda
* Frontend JavaScript tests
* End-to-end tests

## Documentation

* Update README.md if you add/change features
* Add JSDoc comments for JavaScript functions
* Update API documentation if endpoints change
* Add examples for new features

## Questions?

Feel free to ask questions by:
* Opening an issue with the `question` label
* Starting a discussion in GitHub Discussions

## Thank You!

Your contributions help make education more accessible. Thank you for taking the time to contribute! 🙏
