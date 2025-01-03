import streamlit as st
import plotly.graph_objects as go
import json
from typing import Dict, List, Optional, Union
import os

def validate_node(node: Dict, is_root: bool = False) -> List[str]:
    """Validate a single node in the decision tree."""
    errors = []
    
    # Check required string fields
    for field in ['name', 'condition']:
        if field not in node:
            errors.append(f"Missing required field '{field}'")
        elif not isinstance(node[field], str):
            errors.append(f"Field '{field}' must be a string")
        elif not node[field].strip():
            errors.append(f"Field '{field}' cannot be empty")
    
    # Check samples field
    if 'samples' not in node:
        errors.append("Missing required field 'samples'")
    elif not isinstance(node['samples'], (int, float)):
        errors.append("Field 'samples' must be a number")
    elif node['samples'] < 0:
        errors.append("Field 'samples' must be non-negative")
    
    # Check children field if present
    if 'children' in node:
        if not isinstance(node['children'], list):
            errors.append("Field 'children' must be an array")
        else:
            for i, child in enumerate(node['children']):
                if not isinstance(child, dict):
                    errors.append(f"Child {i} must be an object")
                else:
                    child_errors = validate_node(child)
                    errors.extend([f"In child {i}: {err}" for err in child_errors])
    
    return errors

def validate_tree_data(data: Dict) -> List[str]:
    """Validate the entire decision tree data structure."""
    if not isinstance(data, dict):
        return ["Input must be a JSON object"]
    
    # Validate root node
    errors = validate_node(data, is_root=True)
    
    return errors

def load_sample_data() -> Dict:
    """Load sample decision tree data."""
    sample_data = {
        "name": "Root",
        "condition": "Age < 30",
        "samples": 100,
        "children": [
            {
                "name": "Left Subtree",
                "condition": "Income >= 50k",
                "samples": 60,
                "children": [
                    {
                        "name": "Leaf: Approved",
                        "condition": "Output = Approved",
                        "samples": 40
                    },
                    {
                        "name": "Leaf: Denied",
                        "condition": "Output = Denied",
                        "samples": 20
                    }
                ]
            },
            {
                "name": "Right Subtree",
                "condition": "Income < 50k",
                "samples": 40,
                "children": [
                    {
                        "name": "Leaf: Denied",
                        "condition": "Output = Denied",
                        "samples": 40
                    }
                ]
            }
        ]
    }
    return sample_data

def process_node(node: Dict, x: float = 0, y: float = 0, level: int = 0, 
                parent_x: Optional[float] = None, parent_y: Optional[float] = None,
                node_id: str = "0") -> tuple[List[float], List[float], List[str], List[str], List[str], List[str], List[float], List[float]]:
    """Process each node and its children to create visualization data.
    
    Args:
        node: Dictionary containing node data (name, condition, samples, children)
        x: X-coordinate for this node
        y: Y-coordinate for this node
        level: Current tree level (0 = root)
        parent_x: Parent node's X-coordinate
        parent_y: Parent node's Y-coordinate
        node_id: Unique identifier for this node
        
    Returns:
        Tuple containing:
        - x_coords: List of X coordinates for all nodes
        - y_coords: List of Y coordinates for all nodes
        - node_info: List of node information strings
        - node_ids: List of node identifiers
        - parent_ids: List of parent node identifiers
        - colors: List of node colors
        - edge_x: List of X coordinates for edges
        - edge_y: List of Y coordinates for edges
    """
    x_coords = [x]
    y_coords = [y]
    node_info = [f"{node['name']}<br>{node['condition']}<br>Samples: {node['samples']}"]
    node_ids = [node_id]
    parent_ids = [parent_id for parent_id in ["/".join(node_id.split("/")[:-1])] if parent_id]
    colors = ["#2ecc71" if "Approved" in node['name'] 
             else "#e74c3c" if "Denied" in node['name'] 
             else "#3498db"]
    
    # Add edge from parent if not root
    edge_x = []
    edge_y = []
    if parent_x is not None and parent_y is not None:
        edge_x.extend([parent_x, x, None])
        edge_y.extend([parent_y, y, None])
        
    if "children" in node and node["children"]:
        num_children = len(node["children"])
        child_width = 2.0 / (2 ** level)
        for i, child in enumerate(node["children"]):
            child_x = x - child_width/2 + (i+0.5) * child_width/num_children
            child_y = y - 1
            child_id = f"{node_id}/{i}"
            child_coords = process_node(
                child, child_x, child_y, level + 1, x, y, child_id
            )
            x_coords.extend(child_coords[0])
            y_coords.extend(child_coords[1])
            node_info.extend(child_coords[2])
            node_ids.extend(child_coords[3])
            parent_ids.extend(child_coords[4])
            colors.extend(child_coords[5])
            edge_x.extend(child_coords[6])
            edge_y.extend(child_coords[7])
            
    return x_coords, y_coords, node_info, node_ids, parent_ids, colors, edge_x, edge_y

def create_tree_visualization(data: Dict) -> go.Figure:
    """Create a hierarchical tree visualization using Plotly."""

    # Process the tree data
    x_coords, y_coords, node_info, node_ids, parent_ids, colors, edge_x, edge_y = process_node(data)  # type: ignore
    
    # Create the tree visualization
    fig = go.Figure()
    
    # Add edges (lines connecting nodes)
    fig.add_trace(go.Scatter(
        x=edge_x,
        y=edge_y,
        mode='lines',
        line=dict(color='#888', width=1),
        hoverinfo='none',
        showlegend=False,
        customdata=[{"type": "edge"}] * len(edge_x)
    ))
    
    # Add nodes
    hover_template = (
        "<b>%{customdata.name}</b><br>" +
        "Condition: %{customdata.condition}<br>" +
        "Samples: %{customdata.samples}<br>" +
        "<extra></extra>"
    )
    
    node_customdata = [
        {
            "type": "node",
            "id": node_id,
            "parent": parent_id,
            "name": info.split("<br>")[0],
            "condition": info.split("<br>")[1],
            "samples": info.split("<br>")[2].split(": ")[1]
        }
        for node_id, parent_id, info in zip(node_ids, parent_ids, node_info)
    ]
    
    fig.add_trace(go.Scatter(
        x=x_coords,
        y=y_coords,
        mode='markers+text',
        marker=dict(
            size=30,
            color=colors,
            line=dict(color='white', width=2)
        ),
        text=[info.split('<br>')[0] for info in node_info],
        textposition="bottom center",
        hovertemplate=hover_template,
        customdata=node_customdata,
        showlegend=False
    ))
    
    # Update layout
    fig.update_layout(
        title="Decision Tree Breakdown",
        showlegend=False,
        hovermode='closest',
        margin=dict(t=50, l=25, r=25, b=25),
        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        plot_bgcolor='white',
        width=1000,
        height=800,
        # Add click event handler for path highlighting
        clickmode='event+select'
    )
    
    # Add buttons for expand/collapse functionality
    fig.update_layout(
        updatemenus=[
            dict(
                type="buttons",
                showactive=False,
                buttons=[
                    dict(
                        label="Expand All",
                        method="relayout",
                        args=[{"yaxis.range": [min(y_coords)-1, max(y_coords)+1]}]
                    ),
                    dict(
                        label="Collapse All",
                        method="relayout",
                        args=[{"yaxis.range": [0, 1]}]  # Show only root level
                    )
                ],
                x=0.05,
                y=1,
                xanchor="left",
                yanchor="top"
            )
        ]
    )
    
    # Add JavaScript for path highlighting
    fig.update_layout(
        newshape=dict(line_color='#2ecc71'),
        annotations=[
            dict(
                x=0.5,
                y=-0.1,
                xref="paper",
                yref="paper",
                text="Click on a node to highlight its path to root",
                showarrow=False
            )
        ]
    )

    # Add JavaScript callback for path highlighting
    fig.add_trace(go.Scatter(
        x=[],
        y=[],
        mode='lines',
        line=dict(color='#2ecc71', width=3),
        hoverinfo='none',
        showlegend=False,
        visible=False,
        name='highlighted_path'
    ))

    # Add click handler
    fig.update_layout(
        clickmode='event',
        updatemenus=[
            dict(
                type="buttons",
                showactive=False,
                buttons=[
                    dict(
                        label="Expand All",
                        method="relayout",
                        args=[{"yaxis.range": [min(y_coords)-1, max(y_coords)+1]}]
                    ),
                    dict(
                        label="Collapse All",
                        method="relayout",
                        args=[{"yaxis.range": [0, 1]}]  # Show only root level
                    ),
                    dict(
                        label="Clear Highlight",
                        method="update",
                        args=[{"visible": [True, True, False]}, {}]
                    )
                ],
                x=0.05,
                y=1,
                xanchor="left",
                yanchor="top"
            )
        ]
    )

    # Add JavaScript event handlers
    fig.update_layout(
        {
            'clickmode': 'event',
            'hovermode': 'closest'
        }
    )

    # Add custom JavaScript for path highlighting
    st.markdown("""
        <script>
            const graphDiv = document.querySelector('.js-plotly-plot');
            if (graphDiv) {
                graphDiv.on('plotly_click', function(data) {
                    const pt = data.points[0];
                    if (pt.customdata && pt.customdata.type === 'node') {
                        const nodeId = pt.customdata.id;
                        const allNodes = [];
                        let currentNode = nodeId;
                        
                        // Build path to root
                        while (currentNode) {
                            allNodes.push(currentNode);
                            currentNode = currentNode.split('/').slice(0, -1).join('/');
                        }
                        
                        // Update highlighted path
                        const highlightedPath = {
                            x: [],
                            y: []
                        };
                        
                        allNodes.forEach(nodeId => {
                            const nodeIndex = data.points[0].data.customdata
                                .findIndex(node => node.id === nodeId);
                            if (nodeIndex !== -1) {
                                highlightedPath.x.push(data.points[0].data.x[nodeIndex]);
                                highlightedPath.y.push(data.points[0].data.y[nodeIndex]);
                            }
                        });
                        
                        Plotly.update(graphDiv, {
                            'x': [null, null, highlightedPath.x],
                            'y': [null, null, highlightedPath.y],
                            'visible': [true, true, true]
                        }, {}, [0, 1, 2]);
                    }
                });
            }
        </script>
    """, unsafe_allow_html=True)
    
    return fig

def main():
    st.title("Decision Tree Breakdown")
    st.write("""
    Visualize the structure and decision paths of a decision tree model. The visualization shows:
    - Hierarchical structure from root to leaf nodes
    - Decision conditions at each node
    - Sample distribution across different paths
    """)
    
    # Data input options
    data_option = st.radio(
        "Choose data input method:",
        ["Use sample data", "Upload JSON file", "Paste JSON data"]
    )
    
    tree_data = None
    
    if data_option == "Use sample data":
        tree_data = load_sample_data()
        st.write("Using sample decision tree data")
        
    elif data_option == "Upload JSON file":
        uploaded_file = st.file_uploader("Upload JSON file", type=["json"])
        if uploaded_file:
            try:
                tree_data = json.load(uploaded_file)
            except json.JSONDecodeError as e:
                st.error(f"Error: Invalid JSON file - {str(e)}")
                return
                
    else:  # Paste JSON data
        json_str = st.text_area("Paste JSON data here")
        if json_str:
            try:
                tree_data = json.loads(json_str)
            except json.JSONDecodeError as e:
                st.error(f"Error: Invalid JSON data - {str(e)}")
                return
    
    if not tree_data:
        st.error("No data provided. Please upload a file or paste JSON data.")
        return

    try:
        # Validate the tree data
        validation_errors = validate_tree_data(tree_data)
        if validation_errors:
            st.error("Invalid decision tree data:")
            for error in validation_errors:
                st.error(f"- {error}")
            return
        
        # Create and display the visualization
        fig = create_tree_visualization(tree_data)
        st.plotly_chart(fig, use_container_width=True)
        
        # Display raw data in expandable section
        with st.expander("View raw data"):
            st.json(tree_data)
    except Exception as e:
        st.error(f"Error processing tree data: {str(e)}")
        return

if __name__ == "__main__":
    main()
