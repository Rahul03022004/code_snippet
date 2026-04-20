def find_skill_gap(user_skills, jd_skills):
    user_skills = set([s.lower() for s in user_skills])
    jd_skills = set([s.lower() for s in jd_skills])

    gap = jd_skills - user_skills
    return list(gap)