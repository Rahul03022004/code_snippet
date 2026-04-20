def generate_learning_path(graph, gaps):
    path = []

    for skill in gaps:
        skill = skill.capitalize()
        
        if skill in graph:
            prereqs = list(graph.predecessors(skill))
            path.extend(prereqs)
        
        path.append(skill)

    return list(set(path))