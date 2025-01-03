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

from utils.data_validation import validate_neural_network_topology

def load_sample_data():
    """Load sample neural network topology data."""
    sample_data_path = Path(project_root) / "data" / "neural_network_topology_sample.json"
    with open(sample_data_path, 'r') as f: 
        return json.load(f)

def build_graph_from_tree(node, graph, parent=None, depth=0):
    """Build a NetworkX graph from a hierarchical tree structure.
    
    Args:
        node (dict): Current node in the tree
        graph (nx.DiGraph): NetworkX graph to build
        parent (str, optional): Parent node name. Defaults to None.
        depth (int): Current depth in the tree for layout purposes
        
    Returns:
        tuple: (x_pos, y_pos) Position hints for layout
    """
    current_name = node["name"]
    node_type = node.get("type", "default")
    
    # Add this node to the graph with its properties
    graph.add_node(current_name, 
                  node_type=node_type,
                  depth=depth)
    
    # If there's a parent, connect them
    if parent:
        graph.add_edge(parent, current_name)
    
    # Process children
    child_count = len(node["children"])
    for i, child in enumerate(node["children"]):
        # Calculate relative position for child
        build_graph_from_tree(child, graph, current_name, depth + 1)
    
    return graph

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
        is_valid, message = validate_neural_network_topology(data)
        if not is_valid:
            st.error(f"Invalid data: {message}")
            return
            
        # Create network visualization
        G = nx.DiGraph()
        
        # Track clicked node for highlighting
        clicked_node = st.session_state.get('clicked_node', None)
        if 'clicked_node' not in st.session_state:
            st.session_state.clicked_node = None
            
        # Build graph from tree structure
        build_graph_from_tree(data, G)
        
        # Create hierarchical layout
        pos = nx.spring_layout(G)
        
        # Adjust positions to create a top-down tree layout
        root = next(n for n in G.nodes() if G.in_degree(n) == 0)
        bfs_edges = list(nx.bfs_edges(G, root))
        bfs_nodes = [root] + [v for _, v in bfs_edges]
        
        # Calculate levels for each node
        levels = {root: 0}
        for u, v in bfs_edges:
            levels[v] = levels[u] + 1
            
        # Calculate x positions based on tree traversal
        x_positions = {}
        current_level = 0
        level_nodes = []
        
        for node in bfs_nodes:
            if levels[node] != current_level:
                # Position nodes in current level
                width = 1.0 / (len(level_nodes) + 1)
                for i, n in enumerate(level_nodes, 1):
                    x_positions[n] = i * width
                # Reset for next level    
                current_level = levels[node]
                level_nodes = []
            level_nodes.append(node)
            
        # Handle last level
        if level_nodes:
            width = 1.0 / (len(level_nodes) + 1)
            for i, n in enumerate(level_nodes, 1):
                x_positions[n] = i * width
                
        # Set final positions combining x and y coordinates
        max_level = max(levels.values())
        pos = {node: [x_positions[node], 1 - levels[node]/(max_level + 1)] 
               for node in G.nodes()}
        
        # Create edges trace
        edge_x = []
        edge_y = []
        
        for edge in G.edges():
            x0, y0 = pos[edge[0]]
            x1, y1 = pos[edge[1]]
            edge_x.extend([x0, x1, None])
            edge_y.extend([y0, y1, None])
        
        # Create edge colors based on highlighting
        edge_colors = []
        edge_widths = []
        
        for edge in G.edges():
            # Highlight edges connected to clicked node
            if clicked_node and (edge[0] == clicked_node or edge[1] == clicked_node):
                edge_colors.append('rgba(255, 165, 0, 0.8)')  # Orange for highlighted edges
                edge_widths.append(edge_width * 2)
            else:
                edge_colors.append('rgba(128, 128, 128, 0.5)')  # Light gray for normal edges
                edge_widths.append(edge_width)
        
        edge_trace = go.Scatter(
            x=edge_x, y=edge_y,
            line=dict(
                width=edge_widths,
                color=edge_colors,
            ),
            hoverinfo='text',
            mode='lines',
            text=[f"Connection: {edge[0]} → {edge[1]}" for edge in G.edges()],
        )
        
        # Create nodes trace
        node_x = []
        node_y = []
        node_text = []
        node_color = []
        
        # Define color mapping for different node types
        type_colors = {
            "Ensemble": "#1f77b4",      # Blue
            "NeuralNetwork": "#2ca02c",  # Green
            "RandomForest": "#ff7f0e",   # Orange
            "ConvolutionalLayer": "#d62728",  # Red
            "DenseLayer": "#9467bd",     # Purple
            "DecisionTree": "#8c564b",   # Brown
            "default": "#7f7f7f"         # Gray
        }
        
        for node in G.nodes():
            x, y = pos[node]
            node_x.append(x)
            node_y.append(y)
            
            # Get node properties
            node_type = G.nodes[node].get('node_type', 'default')
            node_text.append(f"Name: {node}<br>Type: {node_type}")
            
            # Color nodes based on type
            node_color.append(type_colors.get(node_type, type_colors['default']))
        
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
                st.markdown("### Selected Component")
                st.info(f"Name: {st.session_state.clicked_node}")
                
                # Show node details
                node_type = G.nodes[st.session_state.clicked_node]['node_type']
                depth = G.nodes[st.session_state.clicked_node]['depth']
                st.write(f"Type: {node_type}")
                st.write(f"Depth Level: {depth}")
                
                # Show parent/child relationships
                parent = next(iter(G.predecessors(st.session_state.clicked_node)), None)
                children = list(G.successors(st.session_state.clicked_node))
                
                if parent:
                    st.markdown("#### Parent Component")
                    parent_type = G.nodes[parent]['node_type']
                    st.write(f"{parent} ({parent_type})")
                
                if children:
                    st.markdown("#### Child Components")
                    for child in children:
                        child_type = G.nodes[child]['node_type']
                        st.write(f"{child} ({child_type})")
                
                if st.button('Clear Selection'):
                    st.session_state.clicked_node = None
                    st.rerun()
        
        # Display network statistics
        st.subheader("Network Statistics")
        st.write(f"Total components: {len(G.nodes())}")
        st.write(f"Total connections: {len(G.edges())}")
        st.write(f"Tree depth: {max(nx.shortest_path_length(G, root).values())}")
        
        # Component type statistics
        st.subheader("Component Statistics")
        type_counts = {}
        for node in G.nodes():
            node_type = G.nodes[node].get('node_type', 'default')
            type_counts[node_type] = type_counts.get(node_type, 0) + 1
            
        for node_type, count in type_counts.items():
            st.write(f"{node_type}: {count} components")
        
    except Exception as e:
        st.error(f"Error processing data: {str(e)}")

if __name__ == "__main__":
    main()
