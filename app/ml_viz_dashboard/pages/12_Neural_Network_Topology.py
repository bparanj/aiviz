import streamlit as st
import json
import plotly.graph_objects as go
import networkx as nx
from pathlib import Path
import sys

# Add the project root to the Python path
project_root = str(Path(__file__).parent.parent)
if project_root not in sys.path:
    sys.path.append(project_root)

from utils.data_validation import validate_json_structure

def load_sample_data():
    """Load sample neural network topology data."""
    sample_data_path = Path(project_root) / "data" / "neural_network_topology_sample.json"
    with open(sample_data_path, 'r') as f:
        return json.load(f)

def validate_neural_network_data(data):
    """Validate the neural network topology data structure.
    
    Checks:
    1. Basic structure (layers and connections arrays)
    2. Layer indices (0 to N, sequential)
    3. Node IDs (unique across all layers)
    4. Connection references (valid source/target nodes)
    5. Layer types and minimum requirements
    6. Connection weights (numeric values)
    """
    required_fields = {
        "layers": list,
        "connections": list
    }
    
    if not validate_json_structure(data, required_fields):
        return False, "Data must contain 'layers' and 'connections' arrays"
    
    # Check minimum layers requirement
    if len(data["layers"]) < 2:
        return False, "Network must have at least 2 layers (input and output)"
    
    # Validate layers and collect node information
    layer_indices = set()
    node_ids = set()
    node_layers = {}  # Maps node ID to layer index
    
    for layer in data["layers"]:
        # Check layer index
        if not isinstance(layer.get("layerIndex"), (int, float)):
            return False, "Each layer must have a numeric layerIndex"
        
        layer_idx = layer["layerIndex"]
        if layer_idx in layer_indices:
            return False, f"Duplicate layer index found: {layer_idx}"
        layer_indices.add(layer_idx)
        
        # Check layer type
        layer_type = layer.get("layerType", "hidden")
        if layer_type not in ["input", "hidden", "output"]:
            return False, f"Invalid layer type: {layer_type}"
        
        # Validate nodes array
        if not isinstance(layer.get("nodes"), list):
            return False, "Each layer must have a nodes array"
        if not layer["nodes"]:
            return False, f"Layer {layer_idx} has no nodes"
            
        # Check node IDs
        for node in layer["nodes"]:
            if "id" not in node:
                return False, "Each node must have an id"
            if node["id"] in node_ids:
                return False, f"Duplicate node id found: {node['id']}"
            node_ids.add(node["id"])
            node_layers[node["id"]] = layer_idx
    
    # Verify layer indices are sequential from 0
    expected_indices = set(range(len(layer_indices)))
    if layer_indices != expected_indices:
        return False, "Layer indices must be sequential starting from 0"
    
    # Verify input and output layers
    input_layer = next((l for l in data["layers"] if l.get("layerType") == "input"), None)
    output_layer = next((l for l in data["layers"] if l.get("layerType") == "output"), None)
    
    if not input_layer:
        return False, "Network must have an input layer"
    if not output_layer:
        return False, "Network must have an output layer"
    if input_layer["layerIndex"] != 0:
        return False, "Input layer must have index 0"
    if output_layer["layerIndex"] != len(layer_indices) - 1:
        return False, "Output layer must be the last layer"
    
    # Validate connections
    for conn in data["connections"]:
        # Check required fields
        if "source" not in conn or "target" not in conn:
            return False, "Each connection must have source and target"
            
        # Verify node references
        if conn["source"] not in node_ids:
            return False, f"Invalid source node id: {conn['source']}"
        if conn["target"] not in node_ids:
            return False, f"Invalid target node id: {conn['target']}"
            
        # Check layer ordering
        source_layer = node_layers[conn["source"]]
        target_layer = node_layers[conn["target"]]
        if source_layer >= target_layer:
            return False, f"Invalid connection: source layer ({source_layer}) must be before target layer ({target_layer})"
            
        # Validate weight if present
        if "weight" in conn and not isinstance(conn["weight"], (int, float)):
            return False, "Connection weight must be numeric"
    
    return True, "Data validation successful"

def main():
    st.title("12. Neural Network Topology")
    
    st.markdown("""
    This visualization shows the structure of a neural network, including its layers and connections.
    The visualization uses multiple visual encodings to represent the network structure:
    - Nodes arranged in layers from input to output
    - Connections between nodes showing the flow of data
    - Line thickness/color representing connection weights
    
    Interactive Features:
    - Hover over nodes to see layer information
    - Hover over connections to see weights
    - Use the controls below to customize the visualization
    - Click nodes to highlight their connections
    """)
    
    # Visualization controls in sidebar
    st.sidebar.subheader("Visualization Controls")
    show_weights = st.sidebar.checkbox("Show connection weights", value=True)
    edge_width = st.sidebar.slider("Connection line width", 1, 10, 2)
    node_size = st.sidebar.slider("Node size", 10, 50, 20)
    
    # Data source selection
    data_source = st.radio(
        "Select data source:",
        ["Sample Data", "Upload JSON", "Paste JSON"]
    )
    
    try:
        if data_source == "Sample Data":
            data = load_sample_data()
        elif data_source == "Upload JSON":
            uploaded_file = st.file_uploader("Upload a JSON file", type="json")
            if uploaded_file:
                data = json.load(uploaded_file)
            else:
                st.info("Please upload a JSON file")
                return
        else:  # Paste JSON
            json_str = st.text_area("Paste your JSON data here")
            if json_str:
                data = json.loads(json_str)
            else:
                st.info("Please paste your JSON data")
                return
        
        # Validate data
        is_valid, message = validate_neural_network_data(data)
        if not is_valid:
            st.error(f"Invalid data: {message}")
            return
            
        # Create network visualization
        G = nx.DiGraph()
        
        # Track clicked node for highlighting
        clicked_node = st.session_state.get('clicked_node', None)
        if 'clicked_node' not in st.session_state:
            st.session_state.clicked_node = None
            
        # Add nodes with layer information
        for layer in data["layers"]:
            layer_idx = layer["layerIndex"]
            layer_type = layer.get("layerType", "hidden")
            for node in layer["nodes"]:
                G.add_node(node["id"], 
                          layer=layer_idx,
                          layer_type=layer_type)
        
        # Add edges with weights
        for conn in data["connections"]:
            weight = conn.get("weight", 1.0)
            G.add_edge(conn["source"], 
                      conn["target"], 
                      weight=weight)
        
        # Create layered layout
        layers = {}
        for node, attrs in G.nodes(data=True):
            layer = attrs["layer"]
            if layer not in layers:
                layers[layer] = []
            layers[layer].append(node)
        
        # Calculate node positions
        pos = {}
        sorted_layers = sorted(layers.items())
        layer_count = len(sorted_layers)
        
        for layer_idx, (_, nodes) in enumerate(sorted_layers):
            node_count = len(nodes)
            for node_idx, node in enumerate(nodes):
                # X coordinate based on layer
                x = layer_idx / max(1, layer_count - 1)
                # Y coordinate distributed evenly within layer
                y = node_idx / max(1, node_count - 1)
                if node_count == 1:
                    y = 0.5  # Center single nodes
                pos[node] = [x, y]
        
        # Create edges trace
        edge_x = []
        edge_y = []
        edge_weights = []
        
        for edge in G.edges(data=True):
            x0, y0 = pos[edge[0]]
            x1, y1 = pos[edge[1]]
            edge_x.extend([x0, x1, None])
            edge_y.extend([y0, y1, None])
            edge_weights.append(edge[2].get("weight", 1.0))
        
        # Create edge trace with weight-based coloring
        # Create edge colors based on weights and highlighting
        edge_colors = []
        edge_widths = []
        
        for i, edge in enumerate(G.edges()):
            weight = edge_weights[i]
            # Highlight edges connected to clicked node
            if clicked_node and (edge[0] == clicked_node or edge[1] == clicked_node):
                edge_colors.append('rgba(255, 165, 0, 0.8)')  # Orange for highlighted edges
                edge_widths.append(edge_width * 2)
            else:
                if show_weights:
                    # Color based on weight
                    intensity = min(abs(weight)/2, 1)
                    edge_colors.append(f'rgba(255, 0, 0, {intensity})')
                else:
                    edge_colors.append('#888')
                edge_widths.append(edge_width)
        
        edge_trace = go.Scatter(
            x=edge_x, y=edge_y,
            line=dict(
                width=edge_widths,
                color=edge_colors,
            ),
            hoverinfo='text',
            mode='lines',
            text=[f"Weight: {w:.2f}" for w in edge_weights],
        )
        
        # Create nodes trace
        node_x = []
        node_y = []
        node_text = []
        node_color = []
        
        for node in G.nodes():
            x, y = pos[node]
            node_x.append(x)
            node_y.append(y)
            layer_type = G.nodes[node]["layer_type"]
            node_text.append(f"Node: {node}<br>Layer: {layer_type}")
            
            # Color nodes based on layer type
            if layer_type == "input":
                node_color.append("#1f77b4")  # Blue
            elif layer_type == "output":
                node_color.append("#2ca02c")  # Green
            else:
                node_color.append("#ff7f0e")  # Orange
        
        node_trace = go.Scatter(
            x=node_x, y=node_y,
            mode='markers+text',
            hoverinfo='text',
            text=node_text,
            marker=dict(
                color=node_color,
                size=20,
                line=dict(width=2)
            )
        )
        
        # Create figure
        fig = go.Figure(
            data=[edge_trace, node_trace],
            layout=go.Layout(
                title="Neural Network Topology",
                showlegend=False,
                hovermode='closest',
                margin=dict(b=20, l=5, r=5, t=40),
                xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                plot_bgcolor='white'
            )
        )
        
        # Add click events to the figure
        fig.update_layout(
            clickmode='event',
            hovermode='closest'
        )
        
        # Create a container for the visualization and controls
        col1, col2 = st.columns([3, 1])
        
        with col1:
            # Display the visualization with click event handling
            selected_point = st.plotly_chart(
                fig,
                use_container_width=True,
                custom_events=['plotly_click']
            )
            
            # Handle click events
            if selected_point:
                click_data = selected_point.get('plotly_click', {})
                if click_data and click_data.get('points'):
                    point = click_data['points'][0]
                    if point.get('curveNumber') == 1:  # Node trace
                        node_idx = point.get('pointIndex')
                        if node_idx is not None:
                            clicked_node = list(G.nodes())[node_idx]
                            st.session_state.clicked_node = clicked_node
        
        with col2:
            # Add controls for selected node
            if st.session_state.get('clicked_node'):
                st.markdown("### Selected Node")
                st.info(f"Node ID: {st.session_state.clicked_node}")
                
                # Show node details
                node_type = G.nodes[st.session_state.clicked_node]['layer_type']
                layer_idx = G.nodes[st.session_state.clicked_node]['layer']
                st.write(f"Type: {node_type}")
                st.write(f"Layer: {layer_idx}")
                
                # Show connected nodes
                in_edges = list(G.in_edges(st.session_state.clicked_node))
                out_edges = list(G.out_edges(st.session_state.clicked_node))
                
                if in_edges:
                    st.markdown("#### Input Connections")
                    for source, _ in in_edges:
                        weight = G.edges[source, st.session_state.clicked_node]['weight']
                        st.write(f"From {source} (weight: {weight:.2f})")
                
                if out_edges:
                    st.markdown("#### Output Connections")
                    for _, target in out_edges:
                        weight = G.edges[st.session_state.clicked_node, target]['weight']
                        st.write(f"To {target} (weight: {weight:.2f})")
                
                if st.button('Clear Selection'):
                    st.session_state.clicked_node = None
                    st.rerun()
        
        # Display network statistics
        st.subheader("Network Statistics")
        st.write(f"Number of layers: {len(data['layers'])}")
        st.write(f"Total nodes: {len(G.nodes())}")
        st.write(f"Total connections: {len(G.edges())}")
        
        # Layer-wise statistics
        st.subheader("Layer-wise Statistics")
        for layer in sorted(data["layers"], key=lambda x: x["layerIndex"]):
            layer_type = layer.get("layerType", "hidden")
            num_nodes = len(layer["nodes"])
            st.write(f"Layer {layer['layerIndex']} ({layer_type}): {num_nodes} nodes")
        
    except Exception as e:
        st.error(f"Error processing data: {str(e)}")

if __name__ == "__main__":
    main()
