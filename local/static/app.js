/**
 * Quizify Local Frontend Application
 */
class QuizifyApp {
    constructor() {
        // DOM Elements
        this.dropZone = document.getElementById('dropZone');
        this.fileInput = document.getElementById('fileInput');
        this.selectedFileDiv = document.getElementById('selectedFile');
        this.fileNameSpan = document.getElementById('fileName');
        this.removeFileBtn = document.getElementById('removeFile');
        this.generateBtn = document.getElementById('generateBtn');

        this.statusSection = document.getElementById('statusSection');
        this.statusText = document.getElementById('statusText');

        this.resultsSection = document.getElementById('resultsSection');
        this.topicTitle = document.getElementById('topicTitle');
        this.fileInfo = document.getElementById('fileInfo');
        this.mcqContainer = document.getElementById('mcqContainer');
        this.shortContainer = document.getElementById('shortContainer');
        this.newUploadBtn = document.getElementById('newUploadBtn');

        this.pastUploadsContainer = document.getElementById('pastUploadsContainer');

        // State
        this.selectedFile = null;
        this.currentUploadId = null;

        // API URL
        this.apiUrl = 'http://localhost:5000';

        // Initialize
        this.initEventListeners();
        this.loadPastUploads();
    }

    initEventListeners() {
        // Drag and drop
        this.dropZone.addEventListener('dragover', (e) => this.handleDragOver(e));
        this.dropZone.addEventListener('dragleave', (e) => this.handleDragLeave(e));
        this.dropZone.addEventListener('drop', (e) => this.handleDrop(e));

        // File input
        this.fileInput.addEventListener('change', (e) => this.handleFileSelect(e));
        this.dropZone.addEventListener('click', (e) => {
            // Only trigger if not clicking on the label or input itself
            if (e.target === this.dropZone || e.target.closest('.upload-icon') || e.target.tagName === 'P' || e.target.tagName === 'svg') {
                this.fileInput.click();
            }
        });

        // Remove file
        this.removeFileBtn.addEventListener('click', (e) => {
            e.stopPropagation();
            this.clearSelectedFile();
        });

        // Generate button
        this.generateBtn.addEventListener('click', () => this.handleUpload());

        // New upload button
        this.newUploadBtn.addEventListener('click', () => this.resetToUpload());
    }

    handleDragOver(e) {
        e.preventDefault();
        this.dropZone.classList.add('dragover');
    }

    handleDragLeave(e) {
        e.preventDefault();
        this.dropZone.classList.remove('dragover');
    }

    handleDrop(e) {
        e.preventDefault();
        this.dropZone.classList.remove('dragover');

        const files = e.dataTransfer.files;
        if (files.length > 0) {
            this.setSelectedFile(files[0]);
        }
    }

    handleFileSelect(e) {
        const files = e.target.files;
        if (files.length > 0) {
            this.setSelectedFile(files[0]);
        }
    }

    setSelectedFile(file) {
        // Validate file type
        const allowedExtensions = ['.pdf', '.docx', '.doc', '.txt'];
        const hasValidExtension = allowedExtensions.some(ext => file.name.toLowerCase().endsWith(ext));

        if (!hasValidExtension) {
            alert('Please select a PDF, DOCX, or TXT file.');
            return;
        }

        this.selectedFile = file;
        this.fileNameSpan.textContent = file.name;
        this.selectedFileDiv.style.display = 'flex';
        this.generateBtn.disabled = false;
    }

    clearSelectedFile() {
        this.selectedFile = null;
        this.fileInput.value = '';
        this.selectedFileDiv.style.display = 'none';
        this.generateBtn.disabled = true;
    }

    async handleUpload() {
        if (!this.selectedFile) return;

        try {
            // Show status
            this.showStatus('Uploading and processing file...');

            // Create form data
            const formData = new FormData();
            formData.append('file', this.selectedFile);

            // Upload file
            const response = await fetch(`${this.apiUrl}/upload`, {
                method: 'POST',
                body: formData
            });

            if (!response.ok) {
                const error = await response.json();
                throw new Error(error.error || 'Upload failed');
            }

            const data = await response.json();
            this.currentUploadId = data.upload_id;

            // Fetch and display questions
            this.showStatus('Loading questions...');
            const questions = await this.fetchQuestions(data.upload_id);
            this.displayQuestions(questions);
            this.loadPastUploads(); // Refresh list

        } catch (error) {
            console.error('Upload error:', error);
            this.showError(error.message || 'An error occurred. Please try again.');
        }
    }

    async fetchQuestions(uploadId) {
        const response = await fetch(`${this.apiUrl}/questions/${uploadId}`);

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.error || 'Failed to fetch questions');
        }

        return response.json();
    }

    displayQuestions(data) {
        // Hide status, show results
        this.statusSection.style.display = 'none';
        this.resultsSection.style.display = 'block';
        document.querySelector('.upload-section-modern').style.display = 'none';

        // Set header
        this.topicTitle.textContent = data.topic || 'Generated Questions';
        this.fileInfo.textContent = `From: ${data.filename} | ${data.total_questions} questions`;

        // Display MCQs
        this.mcqContainer.innerHTML = '';
        if (data.mcqs && data.mcqs.length > 0) {
            data.mcqs.forEach((mcq, index) => {
                this.mcqContainer.appendChild(this.createMCQCard(mcq, index + 1));
            });
        } else {
            this.mcqContainer.innerHTML = '<p class="empty-text">No MCQs generated</p>';
        }

        // Display short questions
        this.shortContainer.innerHTML = '';
        if (data.short_questions && data.short_questions.length > 0) {
            data.short_questions.forEach((sq, index) => {
                this.shortContainer.appendChild(this.createShortQuestionCard(sq, index + 1));
            });
        } else {
            this.shortContainer.innerHTML = '<p class="empty-text">No short questions generated</p>';
        }

        // Initialize tab switching
        this.initTabs();
    }

    createMCQCard(mcq, number) {
        const card = document.createElement('div');
        card.className = 'question-card';

        const optionsHtml = mcq.options.map((opt, index) => {
            const isCorrect = opt.startsWith(mcq.correct_answer + ')') || opt.startsWith(mcq.correct_answer + ' ');
            return `<li class="option" data-correct="${isCorrect}" data-index="${index}">${this.escapeHtml(opt)}</li>`;
        }).join('');

        card.innerHTML = `
            <div class="question-number">Question ${number}</div>
            <div class="question-text">${this.escapeHtml(mcq.question)}</div>
            <ul class="options-list">${optionsHtml}</ul>
            ${mcq.explanation ? `
                <div class="explanation" style="display: none;">
                    <strong>Explanation:</strong>
                    ${this.escapeHtml(mcq.explanation)}
                </div>
            ` : ''}
            <div class="quiz-feedback" style="display: none;"></div>
        `;

        // Add click handlers to options
        const optionsList = card.querySelector('.options-list');
        const explanation = card.querySelector('.explanation');
        const feedback = card.querySelector('.quiz-feedback');

        optionsList.addEventListener('click', (e) => {
            const clickedOption = e.target.closest('.option');
            if (!clickedOption || clickedOption.classList.contains('answered')) return;

            const isCorrect = clickedOption.dataset.correct === 'true';

            // Mark all options as answered (disable further clicks)
            optionsList.querySelectorAll('.option').forEach(opt => {
                opt.classList.add('answered');
                if (opt.dataset.correct === 'true') {
                    opt.classList.add('correct');
                }
            });

            // Mark selected option
            clickedOption.classList.add('selected');
            if (!isCorrect) {
                clickedOption.classList.add('wrong');
            }

            // Show feedback
            if (feedback) {
                feedback.style.display = 'block';
                feedback.className = `quiz-feedback ${isCorrect ? 'correct-feedback' : 'wrong-feedback'}`;
                feedback.textContent = isCorrect ? '✓ Correct!' : '✗ Incorrect';
            }

            // Show explanation
            if (explanation) {
                explanation.style.display = 'block';
            }
        });

        return card;
    }

    createShortQuestionCard(sq, number) {
        const card = document.createElement('div');
        card.className = 'question-card';

        const pointsHtml = sq.expected_points && sq.expected_points.length > 0
            ? `<div class="expected-points">
                <strong>Expected Answer Points:</strong>
                <ul>${sq.expected_points.map(p => `<li>${this.escapeHtml(p)}</li>`).join('')}</ul>
               </div>`
            : '';

        card.innerHTML = `
            <div class="question-number">Question ${number}</div>
            <div class="question-text">${this.escapeHtml(sq.question)}</div>
            ${pointsHtml}
            <span class="difficulty-badge ${sq.difficulty || 'medium'}">${(sq.difficulty || 'medium').toUpperCase()}</span>
        `;

        return card;
    }

    async loadPastUploads() {
        try {
            const response = await fetch(`${this.apiUrl}/uploads`);

            if (!response.ok) {
                throw new Error('Failed to load uploads');
            }

            const data = await response.json();
            this.displayPastUploads(data.uploads || []);

        } catch (error) {
            console.error('Error loading past uploads:', error);
            this.pastUploadsContainer.innerHTML = '<p class="empty-text">Unable to load recent uploads</p>';
        }
    }

    displayPastUploads(uploads) {
        if (uploads.length === 0) {
            this.pastUploadsContainer.innerHTML = '<p class="empty-text">No uploads yet</p>';
            return;
        }

        this.pastUploadsContainer.innerHTML = uploads.map(upload => `
            <div class="upload-item" data-upload-id="${upload.upload_id}">
                <div class="upload-item-info">
                    <div class="upload-item-name">${this.escapeHtml(upload.filename || 'Unknown file')}</div>
                    <div class="upload-item-meta">${this.formatDate(upload.created_at)} ${upload.topic ? `- ${upload.topic}` : ''}</div>
                </div>
                <span class="upload-item-status ${upload.status}">${upload.status}</span>
            </div>
        `).join('');

        // Add click handlers
        this.pastUploadsContainer.querySelectorAll('.upload-item').forEach(item => {
            item.addEventListener('click', () => {
                const uploadId = item.dataset.uploadId;
                this.loadUploadQuestions(uploadId);
            });
        });
    }

    async loadUploadQuestions(uploadId) {
        try {
            this.showStatus('Loading questions...');
            const data = await this.fetchQuestions(uploadId);

            if (data.status === 'completed') {
                this.displayQuestions(data);
            } else if (data.status === 'failed') {
                this.showError(data.error || 'Question generation failed');
            } else {
                this.showStatus('Questions are still being generated...');
            }

        } catch (error) {
            console.error('Error loading questions:', error);
            this.showError(error.message || 'Failed to load questions');
        }
    }

    showStatus(message) {
        document.querySelector('.upload-section-modern').style.display = 'none';
        this.resultsSection.style.display = 'none';
        this.statusSection.style.display = 'block';
        this.statusText.textContent = message;
    }

    showError(message) {
        this.statusSection.style.display = 'none';
        document.querySelector('.upload-section-modern').style.display = 'block';
        alert(message);
    }

    resetToUpload() {
        this.clearSelectedFile();
        this.statusSection.style.display = 'none';
        this.resultsSection.style.display = 'none';
        document.querySelector('.upload-section-modern').style.display = 'block';
        this.currentUploadId = null;
    }

    initTabs() {
        const tabs = document.querySelectorAll('.tab');
        const tabContents = document.querySelectorAll('.tab-content');

        tabs.forEach(tab => {
            tab.addEventListener('click', () => {
                // Remove active class from all tabs and contents
                tabs.forEach(t => t.classList.remove('active'));
                tabContents.forEach(tc => tc.classList.remove('active'));

                // Add active class to clicked tab
                tab.classList.add('active');

                // Show corresponding content
                const tabName = tab.dataset.tab;
                const content = document.getElementById(`${tabName}Tab`);
                if (content) {
                    content.classList.add('active');
                }
            });
        });
    }

    formatDate(isoString) {
        if (!isoString) return '';
        const date = new Date(isoString);
        return date.toLocaleDateString() + ' ' + date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    }

    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
}

// Initialize app when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    window.quizifyApp = new QuizifyApp();
});
