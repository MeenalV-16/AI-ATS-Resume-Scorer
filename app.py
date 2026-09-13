# import os
#  #to open the pdf file
# import pymupdf#to load pdf
# from flask import Flask, render_template, request
# from sentence_transformers import SentenceTransformer
# from werkzeug.utils import secure_filename   #to give the uploaded file to backend, use this package
# #cosine similarity import
# from sklearn.metrics.pairwise import cosine_similarity

# #to initiate this app in flask
# app = Flask(__name__, static_folder="styles")

# #to store the uploaded resume file
# app.config['Upload Folder'] = 'uploads'
# os.makedirs(app.config['Upload Folder'], exist_ok=True)

# #load the model
# model = SentenceTransformer('all-MiniLM-L6-v2')

# #to extract the text in the uploaded resume
# def extract_text_from_pdf(pdf_path):
#     text = ""
#     with pymupdf.open(pdf_path) as doc:
#         for page in doc:
#             text = text + page.get_text()
#     return text.strip()

# #cosine similarity used to compare job description and resume keywords
# #job description got from frontend
# def cosines_similarity(resume_text, job_desc):
#     #convert text to embeddings to calc cosine similarity
#     embeddings = model.encode([resume_text, job_desc])
#     similarity = cosine_similarity([embeddings[0]],[embeddings[1]])
#     return round(similarity[0][0]*100,2)

# @app.route('/', methods=['GET','POST'])  #connect this with the submit button in html

# def index():
#     if request.method=='POST':
#         if "resume" not in request.files:
#             return "No file uploaded",400
#         file = request.files['resume']
#         job_desc = request.form['job_desc']

#         if file.filename == '' or job_desc=='':
#             return "Invalid input", 400
#         filename = secure_filename(file.filename)
#         filepath = os.path.join(app.config['Upload Folder'], filename)
#         file.save(filepath)

#         resume_text = extract_text_from_pdf(filepath)
#         score = cosines_similarity(resume_text=resume_text, job_desc=job_desc)

#         #to run the html template too along with app.py flask application
#         return render_template('index.html',score=score)
#     return render_template('index.html',score=None)
# if __name__ == "__main__":
#     app.run(debug=True)


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