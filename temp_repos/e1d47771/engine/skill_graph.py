import networkx as nx

def build_skill_graph():
    G = nx.DiGraph()

    # Example relationships (you can expand later)
    G.add_edge("Python", "Machine Learning")
    G.add_edge("Machine Learning", "Deep Learning")
    G.add_edge("Statistics", "Machine Learning")
    G.add_edge("SQL", "Data Analysis")

    return G