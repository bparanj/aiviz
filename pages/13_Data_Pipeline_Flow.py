import streamlit as st
import json
import plotly.graph_objects as go
import networkx as nx
from pathlib import Path

def load_sample_data():
    """Load sample data from JSON file."""
    sample_path = Path(__file__).parent.parent / "data" / "data_pipeline_flow_sample.json"
    with open(sample_path, "r") as f:
        return json.load(f)

def validate_pipeline_data(data):
    """Validate the input data format."""
    try:
        if not isinstance(data, dict):
            raise ValueError("Data must be a dictionary")
        
        if "nodes" not in data or "links" not in data:
            raise ValueError("Data must contain 'nodes' and 'links' keys")
        
        # Validate nodes
        node_ids = set()
        for node in data["nodes"]:
            if "id" not in node or "name" not in node:
                raise ValueError("Each node must have 'id' and 'name' fields")
            if not isinstance(node["id"], int):
                raise ValueError("Node 'id' must be an integer")
            if node["id"] in node_ids:
                raise ValueError("Node IDs must be unique")
            node_ids.add(node["id"])
        
        # Validate links
        for link in data["links"]:
            if "source" not in link or "target" not in link or "value" not in link:
                raise ValueError("Each link must have 'source', 'target', and 'value' fields")
            if link["source"] not in node_ids or link["target"] not in node_ids:
                raise ValueError("Link source and target must reference valid node IDs")
            if not isinstance(link["value"], (int, float)) or link["value"] < 0:
                raise ValueError("Link value must be a non-negative number")
        
        if len(data["nodes"]) < 2:
            raise ValueError("Pipeline must have at least 2 nodes")
        
        return True
    except ValueError as e:
        raise ValueError(str(e))

def create_sankey_diagram(data, highlight_node=None):
    """Create a Sankey diagram using Plotly."""
    # Filter data based on visibility settings
    show_filtered = st.session_state.get('show_filtered', True)
    
    # Filter nodes and links if needed
    filtered_data = data.copy()
    if not show_filtered:
        # Remove "Filtered Out" nodes and their links
        filtered_nodes = [node for node in data["nodes"] if node["name"] != "Filtered Out"]
        node_ids = {node["id"] for node in filtered_nodes}
        filtered_links = [link for link in data["links"] 
                         if link["source"] in node_ids and link["target"] in node_ids]
        filtered_data = {"nodes": filtered_nodes, "links": filtered_links}
    
    # Create node labels and colors
    labels = [node["name"] for node in filtered_data["nodes"]]
    
    # Create color scheme
    node_colors = ['#2E86C1' if node["name"] == "Raw Data"
                  else '#E74C3C' if node["name"] == "Filtered Out"
                  else '#27AE60' if "Set" in node["name"]
                  else '#F39C12'
                  for node in data["nodes"]]
    
    # Prepare link colors
    link_colors = []
    for link in data["links"]:
        if highlight_node is not None and (link["source"] == highlight_node or link["target"] == highlight_node):
            link_colors.append('rgba(255, 165, 0, 0.8)')  # Highlighted links in orange
        else:
            link_colors.append('rgba(128, 128, 128, 0.3)')  # Regular links in gray
    
    # Create Sankey diagram
    fig = go.Figure(data=[go.Sankey(
        node=dict(
            pad=15,
            thickness=20,
            line=dict(color="black", width=0.5),
            label=labels,
            color=node_colors,
            customdata=[node["id"] for node in data["nodes"]],
            hovertemplate='Node: %{label}<br>ID: %{customdata}<extra></extra>'
        ),
        link=dict(
            source=[link["source"] for link in data["links"]],
            target=[link["target"] for link in data["links"]],
            value=[link["value"] for link in data["links"]],
            color=link_colors,
            hovertemplate='From: %{source.label}<br>'+
                         'To: %{target.label}<br>'+
                         'Records: %{value:,.0f}<extra></extra>'
        )
    )])
    
    # Update layout
    fig.update_layout(
        title="Data Pipeline Flow",
        font=dict(size=12),
        height=600,
        margin=dict(t=40, l=0, r=0, b=0)
    )
    
    return fig

def main():
    st.title("Data Pipeline Flow Visualization")
    st.write("""
    Visualize how data flows through different preprocessing steps and how the volume changes at each stage.
    See how many records continue through the pipeline and how many get filtered out.
    """)
    
    # Initialize session state
    if "show_filtered" not in st.session_state:
        st.session_state["show_filtered"] = True
    if "clicked_node" not in st.session_state:
        st.session_state["clicked_node"] = None
    
    # Add controls in sidebar
    st.sidebar.header("Controls")
    
    # Data source selection
    data_source = st.sidebar.radio(
        "Select data source:",
        ["Sample Data", "Upload JSON", "Paste JSON"]
    )
    
    # Branch visibility control
    show_filtered = st.sidebar.checkbox(
        "Show filtered branches",
        value=st.session_state["show_filtered"],
        help="Toggle visibility of filtered data branches"
    )
    st.session_state["show_filtered"] = show_filtered
    
    # Load data based on selected source
    data = None
    
    try:
        if data_source == "Sample Data":
            data = load_sample_data()
        elif data_source == "Upload JSON":
            uploaded_file = st.sidebar.file_uploader("Upload a JSON file", type="json")
            if uploaded_file:
                try:
                    data = json.load(uploaded_file)
                except json.JSONDecodeError:
                    st.error("Invalid JSON file format")
                    return
            else:
                st.info("Please upload a JSON file")
                return
        else:  # Paste JSON
            json_str = st.sidebar.text_area("Paste your JSON data here")
            if json_str:
                try:
                    data = json.loads(json_str)
                except json.JSONDecodeError:
                    st.error("Invalid JSON format")
                    return
            else:
                st.info("Please paste your JSON data")
                return
        
        if data is None:
            return
        
        # Validate data
        try:
            validate_pipeline_data(data)
        except ValueError as e:
            st.error(f"Invalid data: {str(e)}")
            return
        
        # Track clicked node for highlighting
        clicked_node = st.session_state.get('clicked_node', None)
        if 'clicked_node' not in st.session_state:
            st.session_state.clicked_node = None
        
        # Display pipeline statistics first
        st.subheader("Pipeline Statistics")
        
        # Calculate statistics
        total_input = sum(link["value"] for link in data["links"] if link["source"] == 0)
        filtered_out = sum(link["value"] for link in data["links"] 
                         if any(node["name"] == "Filtered Out" and node["id"] == link["target"] 
                               for node in data["nodes"]))
        final_output = sum(link["value"] for link in data["links"]
                         if any(("Set" in node["name"] or node["name"] == "Final Dataset") 
                               and node["id"] == link["target"] for node in data["nodes"]))
        
        # Display statistics in columns
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Input Records", f"{total_input:,}")
        with col2:
            st.metric("Filtered Out Records", f"{filtered_out:,}")
        with col3:
            st.metric("Final Output Records", f"{final_output:,}")
        
        # Display retention rate
        retention_rate = (final_output / total_input * 100) if total_input > 0 else 0
        st.metric("Data Retention Rate", f"{retention_rate:.1f}%")
        
        # Create and display visualization
        fig = create_sankey_diagram(data, highlight_node=st.session_state.clicked_node)
        
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
                if 'customdata' in point:
                    st.session_state.clicked_node = point['customdata']
                    st.rerun()
        
    except Exception as e:
        st.error(f"Error processing data: {str(e)}")

if __name__ == "__main__":
    main()
