def generate_reasoning(gaps):
    reasoning_list = []

    for skill in gaps:
        reasoning_list.append(
            f"{skill} is required in the Job Description but missing in your resume."
        )

    return reasoning_list