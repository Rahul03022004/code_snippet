def recommend_courses(skills):
    courses = {
        "python": "Python for Everybody - Coursera",
        "machine learning": "Machine Learning by Andrew Ng",
        "deep learning": "Deep Learning Specialization",
        "sql": "SQL for Data Science",
        "data analysis": "Google Data Analytics",
    }

    recommendations = {}

    for skill in skills:
        course = courses.get(skill.lower(), "YouTube / Free resources")
        recommendations[skill] = course

    return recommendations