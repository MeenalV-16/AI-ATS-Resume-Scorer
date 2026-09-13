# AI-ATS Resume Scorer

An AI-powered resume screening application that analyzes how well a resume matches a given job description.

The application extracts text from a PDF resume, compares it with the job description using Natural Language Processing (NLP), calculates a semantic similarity score, and identifies matched and missing skills.

## Features

- Upload resume in PDF format
- Extract resume text automatically
- Compare resume with a job description
- Calculate resume-job semantic similarity score
- Identify matched skills
- Identify missing skills
- Display an overall match level
- Simple and responsive web interface
- Automatically removes uploaded resumes after processing

## Technologies Used

### Backend
- Python
- Flask
- PyMuPDF

### Machine Learning / NLP
- Sentence Transformers
- Scikit-learn
- Cosine Similarity

### Frontend
- HTML
- CSS
- Jinja2

### Tools
- Poetry
- Git
- GitHub
- VS Code

## How It Works

The application follows these steps:

1. The user uploads a resume in PDF format.
2. The application extracts the text from the resume using PyMuPDF.
3. The user provides a job description.
4. Sentence Transformers converts the resume and job description into numerical embeddings.
5. Cosine similarity is used to measure how semantically similar they are.
6. The application calculates a percentage score.
7. The system checks for skills present in both the resume and job description.
8. Matched and missing skills are displayed to the user.

## Project Structure

```text
AI-ATS-Resume-Scorer/
│
├── app.py
├── pyproject.toml
├── poetry.lock
├── .gitignore
│
├── templates/
│   └── index.html
│
├── styles/
│   └── style.css
│
└── uploads/
