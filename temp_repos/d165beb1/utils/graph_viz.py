from pyvis.network import Network
import tempfile

def visualize_graph(graph, highlight_nodes=None):
    net = Network(height="400px", width="100%", directed=True)

    for node in graph.nodes():
        color = "blue"
        if highlight_nodes and node.lower() in highlight_nodes:
            color = "red"

        net.add_node(node, label=node, color=color)

    for edge in graph.edges():
        net.add_edge(edge[0], edge[1])

    tmp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".html")
    net.save_graph(tmp_file.name)

    return tmp_file.name