import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import json
from typing import List, Dict, Union
import plotly.express as px

def load_sample_data() -> List[Dict[str, Union[int, str, float]]]:
    """Load sample resource consumption data."""
    with open("data/resource_consumption_sample.json", "r") as f:
        return json.load(f)

def validate_data(data: List[Dict[str, Union[int, str, float]]]) -> bool:
    """Validate the input data format."""
    if not isinstance(data, list) or len(data) < 1:
        return False
    
    ids = set()
    for item in data:
        if not isinstance(item, dict):
            return False
        if "id" not in item or "name" not in item or ("time" not in item and "compute" not in item):
            return False
        if item["id"] in ids:
            return False
        ids.add(item["id"])
        time_val = item.get("time", 0)
        compute_val = item.get("compute", 0)
        if not isinstance(time_val, (int, float)) or not isinstance(compute_val, (int, float)):
            return False
        if float(time_val) < 0 or float(compute_val) < 0:
            return False
    return True

def create_resource_chart(data: List[Dict[str, Union[int, str, float]]], metric: str = "time") -> go.Figure:
    """Create a horizontal bar chart showing resource consumption."""
    df = pd.DataFrame(data)
    
    # Sort data if requested
    sort_order = st.radio("Sort by:", ["Original", "Ascending", "Descending"], horizontal=True)
    if sort_order != "Original":
        df = df.sort_values(by=metric, ascending=(sort_order == "Ascending"))
    
    # Create horizontal bar chart
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=df[metric],
        y=df["name"],
        orientation='h',
        marker_color='rgb(55, 83, 109)',
        hovertemplate=f"<b>%{{y}}</b><br>{metric}: %{{x}}<extra></extra>"
    ))
    
    # Update layout
    fig.update_layout(
        title=f"Pipeline Stage {metric.title()} Consumption",
        xaxis_title=f"{metric.title()} {'(seconds)' if metric == 'time' else '(% utilization)'}",
        yaxis_title="Pipeline Stage",
        height=400,
        margin=dict(l=0, r=0, t=40, b=0),
        plot_bgcolor='white'
    )
    
    return fig

def main():
    st.title("Resource Consumption Visualization")
    st.write("""
    Visualize time or compute resources consumed by each stage in a data pipeline.
    Identify bottlenecks and resource-intensive stages to optimize pipeline performance.
    """)
    
    # Data input method selection
    data_input = st.radio(
        "Select data input method:",
        ["Sample Data", "Upload JSON", "Paste JSON"],
        horizontal=True
    )
    
    data = None
    if data_input == "Sample Data":
        data = load_sample_data()
    elif data_input == "Upload JSON":
        uploaded_file = st.file_uploader("Upload JSON file", type=["json"])
        if uploaded_file:
            try:
                data = json.load(uploaded_file)
            except json.JSONDecodeError:
                st.error("Invalid JSON file")
    else:  # Paste JSON
        json_str = st.text_area("Paste JSON data")
        if json_str:
            try:
                data = json.loads(json_str)
            except json.JSONDecodeError:
                st.error("Invalid JSON format")
    
    if data:
        if validate_data(data):
            # Select metric to visualize
            metric = st.selectbox(
                "Select metric to visualize:",
                ["time", "compute"],
                format_func=lambda x: "Time (seconds)" if x == "time" else "Compute (% utilization)"
            )
            
            # Create and display chart
            fig = create_resource_chart(data, metric)
            st.plotly_chart(fig, use_container_width=True)
            
            # Display statistics
            df = pd.DataFrame(data)
            st.subheader("Pipeline Statistics")
            col1, col2 = st.columns(2)
            
            with col1:
                st.metric("Total Time", f"{df['time'].sum()} seconds")
                st.metric("Average Stage Time", f"{df['time'].mean():.1f} seconds")
                st.metric("Longest Stage", f"{df.loc[df['time'].idxmax(), 'name']}")
            
            with col2:
                st.metric("Max Compute", f"{df['compute'].max()}%")
                st.metric("Average Compute", f"{df['compute'].mean():.1f}%")
                st.metric("Highest Compute Stage", f"{df.loc[df['compute'].idxmax(), 'name']}")
        else:
            st.error("Invalid data format. Please check the documentation for the required format.")
    
    # Documentation
    with st.expander("Data Format Documentation"):
        st.write("""
        The data should be a JSON array of objects with the following structure:
        ```json
        [
          {
            "id": 0,              // Unique identifier
            "name": "Stage Name", // Stage label
            "time": 60,          // Time in seconds
            "compute": 25        // CPU/GPU usage percentage
          }
        ]
        ```
        """)

if __name__ == "__main__":
    main()
