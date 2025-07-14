from flask import Flask, request, render_template
from resume_parser import parseResume
from job_matcher import getJobScore
from pymongo import MongoClient
from drive_uploader import upload_to_drive
import os

app = Flask(__name__)

UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

client = MongoClient('mongodb://localhost:27017/')
db = client['ResumeDB']
collection = db['Resumes']

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_resume():
    if 'file' not in request.files:
        return "No file uploaded!"
    file = request.files['file']
    if file.filename == '':
        return "No selected file!"

    filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
    file.save(filepath)

    parsedData = parseResume(filepath)
    jobScore = getJobScore(parsedData)
    parsedData['score'] = float(jobScore)

    if collection.find_one({'hash': parsedData['hash']}):
        return "This resume has already been uploaded."

    drive_link = upload_to_drive(filepath, file.filename)
    parsedData['drive_url'] = drive_link

    collection.insert_one(parsedData)

    return render_template(
        'result.html',
        name=parsedData['name'],
        email=parsedData['email'],
        phone=parsedData['phone'],
        score=jobScore,
        drive_url=drive_link
    )

@app.route('/resumes')
def list_resumes():
    query = {}
    name = request.args.get('name')
    email = request.args.get('email')
    min_score = request.args.get('min_score', type=float)
    max_score = request.args.get('max_score', type=float)
    skill = request.args.get('skill')

    if name:
        query['name'] = {'$regex': name, '$options': 'i'}
    if email:
        query['email'] = {'$regex': email, '$options': 'i'}
    if min_score is not None or max_score is not None:
        score_filter = {}
        if min_score is not None:
            score_filter['$gte'] = min_score
        if max_score is not None:
            score_filter['$lte'] = max_score
        query['score'] = score_filter
    if skill:
        skill_list = [s.strip().lower() for s in skill.split(',')]
        query['skills'] = {'$all': skill_list}

    resumes = list(collection.find(query))
    return render_template('resumes.html', resumes=resumes)

if __name__ == '__main__':
    app.run(debug=True)
