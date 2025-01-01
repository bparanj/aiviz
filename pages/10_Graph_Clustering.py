import streamlit as st
import networkx as nx
import json
import plotly.graph_objects as go
from typing import Dict, List, Optional, Any
import numpy as np
from pathlib import Path

def load_sample_data() -> Dict[str, Any]:
    """Load sample data for graph clustering visualization."""
    sample_path = Path(__file__).parent.parent / "data" / "graph_clustering_sample.json"
    with open(sample_path, 'r') as f:
        return json.load(f)

def validate_data(data: Dict[str, Any]) -> bool:
    """
    Validate the input data structure for graph clustering visualization.
    
    Args:
        data: Dictionary containing nodes and links arrays
    
    Returns:
        bool: True if data is valid, False otherwise
    """
    if not isinstance(data, dict):
        st.error("Input must be a dictionary")
        return False
    
    if "nodes" not in data or "links" not in data:
        st.error("Data must contain 'nodes' and 'links' arrays")
        return False
    
    if not isinstance(data["nodes"], list) or not isinstance(data["links"], list):
        st.error("Both 'nodes' and 'links' must be arrays")
        return False
    
    # Validate minimum number of nodes
    if len(data["nodes"]) < 4:
        st.error("At least 4 nodes are required to demonstrate clustering")
        return False
    
    # Check for unique node IDs
    node_ids = set()
    for node in data["nodes"]:
        if not isinstance(node, dict) or "id" not in node:
            st.error("Each node must have an 'id' field")
            return False
        if node["id"] in node_ids:
            st.error(f"Duplicate node ID found: {node['id']}")
            return False
        node_ids.add(node["id"])
    
    # Validate links
    for link in data["links"]:
        if not isinstance(link, dict):
            st.error("Each link must be a dictionary")
            return False
        if "source" not in link or "target" not in link:
            st.error("Each link must have 'source' and 'target' fields")
            return False
        if link["source"] not in node_ids or link["target"] not in node_ids:
            st.error(f"Invalid link: {link['source']} -> {link['target']}")
            return False
        if "weight" in link and not isinstance(link["weight"], (int, float)):
            st.error("Link weight must be a number")
            return False
    
    return True

def create_network_graph(data: Dict[str, Any]) -> nx.Graph:
    """Create a NetworkX graph from the input data."""
    G = nx.Graph()
    
    # Add nodes with labels
    for node in data["nodes"]:
        G.add_node(node["id"], label=node.get("label", node["id"]))
    
    # Add edges with weights
    for link in data["links"]:
        G.add_edge(link["source"], link["target"], weight=link.get("weight", 1.0))
    
    return G

def detect_communities(G: nx.Graph) -> Dict[str, int]:
    """
    Detect communities in the graph using the Louvain method.
    
    Args:
        G: NetworkX graph
    
    Returns:
        Dict mapping node IDs to community IDs
    """
    try:
        import community
        return community.best_partition(G)
    except ImportError:
        st.warning("Community detection requires the python-louvain package. Using connected components instead.")
        communities = {}
        for i, component in enumerate(nx.connected_components(G)):
            for node in component:
                communities[node] = i
        return communities

def create_plotly_figure(G: nx.Graph, communities: Dict[str, int], weight_threshold: float = 0.0) -> go.Figure:
    """Create a Plotly figure for the clustered graph."""
    # Filter edges based on weight threshold
    G_filtered = G.copy()
    edges_to_remove = [(u, v) for u, v, d in G.edges(data=True) if d.get('weight', 1.0) < weight_threshold]
    G_filtered.remove_edges_from(edges_to_remove)
    
    # Use spring layout for node positioning
    pos = nx.spring_layout(G_filtered, k=1/np.sqrt(len(G_filtered.nodes())), iterations=50)
    
    # Create edge traces
    edge_x = []
    edge_y = []
    edge_text = []
    
    for edge in G_filtered.edges(data=True):
        x0, y0 = pos[edge[0]]
        x1, y1 = pos[edge[1]]
        edge_x.extend([x0, x1, None])
        edge_y.extend([y0, y1, None])
        weight = edge[2].get('weight', 1.0)
        edge_text.extend([f"Weight: {weight:.2f}", f"Weight: {weight:.2f}", None])
    
    edge_trace = go.Scatter(
        x=edge_x, y=edge_y,
        line=dict(width=1, color='#888'),
        hoverinfo='text',
        hovertext=edge_text,
        mode='lines')
    
    # Create node traces for each community
    node_traces = []
    max_community = max(communities.values())
    
    for community_id in range(max_community + 1):
        community_nodes = [node for node in G.nodes() if communities[node] == community_id]
        
        node_x = []
        node_y = []
        node_text = []
        node_size = []
        
        for node in community_nodes:
            x, y = pos[node]
            node_x.append(x)
            node_y.append(y)
            
            # Create hover text
            neighbors = list(G.neighbors(node))
            degree = len(neighbors)
            neighbor_text = "<br>Connected to: " + ", ".join(G.nodes[n]["label"] for n in neighbors[:5])
            if len(neighbors) > 5:
                neighbor_text += f"<br>and {len(neighbors) - 5} more"
            
            node_text.append(f"ID: {node}<br>"
                           f"Label: {G.nodes[node]['label']}<br>"
                           f"Cluster: {community_id + 1}<br>"
                           f"Connections: {degree}"
                           f"{neighbor_text}")
            
            # Size nodes by degree
            node_size.append(10 + degree * 5)
        
        node_trace = go.Scatter(
            x=node_x, y=node_y,
            mode='markers',
            hoverinfo='text',
            text=node_text,
            marker=dict(
                size=node_size,
                color=community_id,
                colorscale='Viridis',
                showscale=False,
                line=dict(width=1, color='#888')
            ),
            name=f'Cluster {community_id + 1}',
            customdata=[community_id] * len(node_x),  # Add community ID as custom data
            selectedpoints=[],  # Enable selection
            selected=dict(
                marker=dict(
                    size=20,
                    color='red',
                    line=dict(width=3, color='darkred')
                )
            ),
            unselected=dict(
                marker=dict(
                    size=15,
                    opacity=0.3
                )
            )
        )
        
        node_traces.append(node_trace)
    
    # Create the figure
    fig = go.Figure(data=[edge_trace, *node_traces],
                   layout=go.Layout(
                       showlegend=True,
                       hovermode='closest',
                       margin=dict(b=20,l=5,r=5,t=40),
                       xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                       yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                       title="Graph Clustering Visualization"
                   ))
    
    return fig

def main():
    st.title("Graph Clustering Visualization")
    st.write("""
    This visualization shows how nodes in a network form tightly knit groups or communities based on their connections.
    Nodes are colored by their detected community, and sized based on their number of connections.
    """)
    
    # Add weight threshold slider in sidebar
    st.sidebar.title("Visualization Controls")
    weight_threshold = st.sidebar.slider(
        "Link Weight Threshold",
        min_value=0.0,
        max_value=5.0,
        value=0.0,
        step=0.1,
        help="Filter links with weight below this threshold"
    )
    
    # Add cluster highlighting controls
    highlight_cluster = st.sidebar.checkbox(
        "Enable Cluster Highlighting",
        value=True,
        help="Click on nodes to highlight their cluster"
    )
    
    # Data input selection
    data_source = st.radio(
        "Select data source:",
        ["Sample Data", "Upload JSON", "Paste JSON"]
    )
    
    # Initialize data
    data = None
    
    if data_source == "Sample Data":
        data = load_sample_data()
    elif data_source == "Upload JSON":
        uploaded_file = st.file_uploader("Upload JSON file", type="json")
        if uploaded_file:
            try:
                data = json.load(uploaded_file)
            except json.JSONDecodeError:
                st.error("Invalid JSON file")
    else:  # Paste JSON
        json_str = st.text_area("Paste JSON data")
        if json_str:
            try:
                data = json.loads(json_str)
            except json.JSONDecodeError:
                st.error("Invalid JSON format")
    
    if data and validate_data(data):
        # Create network graph
        G = create_network_graph(data)
        
        # Detect communities
        communities = detect_communities(G)
        
        
        # Create and display the visualization with weight threshold
        fig = create_plotly_figure(G, communities, weight_threshold)
        
        # Add click event handler for cluster highlighting
        if highlight_cluster:
            fig.update_traces(
                marker=dict(
                    size=15,
                    line=dict(width=2, color='DarkSlateGrey')
                ),
                selector=dict(mode='markers')
            )
        st.plotly_chart(fig, use_container_width=True)
        
        # Display statistics in the sidebar
        st.sidebar.title("Graph Statistics")
        st.sidebar.write(f"Number of nodes: {len(G.nodes())}")
        st.sidebar.write(f"Number of edges: {len(G.edges())}")
        st.sidebar.write(f"Number of communities: {len(set(communities.values()))}")
        
        # Display community information
        st.sidebar.title("Community Information")
        for community_id in sorted(set(communities.values())):
            community_nodes = [node for node in G.nodes() if communities[node] == community_id]
            st.sidebar.write(f"Community {community_id + 1}:")
            st.sidebar.write(f"- Size: {len(community_nodes)}")
            st.sidebar.write(f"- Members: {', '.join(G.nodes[node]['label'] for node in community_nodes[:5])}")
            if len(community_nodes) > 5:
                st.sidebar.write(f"  and {len(community_nodes) - 5} more")
            st.sidebar.write("")

if __name__ == "__main__":
    main()
