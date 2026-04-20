def estimate_learning_time(path):
    # Hours per skill (you can expand)
    skill_time = {
        "python": 10,
        "machine learning": 20,
        "deep learning": 25,
        "sql": 8,
        "data analysis": 12,
        "communication": 5
    }

    total_time = 0
    breakdown = {}

    for skill in path:
        t = skill_time.get(skill.lower(), 8)
        breakdown[skill] = t
        total_time += t

    return total_time, breakdown