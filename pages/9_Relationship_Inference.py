import streamlit as st

st.set_page_config(page_title="Relationship Inference")
import json
import networkx as nx
import plotly.graph_objects as go
from pathlib import Path
import sys
import numpy as np
from streamlit.components.v1 import html

# Add JavaScript for handling click events
def inject_custom_js():
    js_code = """
    <script>
        function handleNodeClick(data) {
            if (data && data.points && data.points.length > 0) {
                const point = data.points[0];
                if (point.customdata) {
                    window.parent.postMessage({
                        type: 'streamlit:setComponentValue',
                        selected_points: [point.customdata]
                    }, '*');
                }
            }
        }
    </script>
    """
    html(js_code, height=0)

# Add the project root to the Python path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

def load_sample_data():
    """Load sample data from JSON file."""
    sample_file = project_root / "data" / "relationship_inference_sample.json"
    with open(sample_file, 'r') as f:
        return json.load(f)

def validate_data(data):
    """Validate the input data structure and relationships.
    
    Returns:
        tuple: (is_valid: bool, message: str) - Validation result and message
    """
    # Check basic structure
    if not isinstance(data, dict):
        return False, "Input must be a JSON object"
    
    # Check required fields
    if 'nodes' not in data or not isinstance(data['nodes'], list):
        return False, "Missing or invalid 'nodes' array"
    if 'links' not in data or not isinstance(data['links'], list):
        return False, "Missing or invalid 'links' array"
    
    # Check minimum nodes requirement (3-4 nodes)
    if len(data['nodes']) < 3:
        return False, "At least 3 nodes are required to demonstrate relationships"
    
    # Validate node structure and uniqueness
    node_ids = set()
    for node in data['nodes']:
        if not isinstance(node, dict):
            return False, "Each node must be an object"
        if 'id' not in node:
            return False, "Each node must have an 'id' field"
        if not isinstance(node['id'], str):
            return False, f"Node ID must be a string: {node['id']}"
        if node['id'] in node_ids:
            return False, f"Duplicate node ID found: {node['id']}"
        node_ids.add(node['id'])
        
        # Optional label validation
        if 'label' in node and not isinstance(node['label'], str):
            return False, f"Node label must be a string: {node['id']}"
    
    # Validate links
    for link in data['links']:
        if not isinstance(link, dict):
            return False, "Each link must be an object"
        
        # Check required link fields
        if 'source' not in link or 'target' not in link:
            return False, "Each link must have 'source' and 'target' fields"
        if not isinstance(link['source'], str) or not isinstance(link['target'], str):
            return False, "Link source and target must be strings"
            
        # Validate source and target references
        if link['source'] not in node_ids:
            return False, f"Link source '{link['source']}' not found in nodes"
        if link['target'] not in node_ids:
            return False, f"Link target '{link['target']}' not found in nodes"
            
        # Optional type validation
        if 'type' in link and not isinstance(link['type'], str):
            return False, f"Link type must be a string: {link['source']} -> {link['target']}"
    
    return True, "Data validation successful"

def main():
    # Initialize session state for selected points
    if 'selected_points' not in st.session_state:
        st.session_state.selected_points = []
    
    # Inject custom JavaScript
    inject_custom_js()
    
    st.title("Relationship Inference Visualization")
    
    # Add data input options in sidebar
    st.sidebar.header("Data Input")
    data_source = st.sidebar.radio(
        "Choose Data Source",
        ["Sample Data", "Upload JSON", "Paste JSON"]
    )
    
    # Load data based on selection
    if data_source == "Sample Data":
        data = load_sample_data()
    elif data_source == "Upload JSON":
        uploaded_file = st.sidebar.file_uploader("Upload JSON file", type=['json'])
        if uploaded_file is not None:
            try:
                data = json.loads(uploaded_file.getvalue().decode())
                if not validate_data(data):
                    st.sidebar.error("Invalid JSON structure. Please check the format.")
                    return
            except json.JSONDecodeError:
                st.sidebar.error("Invalid JSON file. Please check the format.")
                return
        else:
            data = load_sample_data()
    else:  # Paste JSON
        default_json = json.dumps(load_sample_data(), indent=2)
        json_str = st.sidebar.text_area(
            "Paste JSON data",
            value=default_json,
            height=300
        )
        try:
            data = json.loads(json_str)
            if not validate_data(data):
                st.sidebar.error("Invalid JSON structure. Please check the format.")
                return
        except json.JSONDecodeError:
            st.sidebar.error("Invalid JSON format. Please check the syntax.")
            return
            
    # Show data format help
    with st.sidebar.expander("Data Format Help"):
        st.markdown("""
        Expected JSON format:
        ```json
        {
          "nodes": [
            { "id": "NodeA", "label": "Alice" },
            { "id": "NodeB", "label": "Bob" }
          ],
          "links": [
            { "source": "NodeA", "target": "NodeB", "type": "friend" }
          ]
        }
        ```
        - `nodes`: Array of nodes with unique IDs and labels
        - `links`: Array of connections between nodes
        """)
    
    st.markdown("""
    This visualization helps you:
    - Explore direct connections between entities
    - Discover indirect relationships through multi-hop paths
    - Identify potential missing connections
    
    Upload your own data or use the sample data to get started.
    """)
    
    # Data input section
    st.header("Data Input")
    data_source = st.radio(
        "Choose data source",
        ["Use sample data", "Upload JSON file", "Paste JSON data"]
    )
    
    # Initialize data
    data = None
    
    if data_source == "Use sample data":
        data = load_sample_data()
        st.success("Sample data loaded successfully!")
        
    elif data_source == "Upload JSON file":
        uploaded_file = st.file_uploader("Upload JSON file", type=['json'])
        if uploaded_file:
            try:
                data = json.load(uploaded_file)
            except json.JSONDecodeError:
                st.error("Error: Invalid JSON file")
                return
                
    else:  # Paste JSON data
        json_str = st.text_area("Paste JSON data here")
        if json_str:
            try:
                data = json.loads(json_str)
            except json.JSONDecodeError:
                st.error("Error: Invalid JSON format")
                return
    
    if data:
        # Validate data structure
        if not validate_data(data):
            st.error("Error: Invalid data structure. Please check the documentation for the required format.")
            return
            
        # Display data structure
        st.header("Data Preview")
        st.json(data)
        
        # Create NetworkX graph
        G = nx.Graph()
        
        # Add nodes with labels
        for node in data['nodes']:
            G.add_node(node['id'], label=node.get('label', node['id']))
            
        # Add edges with types
        for link in data['links']:
            G.add_edge(link['source'], link['target'], type=link.get('type', 'unknown'))
        
        # Calculate layout using force-directed algorithm
        pos = nx.spring_layout(G, k=1/np.sqrt(len(G.nodes())), iterations=50)
        
        # Create edges trace
        edge_x = []
        edge_y = []
        edge_text = []
        
        for edge in G.edges(data=True):
            x0, y0 = pos[edge[0]]
            x1, y1 = pos[edge[1]]
            edge_x.extend([x0, x1, None])
            edge_y.extend([y0, y1, None])
            edge_text.append(f"Type: {edge[2].get('type', 'unknown')}")
        
        edges_trace = go.Scatter(
            x=edge_x, y=edge_y,
            line=dict(width=1, color='#888'),
            hoverinfo='text',
            text=edge_text,
            mode='lines')
        
        # Create nodes trace with color based on connectivity
        node_x = []
        node_y = []
        node_text = []
        node_colors = []
        node_sizes = []
        
        # Calculate node degrees for coloring
        degrees = {node: len(list(G.neighbors(node))) for node in G.nodes()}
        max_degree = max(degrees.values()) if degrees else 1
        
        # Add missing link suggestions
        st.sidebar.header("Missing Link Analysis")
        isolated_nodes = [node for node, degree in degrees.items() if degree == 0]
        low_connectivity_nodes = [node for node, degree in degrees.items() if 0 < degree <= max_degree/3]
        
        if isolated_nodes:
            st.sidebar.warning("Isolated Nodes (No Connections):")
            for node in isolated_nodes:
                st.sidebar.write(f"- {G.nodes[node]['label']}")
                
        if low_connectivity_nodes:
            st.sidebar.info("Low Connectivity Nodes:")
            for node in low_connectivity_nodes:
                st.sidebar.write(f"- {G.nodes[node]['label']}")
                # Suggest potential connections
                potential_connections = []
                for other_node in G.nodes():
                    if other_node != node and other_node not in G.neighbors(node):
                        potential_connections.append(G.nodes[other_node]['label'])
                if potential_connections:
                    st.sidebar.write(f"  Potential connections: {', '.join(potential_connections[:3])}")
        
        for node in G.nodes(data=True):
            x, y = pos[node[0]]
            node_x.append(x)
            node_y.append(y)
            
            # Calculate node degree and normalize for color
            degree = degrees[node[0]]
            color_val = degree / max_degree if max_degree > 0 else 0
            node_colors.append(color_val)
            
            # Adjust size based on connectivity
            base_size = 20
            size_factor = 5
            node_sizes.append(base_size + (degree * size_factor))
            
            # Enhanced tooltip with connectivity info
            connections = [G.nodes[n]['label'] for n in G.neighbors(node[0])]
            connection_text = "<br>Connected to: " + ", ".join(connections) if connections else "<br>No connections"
            degree_text = f"<br>Connections: {degree}"
            isolation_text = "<br>Status: Isolated" if degree == 0 else "<br>Status: Low Connectivity" if degree <= max_degree/3 else ""
            node_text.append(f"ID: {node[0]}<br>Label: {node[1]['label']}{connection_text}{degree_text}{isolation_text}")
        
        nodes_trace = go.Scatter(
            x=node_x, y=node_y,
            mode='markers+text',
            hoverinfo='text',
            text=[G.nodes[node]['label'] for node in G.nodes()],
            hovertext=node_text,
            textposition="top center",
            marker=dict(
                showscale=True,
                colorscale='YlOrRd',
                color=node_colors,
                size=node_sizes,
                colorbar=dict(
                    title='Connectivity',
                    thickness=15,
                    xanchor='left',
                    titleside='right'
                ),
                line_width=2))
        
        # Create the figure
        fig = go.Figure(data=[edges_trace, nodes_trace],
                       layout=go.Layout(
                           title='Network Graph',
                           showlegend=False,
                           hovermode='closest',
                           margin=dict(b=20,l=5,r=5,t=40),
                           xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                           yaxis=dict(showgrid=False, zeroline=False, showticklabels=False))
                       )
        
        # Display the graph
        st.plotly_chart(fig, use_container_width=True)

        # Add node selection for path analysis
        st.header("Path Analysis")
        col1, col2 = st.columns(2)
        
        # Source node selection
        with col1:
            source_node = st.selectbox(
                "Select Source Node",
                options=[node for node in G.nodes()],
                format_func=lambda x: G.nodes[x]['label']
            )
        
        # Target node selection
        with col2:
            target_node = st.selectbox(
                "Select Target Node",
                options=[node for node in G.nodes() if node != source_node],
                format_func=lambda x: G.nodes[x]['label']
            )
        
        if st.button("Find Paths"):
            st.subheader(f"Paths from {G.nodes[source_node]['label']} to {G.nodes[target_node]['label']}")
            
            try:
                # Find all paths between selected nodes
                paths = list(nx.all_simple_paths(G, source_node, target_node))
                
                if paths:
                    # Create a new figure for highlighted paths
                    path_fig = go.Figure()
                    
                    # Add all edges with reduced opacity
                    edge_x, edge_y = [], []
                    edge_colors = []
                    for edge in G.edges():
                        x0, y0 = pos[edge[0]]
                        x1, y1 = pos[edge[1]]
                        edge_x.extend([x0, x1, None])
                        edge_y.extend([y0, y1, None])
                        # Check if edge is in any path
                        is_path_edge = any(
                            edge[0] in path and edge[1] in path and 
                            abs(path.index(edge[0]) - path.index(edge[1])) == 1
                            for path in paths
                        )
                        edge_colors.extend([1.0 if is_path_edge else 0.1] * 3)
                    
                    # Add edges trace
                    path_fig.add_trace(go.Scatter(
                        x=edge_x, y=edge_y,
                        line=dict(color='rgba(50,50,50,1)', width=2),
                        hoverinfo='none',
                        mode='lines',
                        line_color=edge_colors,
                        showlegend=False
                    ))
                    
                    
                    # Add nodes with highlighted path nodes
                    path_nodes = set()
                    for path in paths:
                        path_nodes.update(path)
                    
                    node_x = []
                    node_y = []
                    node_colors = []
                    node_text = []
                    
                    for node in G.nodes():
                        x, y = pos[node]
                        node_x.append(x)
                        node_y.append(y)
                        in_path = node in path_nodes
                        node_colors.append(1.0 if in_path else 0.3)
                        node_text.append(G.nodes[node]['label'])
                    
                    path_fig.add_trace(go.Scatter(
                        x=node_x, y=node_y,
                        mode='markers+text',
                        hoverinfo='text',
                        text=node_text,
                        textposition="top center",
                        marker=dict(
                            size=20,
                            color=node_colors,
                            colorscale='YlOrRd',
                            line_width=2
                        )
                    ))
                    
                    # Update layout
                    path_fig.update_layout(
                        showlegend=False,
                        hovermode='closest',
                        margin=dict(b=20,l=5,r=5,t=40)
                    )
                    
                    # Display the highlighted path graph
                    st.plotly_chart(path_fig, use_container_width=True)
                    
                    # Display path information
                    for i, path in enumerate(paths, 1):
                        path_labels = [G.nodes[n]['label'] for n in path]
                        st.write(f"Path {i}: {' → '.join(path_labels)}")
                else:
                    st.info(f"No paths found between {G.nodes[source_node]['label']} and {G.nodes[target_node]['label']}")
            except nx.NetworkXNoPath:
                st.warning(f"No path exists between {G.nodes[source_node]['label']} and {G.nodes[target_node]['label']}")
        
        # Handle node selection for path highlighting
        selected_points = st.session_state.get('selected_points', [])
        if selected_points:
            node_id = selected_points[0]
            st.subheader(f"Paths from {G.nodes[node_id]['label']}")
            
            # Find and display all paths from selected node
            all_paths = []
            for target in G.nodes():
                if target != node_id:
                    try:
                        paths = list(nx.all_simple_paths(G, node_id, target))
                        all_paths.extend(paths)
                    except nx.NetworkXNoPath:
                        continue
            
            if all_paths:
                for i, path in enumerate(all_paths, 1):
                    path_labels = [G.nodes[n]['label'] for n in path]
                    st.write(f"Path {i}: {' → '.join(path_labels)}")
            else:
                st.info(f"No paths found from {G.nodes[node_id]['label']} to other nodes.")
        
        # Display path analysis between two selected nodes
        st.header("Path Analysis")
        
        # Select nodes for path analysis
        col1, col2 = st.columns(2)
        with col1:
            source_node = st.selectbox("Select source node", options=list(G.nodes()), key="source")
        with col2:
            target_node = st.selectbox("Select target node", options=list(G.nodes()), key="target")
        
        if source_node and target_node:
            try:
                # Find all simple paths between selected nodes
                paths = list(nx.all_simple_paths(G, source_node, target_node))
                
                if paths:
                    st.success(f"Found {len(paths)} path(s) between {source_node} and {target_node}")
                    for i, path in enumerate(paths, 1):
                        path_str = " → ".join([G.nodes[node]['label'] for node in path])
                        st.write(f"Path {i}: {path_str}")
                else:
                    st.warning(f"No path found between {source_node} and {target_node}")
            except nx.NetworkXNoPath:
                st.warning(f"No path exists between {source_node} and {target_node}")

if __name__ == "__main__":
    main()
