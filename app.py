import streamlit as st

st.set_page_config(
    page_title="Home - ML Visualization Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Hide default menu and rename navigation
hide_default_format = """
       <style>
       #MainMenu {visibility: hidden; }
       footer {visibility: hidden;}
       div[data-testid="stSidebarNav"] > div:nth-child(1) > button:nth-child(1) {display: none;}
       div[data-testid="stSidebarNav"] ul {margin-top: -1rem;}
       div[data-testid="stSidebarNav"] ul li:first-child {display: none;}
       div[data-testid="stSidebarNav"] ul li:nth-child(2)::before {
           content: "Home";
           margin-left: 0.5rem;
           color: rgb(49, 51, 63);
           font-size: 14px;
       }
       div[data-testid="stSidebarNav"] ul li:nth-child(2) a {display: none;}
       </style>
"""
st.markdown(hide_default_format, unsafe_allow_html=True)

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
- **Relationship Inference**: Analyze direct and indirect relationships in data
- **Graph Clustering**: Explore community structures in networks
- **Node Influence**: Analyze node importance and centrality
- **Neural Network Topology**: Visualize neural network architecture and weights
- **Data Pipeline Flow**: Visualize data transformations and flow in ML pipelines
- **Feature Extraction**: Explore how raw data transforms into different features
- **Model Input/Output Distribution**: Visualize data flow through model components and outputs
- **Resource Consumption**: Analyze time and compute resource usage across pipeline stages

Use the sidebar to navigate between different visualizations. Each visualization supports custom data input via JSON format.
""")

st.sidebar.markdown("""
### About
This dashboard combines multiple ML visualization tools to help you better understand your models and data.
""")
