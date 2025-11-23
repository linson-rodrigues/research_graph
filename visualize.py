import os
import psycopg2
import networkx as nx
from pyvis.network import Network
from dotenv import load_dotenv

load_dotenv()

def visualize_interactive():
    print("📊 Fetching data for interactive graph...")

    # 1. Fetch Data
    conn = psycopg2.connect(os.getenv("DATABASE_URL"))
    cur = conn.cursor()

    cur.execute("SELECT id, name, type FROM nodes")
    nodes = cur.fetchall()

    cur.execute("SELECT source_id, target_id, type, citation_context FROM edges")
    edges = cur.fetchall()

    conn.close()

    # 2. Build NetworkX Graph
    G = nx.DiGraph()
    id_to_name = {n[0]: n[1] for n in nodes}

    # Color mapping
    COLOR_MAP = {
        "Paper": "#ff9999",     # Red
        "Concept": "#9fffe0",   # Light Green
        "Metric": "#fff79a",    # Yellow
        "Method": "#99c0ff",    # Blue
        "Dataset": "#ffcc99"    # Orange
    }

    for node_id, name, node_type in nodes:
        color = COLOR_MAP.get(node_type, "#a0a0a0")  # default grey
        G.add_node(
            name,
            label=name,
            title=f"{node_type}",
            color=color,
            size=25
        )

    for source_id, target_id, edge_type, context in edges:
        source = id_to_name.get(source_id)
        target = id_to_name.get(target_id)

        if source and target:
            label_text = edge_type
            hover_text = f"{edge_type}<br><br>Context:<br>{context[:200]}..."
            G.add_edge(source, target, title=hover_text, label=label_text)

    # 3. Create PyVis Network
    net = Network(
        height="750px",
        width="100%",
        bgcolor="#1e1e1e",
        font_color="white",
        directed=True
    )

    net.from_nx(G)

    # 4. Improved Physics Settings
    net.set_options("""
        var options = {
          "nodes": {
            "shape": "dot",
            "scaling": {
              "min": 5,
              "max": 30
            },
            "font": {
              "size": 14,
              "face": "arial"
            }
          },
          "edges": {
            "arrows": {
              "to": {"enabled": true, "scaleFactor": 0.5}
            },
            "color": {"inherit": true},
            "smooth": false
          },
          "interaction": {
            "hover": true,
            "multiselect": true,
            "navigationButtons": true
          },
          "physics": {
            "barnesHut": {
              "gravitationalConstant": -20000,
              "centralGravity": 0.25,
              "springLength": 120,
              "springConstant": 0.02,
              "damping": 0.09
            },
            "minVelocity": 0.75
          }
        }
    """)

    # 5. UTF-8 FIX — write HTML manually
    output_file = "knowledge_graph.html"
    html = net.generate_html(notebook=False)

    with open(output_file, "w", encoding="utf-8") as f:
        f.write(html)

    print(f"✅ Graph saved to {output_file}")
    print("🌐 Opening in browser...")

    # Auto-open for Windows
    os.startfile(output_file)

if __name__ == "__main__":
    visualize_interactive()
