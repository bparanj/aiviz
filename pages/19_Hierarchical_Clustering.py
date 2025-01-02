import streamlit as st
import json
import plotly.graph_objects as go
from typing import Dict, List, Optional
import random

def validate_node(node: Dict) -> List[str]:
    """Validate a single node in the hierarchical clustering tree."""
    errors = []
    
    # Check name field
    if 'name' not in node:
        errors.append("Missing required field 'name'")
    elif not isinstance(node['name'], str):
        errors.append("Field 'name' must be a string")
    elif not node['name'].strip():
        errors.append("Field 'name' cannot be empty")
    
    # Check children field if present
    if 'children' in node:
        if not isinstance(node['children'], list):
            errors.append("Field 'children' must be an array")
        else:
            for child in node['children']:
                errors.extend(validate_node(child))
    
    return errors

def process_node(node: Dict, parent: Optional[str] = "", level: int = 0) -> tuple[List[Dict], List[Dict]]:
    """Process a node and its children to create Plotly visualization data."""
    nodes = []
    edges = []
    node_id = f"{parent}_{node['name']}" if parent else node['name']
    
    # Add current node
    nodes.append({
        'id': node_id,
        'label': node['name'],
        'level': level,
        'parent': parent
    })
    
    # Add edge from parent if not root
    if parent:
        edges.append({
            'from': parent,
            'to': node_id
        })
    
    # Process children if any
    if 'children' in node:
        for child in node['children']:
            child_nodes, child_edges = process_node(child, node_id, level + 1)
            nodes.extend(child_nodes)
            edges.extend(child_edges)
    
    return nodes, edges

def create_cluster_visualization(data: Dict) -> go.Figure:
    """Create a hierarchical clustering visualization using Plotly."""
    nodes, edges = process_node(data)
    
    # Generate colors for different branches
    unique_levels = len(set(node['level'] for node in nodes))
    colors = [f'hsl({h},70%,50%)' for h in range(0, 360, 360 // unique_levels)]
    
    # Create figure
    fig = go.Figure()
    
    # Add nodes
    node_positions = {}
    for node in nodes:
        # Calculate y position based on level and siblings
        siblings = [n for n in nodes if n['level'] == node['level']]
        y_pos = siblings.index(node) / (len(siblings) + 1)
        node_positions[node['id']] = (node['level'], y_pos)
        
        fig.add_trace(go.Scatter(
            x=[node['level']],
            y=[y_pos],
            mode='markers+text',
            name=node['label'],
            text=[node['label']],
            textposition='middle right',
            hoverinfo='text',
            hovertext=f"Cluster: {node['label']}",
            marker=dict(
                size=20,
                color=colors[node['level']],
                line=dict(width=2)
            ),
            showlegend=False
        ))
    
    # Add edges
    for edge in edges:
        start_pos = node_positions[edge['from']]
        end_pos = node_positions[edge['to']]
        
        fig.add_trace(go.Scatter(
            x=[start_pos[0], end_pos[0]],
            y=[start_pos[1], end_pos[1]],
            mode='lines',
            line=dict(color='gray', width=1),
            hoverinfo='none',
            showlegend=False
        ))
    
    # Update layout
    fig.update_layout(
        title='Hierarchical Clustering Visualization',
        showlegend=False,
        hovermode='closest',
        xaxis=dict(
            title='Cluster Level',
            showgrid=False,
            zeroline=False
        ),
        yaxis=dict(
            showgrid=False,
            zeroline=False,
            showticklabels=False
        ),
        plot_bgcolor='white',
        updatemenus=[
            dict(
                type="buttons",
                showactive=False,
                buttons=[
                    dict(
                        label="Reset View",
                        method="relayout",
                        args=[{"xaxis.range": None, "yaxis.range": None}]
                    )
                ]
            )
        ]
    )
    
    return fig

def load_sample_data() -> Dict:
    """Load sample hierarchical clustering data."""
    with open('data/hierarchical_clustering_sample.json', 'r') as f:
        return json.load(f)

def main():
    st.title("Hierarchical Clustering Visualization")
    st.write("""
    Visualize how data points group into clusters at various levels (depths) using a hierarchical tree structure.
    This visualization helps identify natural groupings and relationships between data points.
    """)
    
    # Data input method selection
    data_input = st.radio(
        "Choose data input method:",
        ["Use sample data", "Upload JSON file", "Paste JSON data"]
    )
    
    data = None
    try:
        if data_input == "Use sample data":
            data = load_sample_data()
        elif data_input == "Upload JSON file":
            uploaded_file = st.file_uploader("Upload JSON file", type=['json'])
            if uploaded_file:
                data = json.load(uploaded_file)
        else:  # Paste JSON data
            json_str = st.text_area("Paste JSON data here")
            if json_str:
                data = json.loads(json_str)
        
        if data:
            # Validate data
            errors = validate_node(data)
            if errors:
                st.error("Invalid data structure:")
                for error in errors:
                    st.error(f"- {error}")
            else:
                # Create visualization
                fig = create_cluster_visualization(data)
                st.plotly_chart(fig, use_container_width=True)
                
                # Show raw data in expandable section
                with st.expander("View Raw Data"):
                    st.json(data)
    
    except json.JSONDecodeError:
        st.error("Invalid JSON format. Please check your input.")
    except Exception as e:
        st.error(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    main()
