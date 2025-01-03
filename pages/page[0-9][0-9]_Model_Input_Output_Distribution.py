import streamlit as st
import json
import plotly.graph_objects as go
from typing import Dict, List, Any
import pandas as pd
import sys
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from tests.test_model_input_output import validate_model_input_output_data

def load_sample_data() -> Dict[str, List[Dict[str, Any]]]:
    """Load sample data for model input/output distribution visualization."""
    with open("data/model_input_output_sample.json", "r") as f:
        return json.load(f)

def create_sankey_diagram(data: Dict[str, List[Dict[str, Any]]]) -> go.Figure:
    """Create a Sankey diagram showing model input/output distribution."""
    # Extract nodes and links from data
    nodes = data["nodes"]
    links = data["links"]
    
    # Create node labels and colors
    node_labels = [node["name"] for node in nodes]
    node_colors = ["#1f77b4"] * len(nodes)  # Default blue color
    
    # Create the Sankey diagram
    fig = go.Figure(data=[go.Sankey(
        node=dict(
            pad=15,
            thickness=20,
            line=dict(color="black", width=0.5),
            label=node_labels,
            color=node_colors,
            customdata=list(range(len(nodes))),  # Store node indices for highlighting
            hovertemplate="Node: %{label}<br>Total Flow: %{value}<extra></extra>"
        ),
        link=dict(
            source=[link["source"] for link in links],
            target=[link["target"] for link in links],
            value=[link["value"] for link in links],
            hovertemplate="From: %{source.label}<br>To: %{target.label}<br>Flow: %{value}<extra></extra>"
        )
    )])
    
    # Update layout
    fig.update_layout(
        title="Model Input/Output Distribution",
        font=dict(size=12),
        height=600,
        margin=dict(t=40, l=0, r=0, b=0)
    )
    
    return fig

def main():
    st.title("Model Input/Output Distribution")
    
    st.write("""
    Visualize how data flows through different model components and their outputs.
    See which portions of data go into specific model components and how they are distributed
    into downstream steps like post-processing or evaluation.
    """)
    
    # Data input selection
    data_input = st.radio(
        "Select Data Input Method",
        ["Sample Data", "Upload JSON", "Paste JSON"],
        help="Choose how to input your model input/output distribution data"
    )
    
    data = None
    
    if data_input == "Sample Data":
        data = load_sample_data()
        validation_errors = validate_model_input_output_data(data)
        if validation_errors:
            st.error("Sample data validation failed:")
            for error in validation_errors:
                st.error(f"- {error}")
            return
        st.info("Using sample data showing a typical model input/output flow")
        
    elif data_input == "Upload JSON":
        uploaded_file = st.file_uploader("Upload JSON file", type="json")
        if uploaded_file:
            try:
                data = json.load(uploaded_file)
                validation_errors = validate_model_input_output_data(data)
                if validation_errors:
                    st.error("Data validation failed:")
                    for error in validation_errors:
                        st.error(f"- {error}")
                    return
            except json.JSONDecodeError:
                st.error("Invalid JSON file. Please check the format.")
                
    else:  # Paste JSON
        json_str = st.text_area(
            "Paste JSON data",
            height=200,
            help="Paste your model input/output distribution data in JSON format"
        )
        if json_str:
            try:
                data = json.loads(json_str)
                validation_errors = validate_model_input_output_data(data)
                if validation_errors:
                    st.error("Data validation failed:")
                    for error in validation_errors:
                        st.error(f"- {error}")
                    return
            except json.JSONDecodeError:
                st.error("Invalid JSON format. Please check the syntax.")
    
    if data:
        # Display statistics
        st.subheader("Data Flow Statistics")
        total_input = sum(link["value"] for link in data["links"] if link["source"] == 0)
        total_output = sum(link["value"] for link in data["links"] if link["target"] in [4, 5])  # Post-processing and Evaluation
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Input Data", f"{total_input:,}")
        with col2: 
            st.metric("Total Output Data", f"{total_output:,}")
        with col3: 
            retention_rate = (total_output / total_input * 100) if total_input > 0 else 0
            st.metric("Data Retention Rate", f"{retention_rate:.1f}%")
        
        # Create and display Sankey diagram
        fig = create_sankey_diagram(data)
        st.plotly_chart(fig, use_container_width=True)
        
        # Add filtering options
        st.subheader("Filter Visualization")
        st.write("Select which components to show in the visualization:")
        
        # Create checkboxes for each node
        selected_nodes = []
        for node in data["nodes"]:
            if st.checkbox(node["name"], value=True, key=f"node_{node['id']}"):
                selected_nodes.append(node["id"])
        
        if len(selected_nodes) < len(data["nodes"]):
            # Filter data based on selection
            filtered_data = {
                "nodes": [node for node in data["nodes"] if node["id"] in selected_nodes],
                "links": [
                    link for link in data["links"] 
                    if link["source"] in selected_nodes and link["target"] in selected_nodes
                ]
            }
            
            # Update visualization with filtered data
            filtered_fig = create_sankey_diagram(filtered_data)
            st.plotly_chart(filtered_fig, use_container_width=True)

if __name__ == "__main__":
    main()
