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
        
        return True, ""
    except ValueError as e:
        return False, str(e)

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
    data = st.session_state.get("data")
    
    try:
        print(f"Data source selected: {data_source}")
        print(f"Initial data state: {data}")
        
        if data_source == "Sample Data":
            if data is None:
                data = load_sample_data()
                st.session_state["data"] = data
                print(f"Loaded sample data: {data is not None}")
        elif data_source == "Upload JSON":
            uploaded_file = st.sidebar.file_uploader("Upload a JSON file", type="json")
            if uploaded_file:
                try:
                    data = json.load(uploaded_file)
                    st.session_state["data"] = data
                    print(f"Loaded uploaded data: {data is not None}")
                except json.JSONDecodeError:
                    st.error("Invalid JSON file format")
                    print("Failed to parse uploaded JSON")
            else:
                st.info("Please upload a JSON file")
                print("No file uploaded")
        else:  # Paste JSON
            json_str = st.sidebar.text_area("Paste your JSON data here")
            if json_str:
                try:
                    data = json.loads(json_str)
                    st.session_state["data"] = data
                    print(f"Loaded pasted data: {data is not None}")
                except json.JSONDecodeError:
                    st.error("Invalid JSON format")
                    print("Failed to parse pasted JSON")
            else:
                st.info("Please paste your JSON data")
                print("No JSON text pasted")
        
        # Only proceed with visualization if we have valid data
        print(f"Data before validation: {data is not None}")
        if data is not None:
            # Validate data
            is_valid, error_msg = validate_pipeline_data(data)
            print(f"Validation result: valid={is_valid}, error={error_msg}")
            if not is_valid:
                st.error(f"Invalid data: {error_msg}")
                data = None  # Clear invalid data
                st.session_state["data"] = None
                print("Data cleared due to validation failure")
        
        # Only show visualization and stats if we have valid data
        if data is not None:
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
            
            try:
                # Create and display visualization
                print("Creating Sankey diagram...")
                highlight_node = st.session_state.get("clicked_node")  # Use dict-style access
                print(f"Using highlight_node: {highlight_node}")
                fig = create_sankey_diagram(data, highlight_node=highlight_node)
                print(f"Sankey diagram created successfully: {fig is not None}")
                print(f"Figure data: {fig.data}")
                print(f"Figure layout: {fig.layout}")
                
                # Display the visualization with click event handling
                print("Attempting to display plotly chart...")
                selected_point = st.plotly_chart(
                    fig,
                    use_container_width=True,
                    custom_events=['plotly_click']
                )
                print(f"Chart displayed successfully, selected_point: {selected_point}")
            
                # Handle click events
                if selected_point:
                    print(f"Processing click event: {selected_point}")
                    click_data = selected_point.get('plotly_click', {})
                    if click_data and click_data.get('points'):
                        point = click_data['points'][0]
                        if 'customdata' in point:
                            st.session_state["clicked_node"] = point['customdata']  # Use dict-style access
                            st.rerun()
            except Exception as e:
                print(f"Error during visualization: {str(e)}")
                import traceback
                print(f"Traceback: {traceback.format_exc()}")
                st.error(f"Error creating visualization: {str(e)}")
                raise  # Re-raise to ensure test failure captures the real error
        
    except Exception as e:
        print(f"Error processing data: {str(e)}")
        import traceback
        print(f"Traceback: {traceback.format_exc()}")
        st.error(f"Error processing data: {str(e)}")
        raise  # Re-raise to ensure test failure captures the real error

if __name__ == "__main__":
    main()
