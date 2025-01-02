import streamlit as st
import plotly.graph_objects as go
import json
from typing import Dict, List, Union
import os

def validate_node(node: Dict, is_root: bool = False) -> List[str]:
    """Validate a single node in the feature hierarchy."""
    errors = []
    
    # Check required fields
    if not isinstance(node.get('name'), str) or not node['name'].strip():
        errors.append(f"Node must have a non-empty string name")
    
    if not isinstance(node.get('count'), int) or node['count'] < 0:
        errors.append(f"Node '{node.get('name', 'Unknown')}' must have a non-negative integer count")
    
    # Check children if present
    if 'children' in node:
        if not isinstance(node['children'], list):
            errors.append(f"Node '{node['name']}' children must be an array")
        else:
            child_count = 0
            for child in node['children']:
                errors.extend(validate_node(child))
                child_count += child.get('count', 0)
            
            # Optional: Verify count matches children
            if child_count > node['count']:
                errors.append(f"Node '{node['name']}' count ({node['count']}) is less than sum of children ({child_count})")
    
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
