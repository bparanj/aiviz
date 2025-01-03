import streamlit as st
import plotly.graph_objects as go
import json
from typing import Dict, List, Union
import os

def validate_node(node: Dict, is_root: bool = False) -> List[str]:
    """Validate a single node in the feature hierarchy.
    
    Args:
        node: Dictionary containing node data with name, count, and optional children
        is_root: Boolean indicating if this is the root node
        
    Returns:
        List of validation error messages
    """
    errors = []
    
    # Basic node structure validation
    if not isinstance(node, dict):
        return ["Node must be a dictionary"]
    
    # Name validation
    node_name = node.get('name', '')
    if 'name' not in node or not isinstance(node_name, str) or (isinstance(node_name, str) and not node_name.strip()):
        errors.append("Node must have a non-empty string name")
    
    # Get node name for error messages
    display_name = node_name if isinstance(node_name, str) and node_name.strip() else "Unknown"
    
    # Count validation
    count_error = "must have a non-negative integer count"
    if 'count' not in node:
        errors.append(count_error)
        node['count'] = 0  # Set default count to prevent further errors
    else:
        try:
            count = int(node['count'])
            if count < 0:
                errors.append(count_error)
            node['count'] = count  # Convert to int if it was a string number
        except (ValueError, TypeError):
            errors.append(count_error)
            node['count'] = 0  # Set default count to prevent further errors
    
    # Children validation
    child_count = 0
    if 'children' in node:
        if not isinstance(node['children'], list):
            errors.append(f"Node '{display_name}' children must be an array")
        else:
            for child in node['children']:
                errors.extend(validate_node(child))
                try:
                    child_count += int(child.get('count', 0))
                except (ValueError, TypeError):
                    pass  # Error will be caught in child validation
            
            # Hierarchy consistency validation
            try:
                node_count = int(node.get('count', 0))
                if child_count > node_count:
                    errors.append(
                        f"Node '{display_name}' count ({node_count}) is less than sum of children ({child_count})"
                    )
            except (ValueError, TypeError):
                pass  # Error already caught above in count validation
    
    # Root node specific validation
    if is_root:
        if not isinstance(node_name, str) or not node_name.strip():
            errors.append("Node must have a non-empty string name")
        if not isinstance(node.get('children'), list):
            errors.append("Root node must have a children array")
        elif not node.get('children', []):
            errors.append("Root node must have at least one child")
    
    return errors

def process_data_for_sunburst(node: Dict, parent: str = "") -> tuple:
    """Convert hierarchical data to format suitable for Plotly sunburst."""
    names = []
    parents = []
    values = []
    ids = []
    
    # Add current node
    names.append(node['name'])
    parents.append(parent)
    values.append(node['count'])
    ids.append(f"{parent}/{node['name']}" if parent else node['name'])
    
    # Process children
    if 'children' in node:
        for child in node['children']:
            child_names, child_parents, child_values, child_ids = process_data_for_sunburst(
                child, node['name']
            )
            names.extend(child_names)
            parents.extend(child_parents)
            values.extend(child_values)
            ids.extend(child_ids)
    
    return names, parents, values, ids

def create_sunburst_chart(data: Dict) -> go.Figure:
    """Create a Plotly sunburst chart from hierarchical data."""
    names, parents, values, ids = process_data_for_sunburst(data)
    
    fig = go.Figure(go.Sunburst(
        ids=ids,
        labels=names,
        parents=parents,
        values=values,
        branchvalues="total",
        hovertemplate="<b>%{label}</b><br>" +
                      "Features: %{value}<br>" +
                      "Parent: %{parent}<br>" +
                      "<extra></extra>",
        # Color coding for different levels
        marker=dict(
            colors=values,
            colorscale='Viridis',
            showscale=True,
            colorbar=dict(
                title="Feature Count"
            )
        )
    ))
    
    fig.update_layout(
        title={
            'text': "Feature Categories Distribution",
            'y': 0.95,
            'x': 0.5,
            'xanchor': 'center',
            'yanchor': 'top'
        },
        width=800,
        height=800,
        # Enable zooming and panning
        dragmode='pan',
        # Add buttons for zoom control
        updatemenus=[dict(
            type="buttons",
            showactive=False,
            buttons=[
                dict(
                    label="Reset View",
                    method="relayout",
                    args=[{"xaxis.range": None, "yaxis.range": None}]
                )
            ],
            pad={"r": 10, "t": 10},
            x=0.1,
            y=1.1
        )]
    )
    
    return fig

def load_sample_data() -> Dict:
    """Load sample data from JSON file."""
    sample_path = os.path.join(
        os.path.dirname(os.path.dirname(__file__)),
        "data",
        "nested_feature_categories_sample.json"
    )
    with open(sample_path, 'r') as f:
        return json.load(f)

def main():
    st.title("Nested Feature Categories")
    st.write("""
    Visualize how features are organized into categories and subcategories, showing the distribution
    of features across different levels of the hierarchy. The size and color of each segment represent
    the number of features in that category.
    
    - **Hover** over segments to see details
    - **Click** on a segment to zoom into that category
    - **Double-click** to zoom out
    - Use the **Reset View** button to return to the initial view
    """)
    
    # Data input method selection
    data_input = st.radio(
        "Select input method:",
        ["Sample Data", "Upload JSON", "Paste JSON"],
        key="data_input"
    )
    
    data = None
    if data_input == "Sample Data":
        data = load_sample_data()
        st.success("Loaded sample feature categories data")
    
    elif data_input == "Upload JSON":
        uploaded_file = st.file_uploader("Upload JSON file", type=['json'])
        if uploaded_file:
            try:
                data = json.load(uploaded_file)
            except json.JSONDecodeError:
                st.error("Invalid JSON file. Please check the format.")
    
    else:  # Paste JSON
        json_str = st.text_area(
            "Paste JSON data",
            height=300,
            help="Paste your feature categories data in JSON format"
        )
        if json_str:
            try:
                data = json.loads(json_str)
            except json.JSONDecodeError:
                st.error("Invalid JSON format. Please check the syntax.")
    
    if data:
        # Validate data
        errors = validate_node(data, is_root=True)
        if errors:
            st.error("Data validation failed:")
            for error in errors:
                st.write(f"- {error}")
            
            with st.expander("Show Expected Data Format"):
                st.code(json.dumps({
                    "name": "Category Name",
                    "count": 42,
                    "children": [
                        {
                            "name": "Subcategory",
                            "count": 20,
                            "children": []
                        }
                    ]
                }, indent=2), language="json")
                
                st.write("""
                **Requirements:**
                - Each node must have a `name` (string) and `count` (non-negative integer)
                - `children` is optional but must be an array if present
                - Child feature counts cannot exceed parent count
                """)
        else:
            # Create and display visualization
            fig = create_sunburst_chart(data)
            st.plotly_chart(fig, use_container_width=True)
            
            # Show statistics
            total_features = data['count']
            st.write(f"**Total Features:** {total_features}")
            
            # Show raw data in expandable section
            with st.expander("View Raw Data"):
                st.json(data)

if __name__ == "__main__":
    main()
