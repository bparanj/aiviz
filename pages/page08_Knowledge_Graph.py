import streamlit as st
import json
from pathlib import Path
import networkx as nx
import matplotlib.pyplot as plt

def validate_knowledge_graph_data(data):
    """Validate the knowledge graph data structure."""
    if not isinstance(data, dict):
        return False, "Data must be a dictionary"
    
    if "nodes" not in data or "links" not in data:
        return False, "Data must contain 'nodes' and 'links' keys"
        
    if not isinstance(data["nodes"], list) or not isinstance(data["links"], list):
        return False, "Both 'nodes' and 'links' must be arrays"
        
    # Check if nodes are empty
    if not data["nodes"]:
        return False, "Graph must contain at least one node"
        
    # Validate nodes
    node_ids = set()
    for node in data["nodes"]:
        if not isinstance(node, dict):
            return False, "Each node must be a dictionary"
            
        if "id" not in node or "label" not in node:
            return False, "Each node must have 'id' and 'label' fields"
            
        node_ids.add(node["id"])
    
    # Validate links
    for link in data["links"]:
        if not isinstance(link, dict):
            return False, "Each link must be a dictionary"
            
        if "source" not in link or "target" not in link:
            return False, "Each link must have 'source' and 'target' fields"
            
        if link["source"] not in node_ids or link["target"] not in node_ids:
            return False, "Link endpoints must reference existing node IDs"
    
    return True, "Valid knowledge graph data"

def load_sample_data():
    """Load sample knowledge graph data."""
    sample_path = Path(__file__).parent.parent / "data" / "knowledge_graph_sample.json"
    with open(sample_path, "r") as f:
        return json.load(f)

def visualize_knowledge_graph(data):
    """Create a network visualization of the knowledge graph."""
    G = nx.Graph()
    
    # Add nodes
    for node in data["nodes"]:
        G.add_node(node["id"], label=node["label"])
    
    # Add edges
    for link in data["links"]:
        G.add_edge(link["source"], link["target"])
    
    # Create the visualization
    fig = plt.figure(figsize=(10, 8))
    pos = nx.spring_layout(G)
    
    # Draw nodes
    nx.draw_networkx_nodes(G, pos, node_color='lightblue', 
                          node_size=500, alpha=0.6)
    
    # Draw edges
    nx.draw_networkx_edges(G, pos)
    
    # Add labels
    labels = nx.get_node_attributes(G, 'label')
    nx.draw_networkx_labels(G, pos, labels)
    
    plt.title("Knowledge Graph Visualization")
    return fig

def main():
    st.title("Knowledge Graph Visualization")
    
    # File upload
    uploaded_file = st.file_uploader("Upload Knowledge Graph JSON", type=["json"])
    
    # Load data
    if uploaded_file is not None:
        try:
            data = json.load(uploaded_file)
        except json.JSONDecodeError:
            st.error("Invalid JSON file")
            return
    else:
        data = load_sample_data()
    
    # Validate data
    is_valid, message = validate_knowledge_graph_data(data)
    if not is_valid:
        st.error(f"Invalid data: {message}")
        return
    
    # Display raw data
    with st.expander("View Raw Data"):
        st.json(data)
    
    # Create visualization
    fig = visualize_knowledge_graph(data)
    st.pyplot(fig)

if __name__ == "__main__":
    main()
