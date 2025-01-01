import streamlit as st

# Configure the app and set the first page name to "Home"
st.set_page_config(
    page_title="ML Visualization Dashboard",
    page_icon="📊",
    layout="wide"
)

# Display the main content
st.title("ML Visualization Dashboard")

st.markdown("""
Welcome to the Machine Learning Visualization Dashboard! This application provides interactive visualizations for:

- **Hyperparameter Impact**: Analyze how different hyperparameter settings affect model performance
- **Dataset Variations**: Compare model performance across different dataset splits
- **Correlation Matrix**: Explore feature correlations in your data
- **Confusion Matrix**: Visualize classification model performance across classes
- **Attention Map**: Visualize attention weights in neural networks
- **Feature-Feature Interactions**: Explore relationships between different features
- **Pairwise Similarity**: Compare similarities between different samples
- **Knowledge Graph**: Visualize relationships between entities

Use the sidebar to navigate between different visualizations. Each visualization supports custom data input via JSON format.
""")

st.sidebar.markdown("""
### About
This dashboard combines multiple ML visualization tools to help you better understand your models and data.
""")
