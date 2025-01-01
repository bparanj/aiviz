import streamlit as st

st.set_page_config(
    page_title="ML Visualization Dashboard",
    page_icon="📊",
    layout="wide"
)

st.title("ML Visualization Dashboard")
st.sidebar.success("Home")

st.markdown("""
Welcome to the Machine Learning Visualization Dashboard! This application provides interactive visualizations for:

- **Hyperparameter Impact**: Analyze how different hyperparameter settings affect model performance
- **Dataset Variations**: Compare model performance across different dataset splits
- **Correlation Matrix**: Explore feature correlations in your data
- **Confusion Matrix**: Visualize classification model performance across classes

Use the sidebar to navigate between different visualizations. Each visualization supports custom data input via JSON format.
""")

st.sidebar.markdown("""
### About
This dashboard combines multiple ML visualization tools to help you better understand your models and data.
""")
