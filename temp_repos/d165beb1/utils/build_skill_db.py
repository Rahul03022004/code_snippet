import pandas as pd
from models.skill_extractor import extract_skills

def build_skill_database():
    df = pd.read_csv("data/resume_dataset.csv")

    all_skills = set()

    # change column name if needed
    text_column = df.columns[0]

    for text in df[text_column].head(100):  # limit for speed
        try:
            skills = extract_skills(str(text))
            for s in skills:
                all_skills.add(s.lower())
        except:
            continue

    return list(all_skills)


if __name__ == "__main__":
    skills = build_skill_database()

    pd.DataFrame(skills, columns=["skill"]).to_csv(
        "data/skills_from_dataset.csv", index=False
    )

    print("Skill DB created!")