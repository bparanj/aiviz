import streamlit as st
import json
import plotly.graph_objects as go
from utils.data_validation import validate_hyperparameter_data, load_json_data

st.set_page_config(page_title="Hyperparameter Impact", page_icon="📈")

st.title("Hyperparameter Impact")

# Sample data
sample_data = [
    {"paramValue": "10 trees", "metric": 0.75},
    {"paramValue": "50 trees", "metric": 0.82},
    {"paramValue": "100 trees", "metric": 0.85},
    {"paramValue": "200 trees", "metric": 0.88},
    {"paramValue": "500 trees", "metric": 0.87}
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
        valid, message = validate_hyperparameter_data(data)
        if not valid:
            st.error(message)
            st.stop()
    else:
        data = None

if data is not None:
    # Create visualization
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=[d["paramValue"] for d in data],
        y=[d["metric"] for d in data],
        text=[f"{d['metric']:.3f}" for d in data],
        textposition='auto',
    ))
    
    fig.update_layout(
        title="Impact of Hyperparameter on Model Performance",
        xaxis_title="Hyperparameter Value",
        yaxis_title="Performance Metric",
        yaxis_range=[0, 1],
        height=600
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Add interactivity options
    st.subheader("Visualization Options")
    if st.button("Sort by Metric"):
        sorted_data = sorted(data, key=lambda x: x["metric"])
        data[:] = sorted_data
        st.rerun()

    # Display raw data
    st.subheader("Raw Data")
    st.json(data)
