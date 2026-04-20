import re
import pandas as pd

# Load dataset skills
try:
    df = pd.read_csv("data/skills_from_dataset.csv")
    KNOWN_SKILLS = set(df["skill"].str.lower())
except:
    KNOWN_SKILLS = set([
        "python", "machine learning", "deep learning",
        "sql", "data analysis", "statistics",
        "communication", "problem solving"
    ])

def extract_skills(text):
    text = text.lower()

    found_skills = []

    for skill in KNOWN_SKILLS:
        # simple keyword match
        if re.search(r"\b" + re.escape(skill) + r"\b", text):
            found_skills.append(skill)

    return list(set(found_skills))
