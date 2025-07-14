import pdfplumber
import re
import hashlib

def hash_text(text):
    return hashlib.md5(text.encode('utf-8')).hexdigest()

def parseResume(filepath):
    with pdfplumber.open(filepath) as pdf:
        text = " ".join([page.extract_text() for page in pdf.pages if page.extract_text()])

    resume_hash = hash_text(text)

    nameMatch = re.search(r'([A-Z][a-z]+\s[A-Z][a-z]+)', text)
    candidateName = nameMatch.group(0) if nameMatch else "Unknown"

    emailMatch = re.search(r'[\w\.-]+@[\w\.-]+', text)
    email = emailMatch.group(0) if emailMatch else "Unknown"

    phoneMatch = re.search(r'(\d{3}[-.\s]??\d{3}[-.\s]??\d{4}|\(\d{3}\)\s*\d{3}[-.\s]??\d{4}|\d{3}[-.\s]??\d{4})', text)
    phone = phoneMatch.group(0) if phoneMatch else "Unknown"

    skills = ["python", "machine", "learning", "data", "scientist", "developer", "tensorflow", "pytorch", "git", "docker", "skills", "nlp"]
    skillsFound = [skill.lower() for skill in skills if skill.lower() in text.lower()]

    experience_keywords = ['years of experience', 'experience in', 'worked with', 'developed', 'expertise in']
    experience_score = 0
    for keyword in experience_keywords:
        if re.search(r'\b' + re.escape(keyword) + r'\b', text, re.IGNORECASE):
            experience_score += 10 

    skill_match_score = len(skillsFound) * 5
    experience_score_normalized = min(experience_score, 30)
    total_score = skill_match_score + experience_score_normalized

    return {
        "name": candidateName,
        "email": email,
        "phone": phone,
        "skills": skillsFound,
        "experience_score": experience_score,
        "total_score": total_score,
        "hash": resume_hash
    }
