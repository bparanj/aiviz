import streamlit as st
import json
import networkx as nx
import plotly.graph_objects as go
import numpy as np
from pathlib import Path

def load_sample_data():
    sample_path = Path(__file__).parent.parent / "data" / "node_influence_sample.json"
    with open(sample_path, 'r') as f:
        return json.load(f)

def validate_data(data):
    """Validate the input data format and constraints."""
    if not isinstance(data, dict):
        raise ValueError("Data must be a dictionary")
    
    if 'nodes' not in data or 'links' not in data:
        raise ValueError("Data must contain 'nodes' and 'links' arrays")
    
    # Validate nodes
    node_ids = set()
    for node in data['nodes']:
        if 'id' not in node:
            raise ValueError("Each node must have an 'id' field")
        if node['id'] in node_ids:
            raise ValueError(f"Duplicate node ID found: {node['id']}")
        node_ids.add(node['id'])
        
        if 'influence' not in node:
            raise ValueError(f"Node {node['id']} missing required 'influence' field")
        if not isinstance(node['influence'], (int, float)) or node['influence'] < 0:
            raise ValueError(f"Node {node['id']} has invalid influence value. Must be a non-negative number")
    
    # Validate links
    for link in data['links']:
        if 'source' not in link or 'target' not in link:
            raise ValueError("Each link must have 'source' and 'target' fields")
        if link['source'] not in node_ids:
            raise ValueError(f"Link source '{link['source']}' not found in nodes")
        if link['target'] not in node_ids:
            raise ValueError(f"Link target '{link['target']}' not found in nodes")
        if 'weight' in link:
            if not isinstance(link['weight'], (int, float)) or link['weight'] <= 0:
                raise ValueError(f"Link weight must be a positive number")
    
    return True

def create_network_graph(data):
    """Create a NetworkX graph from the input data."""
    G = nx.Graph()
    
    # Add nodes with attributes
    for node in data['nodes']:
        G.add_node(node['id'], 
                  label=node.get('label', node['id']),
                  influence=node['influence'])
    
    # Add edges with weights
    for link in data['links']:
        G.add_edge(link['source'], 
                  link['target'], 
                  weight=link.get('weight', 1.0))
    
    return G

def create_plotly_figure(G, pos=None, selected_node=None):
    """Create a Plotly figure for the network visualization."""
    if pos is None:
        # Use spring layout with weights for better node spacing
        pos = nx.spring_layout(G, k=1.5, iterations=50, weight='weight')
    
    # Extract node positions and attributes
    node_x = []
    node_y = []
    node_text = []
    node_size = []
    node_color = []
    node_symbols = []  # For different node shapes based on selection
    node_ids = []  # Store node IDs for customdata
    node_influences = []  # Store influence values for customdata
    
    # Calculate node degree (number of connections) for additional influence metric
    degrees = dict(G.degree())
    
    for node in G.nodes():
        x, y = pos[node]
        node_x.append(x)
        node_y.append(y)
        
        # Get node attributes
        label = G.nodes[node].get('label', node)
        influence = float(G.nodes[node]['influence'])  # Ensure influence is float
        degree = degrees[node]
        
        # Store node ID and influence for customdata
        node_ids.append(str(node))
        node_influences.append(influence)
        
        # Scale node size based on both influence and degree
        # This creates a more nuanced visualization of node importance
        size = 20 + (influence * 40) + (degree * 5)
        node_size.append(size)
        
        # Use influence for color intensity
        node_color.append(influence)
        
        # Use different symbols for selected vs non-selected nodes
        symbol = 'star' if node == selected_node else 'circle'
        node_symbols.append(symbol)
        
        # Create detailed hover text
        hover_text = [
            f"Node: {label}",
            f"Influence: {influence:.2f}",
            f"Connections: {degree}",
            "Click to highlight connections"
        ]
        node_text.append("<br>".join(hover_text))
    
    # Create edges with improved styling
    edge_x = []
    edge_y = []
    edge_text = []
    edge_width = []
    edge_color = []
    
    for edge in G.edges():
        x0, y0 = pos[edge[0]]
        x1, y1 = pos[edge[1]]
        
        edge_x.extend([x0, x1, None])
        edge_y.extend([y0, y1, None])
        
        weight = G.edges[edge].get('weight', 1.0)
        # Scale edge width based on weight
        scaled_width = 1 + (weight * 2)
        edge_width.extend([scaled_width] * 3)
        
        # Color edges connected to selected node
        if selected_node and (edge[0] == selected_node or edge[1] == selected_node):
            edge_color.extend(['rgba(255,0,0,0.8)'] * 3)  # Red for selected
        else:
            edge_color.extend(['rgba(180,180,180,0.5)'] * 3)  # Light gray for others
            
        # Enhanced edge hover text
        source_label = G.nodes[edge[0]].get('label', edge[0])
        target_label = G.nodes[edge[1]].get('label', edge[1])
        edge_text.extend([
            f"Connection: {source_label} → {target_label}<br>"
            f"Weight: {weight:.1f}"
        ] * 3)
    
    # Create regular edges trace
    regular_edge_x = []
    regular_edge_y = []
    regular_edge_text = []
    
    # Create highlighted edges trace
    highlighted_edge_x = []
    highlighted_edge_y = []
    highlighted_edge_text = []
    
    for i in range(0, len(edge_x), 3):
        if edge_color[i] == 'rgba(255,0,0,0.8)':
            highlighted_edge_x.extend([edge_x[i], edge_x[i+1], None])
            highlighted_edge_y.extend([edge_y[i], edge_y[i+1], None])
            highlighted_edge_text.extend([edge_text[i]] * 3)
        else:
            regular_edge_x.extend([edge_x[i], edge_x[i+1], None])
            regular_edge_y.extend([edge_y[i], edge_y[i+1], None])
            regular_edge_text.extend([edge_text[i]] * 3)
    
    # Create regular edges trace
    edge_trace = go.Scatter(
        x=regular_edge_x, y=regular_edge_y,
        line=dict(color='rgba(180,180,180,0.5)', width=1),
        hoverinfo='text',
        text=regular_edge_text,
        mode='lines',
        showlegend=False
    )
    
    # Create highlighted edges trace if any exist
    if highlighted_edge_x:
        highlighted_edge_trace = go.Scatter(
            x=highlighted_edge_x, y=highlighted_edge_y,
            line=dict(color='rgba(255,0,0,0.8)', width=2),
            hoverinfo='text',
            text=highlighted_edge_text,
            mode='lines',
            showlegend=False
        )
    
    # Create node trace with enhanced styling and hover support
    node_trace = go.Scatter(
        x=node_x, y=node_y,
        mode='markers+text',
        hoverinfo='text',
        text=node_text,
        marker=dict(
            size=node_size,
            color=[float(val) for val in node_color],  # Convert to float for colorscale
            colorscale='Viridis',
            showscale=True,
            colorbar=dict(
                title='Influence Score',
                thickness=15,
                len=0.5,
                tickformat='.2f'
            ),
            symbol=node_symbols,
            line=dict(
                width=2,
                color='rgba(50,50,50,0.8)'  # Single color for node borders
            )
        ),
        hoverlabel=dict(
            bgcolor='rgba(255,255,255,0.8)',
            font=dict(size=12)
        ),
        showlegend=False,
        customdata=[{'id': node_id, 'influence': influence} for node_id, influence in zip(node_ids, node_influences)],
        hovertemplate='Node: %{text}<br>Influence: %{customdata.influence:.3f}<extra></extra>'
    )
    
    # Create the figure with enhanced layout and selection handling
    data = [edge_trace, node_trace]
    if 'highlighted_edge_trace' in locals():
        data.append(highlighted_edge_trace)
    fig = go.Figure(
        data=data,
        layout=go.Layout(
            title=dict(
                text='Node Influence Network',
                x=0.5,
                y=0.95,
                xanchor='center',
                yanchor='top',
                font=dict(size=24)
            ),
            showlegend=False,
            hovermode='closest',
            clickmode='event+select',
            dragmode='select',  # Use select mode for node selection
            margin=dict(b=20, l=5, r=5, t=60),
            xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            plot_bgcolor='white',
            annotations=[
                dict(
                    text="Node Size = Influence + Connections<br>Color Intensity = Influence Score",
                    showarrow=False,
                    xref="paper", yref="paper",
                    x=0.01, y=0.01,
                    align='left',
                    bgcolor='rgba(255,255,255,0.8)',
                    bordercolor='gray',
                    borderwidth=1,
                    font=dict(size=12)
                )
            ]
        )
    )
    
    return fig

def main():
    st.title("11. Node Influence")
    st.write("""
    This visualization shows which nodes in a network are the most influential based on their influence scores.
    The visualization uses multiple visual encodings to represent node importance:
    - **Node Size**: Larger nodes indicate higher influence and more connections
    - **Color Intensity**: Darker colors represent higher influence scores
    - **Edge Thickness**: Thicker lines show stronger connections between nodes
    
    Click on a node to highlight its connections and see its influence in the network.
    """)
    
    # Data source selection
    data_source = st.radio(
        "Select data source:",
        ["Sample Data", "Upload JSON", "Paste JSON"]
    )
    
    try:
        if data_source == "Sample Data":
            data = load_sample_data()
        elif data_source == "Upload JSON":
            uploaded_file = st.file_uploader("Upload a JSON file", type=['json'])
            if uploaded_file is None:
                st.info("Please upload a JSON file")
                return
            data = json.load(uploaded_file)
        else:  # Paste JSON
            json_str = st.text_area(
                "Paste JSON data",
                value=json.dumps(load_sample_data(), indent=2)
            )
            if not json_str:
                st.info("Please paste your JSON data")
                return
            data = json.loads(json_str)
        
        # Validate data
        validate_data(data)
        
        # Add node selection functionality
        selected_node = st.session_state.get('selected_node', None)
        
        # Create and display the network visualization
        G = create_network_graph(data)
        fig = create_plotly_figure(G, selected_node=selected_node)
        
        # Handle node click events
        if 'selected_node' not in st.session_state:
            st.session_state.selected_node = None

        # Display the plot and capture click events
        clicked_point = st.plotly_chart(
            fig,
            use_container_width=True,
            key='network_plot'
        )
        
        # Handle selection through Plotly's built-in selection mode
        if st.session_state.get('selected_node') is not None:
            st.info(f"""
            **Selected Node Details:**
            - Label: {G.nodes[st.session_state.selected_node].get('label', st.session_state.selected_node)}
            - Influence Score: {G.nodes[st.session_state.selected_node]['influence']:.2f}
            - Number of Connections: {len(list(G.neighbors(st.session_state.selected_node)))}
            """)
            
            # Add a button to clear selection
            if st.button('Clear Selection', key='clear_selection'):
                st.session_state.selected_node = None
                st.rerun()
        
        # Display network statistics with enhanced formatting
        col1, col2 = st.columns(2)
        
        with col1:
            st.header("Network Statistics")
            st.write(f"**Number of nodes:** {G.number_of_nodes()}")
            st.write(f"**Number of edges:** {G.number_of_edges()}")
            
            # Calculate and display network density
            density = nx.density(G)
            st.write(f"**Network density:** {density:.2f}")
        
        with col2:
            st.header("Influence Statistics")
            influence_values = [G.nodes[node]['influence'] for node in G.nodes()]
            
            # Create a more detailed influence analysis
            stats = {
                "Average influence": np.mean(influence_values),
                "Maximum influence": max(influence_values),
                "Minimum influence": min(influence_values),
                "Median influence": np.median(influence_values),
                "Std deviation": np.std(influence_values)
            }
            
            for label, value in stats.items():
                st.write(f"**{label}:** {value:.2f}")
            
        # Display selected node information if any
        if selected_node:
            st.header("Selected Node Details")
            node_data = {
                "Label": G.nodes[selected_node].get('label', selected_node),
                "Influence Score": G.nodes[selected_node]['influence'],
                "Number of Connections": len(list(G.neighbors(selected_node))),
                "Connected To": [G.nodes[n].get('label', n) for n in G.neighbors(selected_node)]
            }
            
            for label, value in node_data.items():
                if isinstance(value, list):
                    st.write(f"**{label}:** {', '.join(value)}")
                else:
                    st.write(f"**{label}:** {value}")
        
    except Exception as e:
        st.error(f"Error: {str(e)}")

if __name__ == "__main__":
    main()
