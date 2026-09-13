
import os
import uuid
import pymupdf

from flask import Flask, render_template, request
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from werkzeug.utils import secure_filename


# Create Flask application
app = Flask(__name__, static_folder="styles")


# Folder where uploaded resumes will be stored
app.config["UPLOAD_FOLDER"] = "uploads"

os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)


# Load the Sentence Transformer model
model = SentenceTransformer("all-MiniLM-L6-v2")


# Skills that our application can identify
SKILLS = [
    "python",
    "java",
    "c",
    "c++",
    "javascript",
    "html",
    "css",
    "react",
    "angular",
    "node.js",
    "flask",
    "fastapi",
    "sql",
    "mysql",
    "mongodb",
    "machine learning",
    "deep learning",
    "artificial intelligence",
    "tensorflow",
    "pytorch",
    "scikit-learn",
    "pandas",
    "numpy",
    "git",
    "github",
    "docker",
    "aws",
    "azure",
]


# Extract text from PDF
def extract_text_from_pdf(pdf_path):

    text = ""

    with pymupdf.open(pdf_path) as doc:

        for page in doc:
            text = text + page.get_text()

    return text.strip()


# Calculate semantic similarity
def calculate_similarity(resume_text, job_desc):

    embeddings = model.encode([
        resume_text,
        job_desc
    ])

    similarity = cosine_similarity(
        [embeddings[0]],
        [embeddings[1]]
    )

    score = similarity[0][0] * 100

    return round(score, 2)


# Find skills in a piece of text
def find_skills(text):

    text = text.lower()

    found_skills = []

    for skill in SKILLS:

        if skill.lower() in text:
            found_skills.append(skill)

    return found_skills


# Home page
@app.route("/", methods=["GET", "POST"])
def index():

    if request.method == "POST":

        # Check whether resume was uploaded
        if "resume" not in request.files:
            return render_template(
                "index.html",
                error="Please upload a resume."
            )

        file = request.files["resume"]

        # Get job description
        job_desc = request.form.get("job_desc", "").strip()

        # Validate file
        if file.filename == "":
            return render_template(
                "index.html",
                error="Please select a resume PDF."
            )

        # Validate job description
        if job_desc == "":
            return render_template(
                "index.html",
                error="Please enter a job description."
            )

        # Check PDF format
        if not file.filename.lower().endswith(".pdf"):
            return render_template(
                "index.html",
                error="Only PDF files are allowed."
            )

        # Make filename safe
        original_filename = secure_filename(file.filename)

        # Create unique filename
        filename = str(uuid.uuid4()) + "_" + original_filename

        # Create complete file path
        filepath = os.path.join(
            app.config["UPLOAD_FOLDER"],
            filename
        )

        # Save uploaded resume
        file.save(filepath)

        try:

            # Extract resume text
            resume_text = extract_text_from_pdf(filepath)

            if not resume_text:
                return render_template(
                    "index.html",
                    error="Could not extract text from this PDF."
                )

            # Calculate semantic similarity
            score = calculate_similarity(
                resume_text,
                job_desc
            )

            # Find skills
            resume_skills = find_skills(resume_text)
            job_skills = find_skills(job_desc)

            # Skills present in both resume and job description
            matched_skills = [
                skill for skill in job_skills
                if skill in resume_skills
            ]

            # Skills required by job but missing in resume
            missing_skills = [
                skill for skill in job_skills
                if skill not in resume_skills
            ]

            # Decide score message
            if score >= 80:
                message = "Excellent Match"
            elif score >= 60:
                message = "Good Match"
            elif score >= 40:
                message = "Moderate Match"
            else:
                message = "Low Match"

            return render_template(
                "index.html",
                score=score,
                message=message,
                matched_skills=matched_skills,
                missing_skills=missing_skills
            )

        finally:

            # Delete uploaded resume after processing
            if os.path.exists(filepath):
                os.remove(filepath)

    # First time opening the page
    return render_template(
        "index.html",
        score=None
    )


# Start Flask server
if __name__ == "__main__":
    app.run(debug=True)
