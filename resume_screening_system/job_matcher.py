jobDescription = "Looking machine learning Python NLP Data Scientist developer skills TensorFlow PyTorch Git Docker"

def getJobScore(parsed_resume):
    jobSkills = set(jobDescription.lower().split())    
    resumeSkills = set(parsed_resume['skills'])    
    jobMatchScore = (len(resumeSkills.intersection(jobSkills)) / len(jobSkills)) * 100
    return round(jobMatchScore, 2)
