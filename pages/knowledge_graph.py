import streamlit as st
import networkx as nx
import plotly.graph_objects as go
import json
from pathlib import Path
import pandas as pd

def load_sample_data():
    sample_path = Path(__file__).parent.parent / "data" / "knowledge_graph_sample.json"
    with open(sample_path, 'r') as f:
        return json.load(f)

def validate_knowledge_graph_data(data):
    """Validate the knowledge graph data format and constraints."""
    if not isinstance(data, dict):
        return False, "Data must be a dictionary"
    
    if "nodes" not in data or "links" not in data:
        return False, "Data must contain 'nodes' and 'links' keys"
    
    # Validate nodes
    node_ids = set()
    for node in data["nodes"]:
        if "id" not in node:
            return False, "Each node must have an 'id'"
        if node["id"] in node_ids:
            return False, "Node IDs must be unique"
        node_ids.add(node["id"])
    
    # Validate links
    for link in data["links"]:
        if "source" not in link or "target" not in link:
            return False, "Each link must have 'source' and 'target'"
        if link["source"] not in node_ids:
            return False, f"Link source '{link['source']}' not found in nodes"
        if link["target"] not in node_ids:
            return False, f"Link target '{link['target']}' not found in nodes"
    
    if len(data["nodes"]) < 2:
        return False, "At least 2 nodes are required"
    
    return True, "Valid data"

def create_network_graph(data):
    """Create a NetworkX graph from the data."""
    G = nx.Graph()
    
    # Add nodes with labels
    for node in data["nodes"]:
        G.add_node(node["id"], label=node.get("label", node["id"]))
    
    # Add edges with types
    for link in data["links"]:
        G.add_edge(link["source"], link["target"], type=link.get("type", ""))
    
    return G

def create_plotly_figure(G):
    """Create an interactive Plotly figure from the NetworkX graph."""
    # Use force-directed layout
    pos = nx.spring_layout(G)
    
    # Create edge trace
    edge_x = []
    edge_y = []
    edge_text = []
    
    for edge in G.edges(data=True):
        x0, y0 = pos[edge[0]]
        x1, y1 = pos[edge[1]]
        edge_x.extend([x0, x1, None])
        edge_y.extend([y0, y1, None])
        edge_text.append(edge[2].get('type', ''))
    
    edge_trace = go.Scatter(
        x=edge_x, y=edge_y,
        line=dict(width=0.5, color='#888'),
        hoverinfo='text',
        text=edge_text,
        mode='lines')
    
    # Create node trace
    node_x = []
    node_y = []
    node_text = []
    
    for node in G.nodes():
        x, y = pos[node]
        node_x.append(x)
        node_y.append(y)
        node_text.append(G.nodes[node].get('label', node))
    
    node_trace = go.Scatter(
        x=node_x, y=node_y,
        mode='markers+text',
        hoverinfo='text',
        text=node_text,
        textposition="top center",
        marker=dict(
            showscale=False,
            size=20,
            line_width=2))
    
    # Create figure
    fig = go.Figure(data=[edge_trace, node_trace],
                   layout=go.Layout(
                       showlegend=False,
                       hovermode='closest',
                       margin=dict(b=0, l=0, r=0, t=0),
                       xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                       yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                       dragmode='pan',  # Enable pan/drag mode
                       clickmode='event+select'  # Enable click events
                   ))
    
    # Make the plot more interactive
    fig.update_layout(
        hoverlabel=dict(
            bgcolor="white",
            font_size=12,
            font_family="Arial"
        ),
        # Enable zoom
        modebar=dict(
            add=['zoom', 'pan', 'select', 'lasso2d', 'resetScale2d']
        )
    )
    
    return fig

def main():
    st.title("Knowledge Graph Visualization")
    
    st.markdown("""
    This visualization shows relationships between entities in a knowledge graph using a force-directed layout.
    Nodes represent entities (e.g., people, places, organizations) and edges represent relationships between them.
    
    The graph supports:
    - Interactive drag and zoom
    - Hover tooltips showing node labels and relationship types
    - Pan and zoom controls
    - Custom data input through JSON
    """)
    
    # Data input selection
    data_source = st.radio(
        "Select data source",
        ["Sample Data", "Custom Input"]
    )
    
    if data_source == "Sample Data":
        data = load_sample_data()
        
        # Display sample data structure
        with st.expander("View Sample Data Structure"):
            st.code(json.dumps(data, indent=2), language='json')
    else:
        json_input = st.text_area(
            "Enter your JSON data (must contain 'nodes' and 'links' arrays)",
            height=200,
            help="Press Ctrl+Enter to apply changes"
        )
        
        if json_input:
            try:
                data = json.loads(json_input)
            except json.JSONDecodeError:
                st.error("Invalid JSON format. Please check your input.")
                return
        else:
            data = load_sample_data()
    
    # Validate data
    is_valid, message = validate_knowledge_graph_data(data)
    if not is_valid:
        st.error(f"Invalid data: {message}")
        return
    
    # Create and display the graph
    G = create_network_graph(data)
    fig = create_plotly_figure(G)
    
    # Display statistics
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Number of Nodes", len(G.nodes()))
    with col2:
        st.metric("Number of Edges", len(G.edges()))
    with col3:
        n_nodes = len(G.nodes())
        n_edges = len(G.edges())
        avg_degree = (2 * n_edges) / n_nodes if n_nodes > 0 else 0
        st.metric("Average Degree", round(avg_degree, 2))
    
    # Display the graph with increased height
    st.plotly_chart(fig, use_container_width=True, height=800)
    
    # Add instructions for interaction
    st.markdown("""
    ### Interaction Instructions
    - **Pan**: Click and drag on the background
    - **Zoom**: Use mouse wheel or pinch gesture
    - **Select**: Click on nodes to highlight them
    - **View Details**: Hover over nodes and edges to see details
    - **Reset**: Use the reset button in the modebar to restore the original view
    """)

if __name__ == "__main__":
    main()
