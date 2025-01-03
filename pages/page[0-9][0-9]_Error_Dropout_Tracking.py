import streamlit as st
import plotly.graph_objects as go
import json
from typing import Dict, List, Any
import pandas as pd

def load_sample_data() -> Dict[str, List[Dict[str, Any]]]:
    """Load sample error/dropout tracking data."""
    with open("data/error_dropout_sample.json", "r") as f:
        return json.load(f)

def validate_data(data: Dict[str, List[Dict[str, Any]]]) -> bool:
    """Validate the input data format."""
    if not isinstance(data, dict):
        return False
    
    if "nodes" not in data or "links" not in data:
        return False
        
    # Check nodes format
    nodes = data["nodes"]
    if not isinstance(nodes, list):
        return False
        
    node_ids = set()
    has_discard_node = False
    for node in nodes:
        if not isinstance(node, dict):
            return False
        if "id" not in node or "name" not in node:
            return False
        if not isinstance(node["id"], int):
            return False
        if node["id"] in node_ids:
            return False
        node_ids.add(node["id"])
        if node["name"] == "Discarded":
            has_discard_node = True
            
    # Check links format
    links = data["links"]
    if not isinstance(links, list):
        return False
        
    has_dropout_path = False
    for link in links:
        if not isinstance(link, dict):
            return False
        if "source" not in link or "target" not in link or "value" not in link:
            return False
        if link["source"] not in node_ids or link["target"] not in node_ids:
            return False
        if not isinstance(link["value"], (int, float)) or link["value"] < 0:
            return False
        # Check if this link leads to a discard node
        for node in nodes:
            if node["id"] == link["target"] and node["name"] == "Discarded":
                has_dropout_path = True
                
    # Ensure there's at least one dropout path
    if not has_discard_node or not has_dropout_path:
        return False
            
    return True

def create_sankey_diagram(data: Dict[str, List[Dict[str, Any]]]) -> go.Figure:
    """Create a Sankey diagram visualization."""
    fig = go.Figure(data=[go.Sankey(
        node=dict(
            pad=15,
            thickness=20,
            line=dict(color="black", width=0.5),
            label=[node["name"] for node in data["nodes"]],
            color=["#2E86C1" if node["name"] != "Discarded" else "#E74C3C" 
                  for node in data["nodes"]]
        ),
        link=dict(
            source=[link["source"] for link in data["links"]],
            target=[link["target"] for link in data["links"]],
            value=[link["value"] for link in data["links"]],
            color=["rgba(46, 134, 193, 0.4)" if link["target"] != 5 else "rgba(231, 76, 60, 0.4)"
                  for link in data["links"]],
            hovertemplate="From: %{source.label}<br>" +
                         "To: %{target.label}<br>" +
                         "Samples: %{value:,.0f}<extra></extra>"
        )
    )])
    
    fig.update_layout(
        title_text="Data Sample Flow Through Pipeline",
        font_size=12,
        height=600,
        hovermode="x",
        plot_bgcolor="white",
        paper_bgcolor="white"
    )
    
    return fig

def calculate_statistics(data: Dict[str, List[Dict[str, Any]]]) -> pd.DataFrame:
    """Calculate statistics about data loss at each stage."""
    stats = []
    nodes = {node["id"]: node["name"] for node in data["nodes"]}
    
    for node_id in nodes:
        if nodes[node_id] == "Discarded":
            continue
            
        incoming = sum(link["value"] for link in data["links"] 
                      if link["target"] == node_id)
        outgoing = sum(link["value"] for link in data["links"] 
                      if link["source"] == node_id)
        dropped = sum(link["value"] for link in data["links"] 
                     if link["source"] == node_id and link["target"] == 5)
        
        if node_id == 0:  # Raw Data
            incoming = outgoing + dropped
            
        stats.append({
            "Stage": nodes[node_id],
            "Incoming Samples": incoming,
            "Outgoing Samples": outgoing - dropped,
            "Dropped Samples": dropped,
            "Drop Rate (%)": round(dropped / incoming * 100, 2) if incoming > 0 else 0
        })
        
    return pd.DataFrame(stats)

def main():
    st.title("Error/Dropout Tracking")
    st.write("""
    Visualize how data samples flow through your pipeline and identify where samples are being dropped
    or flagged. This helps identify potential bottlenecks and data quality issues.
    """)
    
    # Data input section
    st.subheader("Data Input")
    data_input = st.radio(
        "Choose data input method:",
        ["Use sample data", "Upload JSON file", "Paste JSON data"]
    )
    
    # Optional filtering
    show_dropouts = st.checkbox("Show dropout paths", value=True,
                              help="Toggle visibility of paths leading to discarded samples")
    
    try:
        if data_input == "Use sample data":
            data = load_sample_data()
        elif data_input == "Upload JSON file":
            uploaded_file = st.file_uploader("Upload JSON file", type="json")
            if uploaded_file:
                data = json.load(uploaded_file)
            else:
                st.info("Please upload a JSON file")
                return
        else:  # Paste JSON data
            json_str = st.text_area("Paste JSON data here")
            if json_str:
                data = json.loads(json_str)
            else:
                st.info("Please paste JSON data")
                return
                
        # Validate data
        if not validate_data(data):
            st.error("Invalid data format. Please check the documentation for the required format.")
            return
            
        # Filter data if dropout paths are hidden
        if not show_dropouts:
            filtered_data = {
                "nodes": [node for node in data["nodes"] if node["name"] != "Discarded"],
                "links": [link for link in data["links"] if link["target"] != 5]
            }
            viz_data = filtered_data
        else:
            viz_data = data
            
        # Create visualization
        st.subheader("Data Flow Visualization")
        fig = create_sankey_diagram(viz_data)
        st.plotly_chart(fig, use_container_width=True)
        
        # Display statistics
        st.subheader("Data Loss Statistics")
        stats_df = calculate_statistics(data)
        st.dataframe(stats_df)
        
        # Show total data loss
        total_input = stats_df.iloc[0]["Incoming Samples"]
        total_output = stats_df.iloc[-1]["Outgoing Samples"]
        total_loss = total_input - total_output
        total_loss_pct = round((total_loss / total_input) * 100, 2)
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric(
                "Total Data Loss",
                f"{total_loss:,} samples",
                delta=-total_loss_pct,
                delta_color="inverse"
            )
        with col2:
            st.metric(
                "Data Retention Rate",
                f"{100 - total_loss_pct:.1f}%",
                delta=total_output,
                delta_color="normal"
            )
        
    except Exception as e:
        st.error(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    main()
