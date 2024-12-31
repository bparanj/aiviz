import streamlit as st
import json
import plotly.graph_objects as go
import numpy as np
from utils.data_validation import validate_correlation_matrix, load_json_data

st.set_page_config(page_title="Correlation Matrix", page_icon="🔄")

st.title("Correlation Matrix Visualization")

# Sample data
sample_data = {
    "features": ["Age", "Income", "Education", "CreditScore"],
    "matrix": [
        [1.00, 0.65, 0.32, 0.78],
        [0.65, 1.00, 0.45, 0.25],
        [0.32, 0.45, 1.00, 0.11],
        [0.78, 0.25, 0.11, 1.00]
    ]
}

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
        valid, message = validate_correlation_matrix(data)
        if not valid:
            st.error(message)
            st.stop()
    else:
        data = None

if data is not None:
    # Color scale selection
    color_scale = st.selectbox(
        "Select color scale:",
        ["RdBu", "Viridis", "Plasma", "RdYlBu"],
        index=0
    )

    # Create heatmap
    fig = go.Figure(data=go.Heatmap(
        z=data["matrix"],
        x=data["features"],
        y=data["features"],
        colorscale=color_scale,
        zmin=-1,
        zmax=1,
        text=[[f"{val:.2f}" for val in row] for row in data["matrix"]],
        texttemplate="%{text}",
        textfont={"size": 12},
        hoverongaps=False
    ))

    fig.update_layout(
        title="Feature Correlation Matrix",
        height=600,
        width=800
    )

    st.plotly_chart(fig, use_container_width=True)

    # Display raw data
    st.subheader("Raw Data")
    st.json(data)
