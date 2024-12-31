import streamlit as st
import json
import plotly.graph_objects as go
from utils.data_validation import validate_dataset_variations, load_json_data

st.set_page_config(page_title="Dataset Variations", page_icon="📊")

st.title("Dataset Variations Visualization")

# Sample data
sample_data = [
    {"dataset": "Training", "metric": 0.90},
    {"dataset": "Validation", "metric": 0.85},
    {"dataset": "Test", "metric": 0.80}
]

# Data input
st.subheader("Data Input")
data_source = st.radio("Choose data source:", ["Use sample data", "Input custom data"])

if data_source == "Use sample data":
    data = sample_data
else:
    json_input = st.text_area("Enter your JSON data:", height=200)
    if json_input:
        loaded_data = load_json_data(json_input)
        if isinstance(loaded_data, tuple):
            st.error(loaded_data[1])
            st.stop()
        data = loaded_data
        valid, message = validate_dataset_variations(data)
        if not valid:
            st.error(message)
            st.stop()
    else:
        data = None

if data is not None:
    # Create visualization
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=[d["dataset"] for d in data],
        y=[d["metric"] for d in data],
        text=[f"{d['metric']:.3f}" for d in data],
        textposition='auto',
    ))
    
    fig.update_layout(
        title="Model Performance Across Datasets",
        xaxis_title="Dataset",
        yaxis_title="Performance Metric",
        yaxis_range=[0, 1],
        height=600
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Display raw data
    st.subheader("Raw Data")
    st.json(data)
