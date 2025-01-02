import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import json
from typing import Dict, List, Union, Optional
import numpy as np

def create_sankey_diagram(data: Dict) -> go.Figure:
    """Create a Sankey diagram showing data flow through pipeline stages."""
    # Extract nodes and links
    nodes = data["nodes"]
    links = data["links"]
    
    # Create color scheme
    node_colors = ["#2ecc71" if node["name"] != "Discarded" else "#e74c3c" 
                  for node in nodes]
    link_colors = ["#3498db" if link["target"] != [n["id"] for n in nodes if n["name"] == "Discarded"][0]
                  else "#e74c3c" for link in links]
    
    # Create Sankey diagram
    fig = go.Figure(data=[go.Sankey(
        node=dict(
            pad=15,
            thickness=20,
            line=dict(color="black", width=0.5),
            label=[node["name"] for node in nodes],
            color=node_colors,
            customdata=[node["id"] for node in nodes],
            hovertemplate="Stage: %{label}<br>ID: %{customdata}<extra></extra>"
        ),
        link=dict(
            source=[link["source"] for link in links],
            target=[link["target"] for link in links],
            value=[link["value"] for link in links],
            color=link_colors,
            hovertemplate=(
                "From: %{source.label}<br>" +
                "To: %{target.label}<br>" +
                "Samples: %{value:,}<extra></extra>"
            )
        )
    )])
    
    # Update layout
    fig.update_layout(
        title_text="Data Pipeline Flow",
        font_size=12,
        height=600,
        margin=dict(t=40, l=0, r=0, b=0)
    )
    
    return fig

def calculate_statistics(data: Dict) -> pd.DataFrame:
    """Calculate statistics for each pipeline stage."""
    stats = []
    nodes = {node["id"]: node["name"] for node in data["nodes"]}
    discarded_id = [id for id, name in nodes.items() if name == "Discarded"][0]
    
    # Calculate incoming and outgoing samples for each node
    for node_id, node_name in nodes.items():
        if node_name == "Discarded":
            continue
            
        # Calculate incoming samples
        incoming = sum(link["value"] for link in data["links"] 
                      if link["target"] == node_id)
        
        # Calculate outgoing samples (excluding discarded)
        outgoing = sum(link["value"] for link in data["links"]
                      if link["source"] == node_id and link["target"] != discarded_id)
        
        # Calculate dropped samples
        dropped = sum(link["value"] for link in data["links"]
                     if link["source"] == node_id and link["target"] == discarded_id)
        
        # Calculate drop rate
        total_out = outgoing + dropped
        drop_rate = (dropped / total_out * 100) if total_out > 0 else 0
        
        stats.append({
            "Stage": node_name,
            "Incoming Samples": incoming,
            "Outgoing Samples": outgoing,
            "Dropped Samples": dropped,
            "Drop Rate (%)": round(drop_rate, 2)
        })
    
    return pd.DataFrame(stats)

def validate_data(data: Dict) -> bool:
    """Validate the input data format."""
    try:
        # Check required fields
        if not all(key in data for key in ["nodes", "links"]):
            st.error("Missing required fields: nodes and links")
            return False
            
        # Validate nodes
        if not all(all(key in node for key in ["id", "name"]) for node in data["nodes"]):
            st.error("Invalid node format: each node must have id and name")
            return False
            
        # Check for Discarded node
        if not any(node["name"] == "Discarded" for node in data["nodes"]):
            st.error("Missing Discarded node")
            return False
            
        # Validate links
        if not all(all(key in link for key in ["source", "target", "value"]) 
                  for link in data["links"]):
            st.error("Invalid link format: each link must have source, target, and value")
            return False
            
        # Validate node references
        node_ids = {node["id"] for node in data["nodes"]}
        for link in data["links"]:
            if link["source"] not in node_ids or link["target"] not in node_ids:
                st.error("Invalid node reference in links")
                return False
                
        return True
    except Exception as e:
        st.error(f"Error validating data: {str(e)}")
        return False

def main():
    """Main function for the Error/Dropout Tracking page."""
    st.title("Error/Dropout Tracking")
    st.write("""
    Visualize how data samples flow through your pipeline stages, tracking where samples
    are dropped or flagged. This helps identify potential bottlenecks and data quality issues.
    """)
    
    # Data input options
    data_input = st.radio(
        "Choose data input method:",
        ["Use sample data", "Upload JSON file", "Paste JSON data"]
    )
    
    data = None
    
    if data_input == "Use sample data":
        with open("data/error_dropout_sample.json", "r") as f:
            data = json.load(f)
            
    elif data_input == "Upload JSON file":
        uploaded_file = st.file_uploader("Upload JSON file", type="json")
        if uploaded_file:
            try:
                data = json.load(uploaded_file)
            except json.JSONDecodeError:
                st.error("Invalid JSON file")
                return
        else:
            st.error("Please upload a JSON file")
            return
            
    else:  # Paste JSON data
        json_str = st.text_area("Paste JSON data here")
        if json_str:
            try:
                data = json.loads(json_str)
            except json.JSONDecodeError:
                st.error("Invalid JSON")
                return
        else:
            st.error("Please enter JSON data")
            return
    
    if data and validate_data(data):
        # Show/hide dropout paths
        show_dropouts = st.checkbox(
            "Show dropout paths",
            value=True,
            help="Toggle to show or hide paths leading to the Discarded node"
        )
        
        # Create visualization
        fig = create_sankey_diagram(data)
        
        # Filter out dropout paths if needed
        if not show_dropouts:
            discarded_id = [node["id"] for node in data["nodes"] 
                          if node["name"] == "Discarded"][0]
            filtered_links = [link for link in data["links"] 
                            if link["target"] != discarded_id]
            filtered_data = {
                "nodes": data["nodes"],
                "links": filtered_links
            }
            fig = create_sankey_diagram(filtered_data)
        
        # Display visualization
        st.plotly_chart(fig, use_container_width=True)
        
        # Display statistics
        st.subheader("Pipeline Statistics")
        stats_df = calculate_statistics(data)
        st.dataframe(stats_df)
        
        # Display key metrics
        col1, col2 = st.columns(2)
        with col1:
            total_dropped = stats_df["Dropped Samples"].sum()
            st.metric("Total Samples Dropped", f"{total_dropped:,}")
        with col2:
            avg_drop_rate = stats_df["Drop Rate (%)"].mean()
            st.metric("Average Drop Rate", f"{avg_drop_rate:.2f}%")

if __name__ == "__main__":
    main()
