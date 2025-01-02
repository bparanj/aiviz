import streamlit as st
import plotly.graph_objects as go
import json
from pathlib import Path
import pandas as pd

def load_sample_data():
    """Load sample taxonomy data from JSON file."""
    sample_path = Path(__file__).parent.parent / "data" / "domain_taxonomy_sample.json"
    with open(sample_path, 'r') as f:
        return json.load(f)

def validate_node(node):
    """Validate a single node in the taxonomy tree."""
    if not isinstance(node, dict):
        return False, "Node must be a dictionary"
    
    if 'name' not in node or not isinstance(node['name'], str) or not node['name'].strip():
        return False, "Node must have a non-empty name string"
    
    if 'count' not in node or not isinstance(node['count'], (int, float)) or node['count'] < 0:
        return False, "Node must have a non-negative count"
    
    if 'children' not in node or not isinstance(node['children'], list):
        return False, "Node must have a children array"
    
    for child in node['children']:
        is_valid, message = validate_node(child)
        if not is_valid:
            return False, f"Invalid child node: {message}"
    
    return True, "Valid node"

def process_data_for_treemap(node, parent_id="", level=0):
    """Convert hierarchical JSON to flat arrays for Plotly treemap."""
    # Initialize arrays for current node and its descendants
    ids = []
    labels = []
    parents = []
    values = []
    
    # Add current node
    current_id = f"{level}_{node['name']}"
    ids.append(current_id)
    labels.append(node['name'])
    values.append(node['count'])
    parents.append(parent_id)
    
    # Process children
    for child in node['children']:
        # Recursively process child and get its data
        child_ids, child_labels, child_parents, child_values = process_data_for_treemap(
            child, current_id, level + 1
        )
        # Extend current arrays with child data
        ids.extend(child_ids)
        labels.extend(child_labels)
        parents.extend(child_parents)
        values.extend(child_values)
    
    return ids, labels, parents, values

def create_treemap(data):
    """Create a Plotly treemap visualization."""
    ids, labels, parents, values = process_data_for_treemap(data)
    
    fig = go.Figure(go.Treemap(
        ids=ids,
        labels=labels,
        parents=parents,
        values=values,
        textinfo="label+value",
        hovertemplate="""
        Category: %{label}<br>
        Count: %{value}<br>
        Percentage of parent: %{percentParent:.1%}<br>
        <extra></extra>
        """,
        marker=dict(
            colors=[f"hsl({(i*50)%360}, 70%, 50%)" for i in range(len(ids))]
        )
    ))
    
    fig.update_layout(
        title="Domain Taxonomy Visualization",
        width=800,
        height=600,
        margin=dict(t=30, l=10, r=10, b=10)
    )
    
    return fig

def main():
    st.title("Domain Taxonomy Visualization")
    st.write("""
    Visualize hierarchical domain categories and their relative sizes using an interactive treemap.
    Each rectangle's size represents the count or prevalence of items in that category.
    """)
    
    # Input method selection
    input_method = st.radio(
        "Select input method:",
        ["Use Sample Data", "Upload JSON File", "Paste JSON"]
    )
    
    data = None
    
    if input_method == "Use Sample Data":
        data = load_sample_data()
        st.success("Sample data loaded successfully!")
        
    elif input_method == "Upload JSON File":
        uploaded_file = st.file_uploader("Upload JSON file", type=['json'])
        if uploaded_file:
            try:
                data = json.load(uploaded_file)
                st.success("File uploaded successfully!")
            except json.JSONDecodeError:
                st.error("Invalid JSON file. Please check the format.")
                
    else:  # Paste JSON
        json_str = st.text_area("Paste JSON data here")
        if json_str:
            try:
                data = json.loads(json_str)
                st.success("JSON parsed successfully!")
            except json.JSONDecodeError:
                st.error("Invalid JSON format. Please check the input.")
    
    if data:
        # Validate data
        is_valid, message = validate_node(data)
        if not is_valid:
            st.error(f"Invalid data structure: {message}")
            return
        
        # Show raw data in expandable section
        with st.expander("View Raw Data"):
            st.json(data)
        
        # Create and display visualization
        fig = create_treemap(data)
        st.plotly_chart(fig, use_container_width=True)
        
        # Instructions
        st.header("Instructions")
        st.markdown("""
        - Click on a category to zoom in
        - Click in the center to zoom out
        - Hover over sections to see details:
          - Category name
          - Count value
          - Percentage of parent category
        - Double click to reset the view
        """)

if __name__ == "__main__":
    main()
