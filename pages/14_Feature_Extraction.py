import streamlit as st
import json
import plotly.graph_objects as go
from pathlib import Path
import pandas as pd

def load_sample_data():
    """Load sample data for the feature extraction visualization."""
    sample_data_path = Path(__file__).parent.parent / "data" / "feature_extraction_sample.json"
    with open(sample_data_path, "r") as f:
        return json.load(f)

def validate_feature_extraction_data(data):
    """Validate the feature extraction data format."""
    try:
        if not isinstance(data, dict):
            return False, "Data must be a dictionary"
        
        if "nodes" not in data or "links" not in data:
            return False, "Data must contain 'nodes' and 'links' keys"
        
        # Validate nodes
        node_ids = set()
        for node in data["nodes"]:
            if "id" not in node or "name" not in node:
                return False, "Each node must have 'id' and 'name' fields"
            if node["id"] in node_ids:
                return False, "Node IDs must be unique"
            node_ids.add(node["id"])
        
        # Validate links
        for link in data["links"]:
            if "source" not in link or "target" not in link or "value" not in link:
                return False, "Each link must have 'source', 'target', and 'value' fields"
            if link["source"] not in node_ids or link["target"] not in node_ids:
                return False, "Link source and target must reference valid node IDs"
            if not isinstance(link["value"], (int, float)) or link["value"] < 0:
                return False, "Link value must be a non-negative number"
        
        # Ensure at least one feature node besides raw data
        if len(node_ids) < 2:
            return False, "Data must contain at least two nodes (raw data and one feature)"
        
        return True, ""
    except Exception as e:
        return False, str(e)

def create_sankey_diagram(data, highlight_node=None):
    """Create a Sankey diagram for feature extraction visualization."""
    # Prepare node colors based on type and highlighting
    node_colors = []
    for node in data["nodes"]:
        if highlight_node is not None and node["id"] == highlight_node:
            color = "#FFD700"  # Highlighted node in gold
        elif "Raw Data" in node["name"]:
            color = "#2E86C1"  # Blue for raw data
        elif "Cleaned" in node["name"]:
            color = "#27AE60"  # Green for cleaned data
        elif "Feature" in node["name"] or any(keyword in node["name"] for keyword in ["Embeddings", "Encodings", "Phrases"]):
            color = "#E67E22"  # Orange for features
        else:
            color = "#95A5A6"  # Gray for other nodes
        node_colors.append(color)
    
    # Create the Sankey diagram
    fig = go.Figure(data=[go.Sankey(
        node=dict(
            pad=15,
            thickness=20,
            line=dict(color="black", width=0.5),
            label=[node["name"] for node in data["nodes"]],
            color=node_colors,
            customdata=[node.get("description", "") for node in data["nodes"]],
            hovertemplate="Node: %{label}<br>Description: %{customdata}<extra></extra>"
        ),
        link=dict(
            source=[link["source"] for link in data["links"]],
            target=[link["target"] for link in data["links"]],
            value=[link["value"] for link in data["links"]],
            customdata=[link.get("description", "") for link in data["links"]],
            hovertemplate="From: %{source.label}<br>To: %{target.label}<br>" +
                         "Value: %{value}<br>Description: %{customdata}<extra></extra>"
        )
    )])
    
    # Update layout
    fig.update_layout(
        title_text="Feature Extraction Flow",
        font_size=12,
        height=600,
        margin=dict(t=40, l=0, r=0, b=0)
    )
    
    return fig

def main():
    """Main function for the Feature Extraction visualization page."""
    st.title("Feature Extraction Flow Visualization")
    
    st.markdown("""
    This visualization shows how raw data transforms into different features through various extraction methods.
    The thickness of the connections represents the volume or importance of the data flow.
    """)
    
    # Data input selection
    input_method = st.sidebar.radio(
        "Select data source:",
        ["Sample Data", "Upload JSON", "Paste JSON"]
    )
    
    # Initialize session state for node highlighting
    if "clicked_node" not in st.session_state:
        st.session_state.clicked_node = None
    
    # Data loading based on selected method
    data = None
    if input_method == "Sample Data":
        data = load_sample_data()
    elif input_method == "Upload JSON":
        uploaded_file = st.sidebar.file_uploader("Upload a JSON file", type="json")
        if uploaded_file:
            try:
                data = json.load(uploaded_file)
            except json.JSONDecodeError:
                st.error("Invalid JSON file. Please check the format.")
    else:  # Paste JSON
        json_str = st.sidebar.text_area("Paste your JSON data here")
        if json_str:
            try:
                data = json.loads(json_str)
            except json.JSONDecodeError:
                st.error("Invalid JSON data. Please check the format.")
    
    if data:
        # Validate data
        is_valid, error_message = validate_feature_extraction_data(data)
        if not is_valid:
            st.error(f"Invalid data format: {error_message}")
            return
        
        # Node selection for highlighting
        node_names = [node["name"] for node in data["nodes"]]
        selected_node = st.sidebar.selectbox(
            "Highlight a node:",
            ["None"] + node_names
        )
        
        # Update clicked node in session state
        if selected_node != "None":
            st.session_state.clicked_node = data["nodes"][node_names.index(selected_node)]["id"]
        else:
            st.session_state.clicked_node = None
        
        # Create and display Sankey diagram
        fig = create_sankey_diagram(data, st.session_state.clicked_node)
        st.plotly_chart(fig, use_container_width=True)
        
        # Display statistics
        st.subheader("Feature Extraction Statistics")
        col1, col2, col3 = st.columns(3)
        
        # Calculate statistics
        total_input = sum(link["value"] for link in data["links"] if link["source"] == 0)
        total_features = len([node for node in data["nodes"] if node["id"] != 0])
        avg_feature_value = sum(link["value"] for link in data["links"]) / len(data["links"])
        
        col1.metric("Total Input Records", f"{total_input:,}")
        col2.metric("Number of Features", total_features)
        col3.metric("Avg. Feature Flow", f"{avg_feature_value:,.1f}")

if __name__ == "__main__":
    main()
