import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import json
from utils.data_validation import validate_pairwise_similarity

# Page title and description
st.title("Pairwise Similarity")
st.write("Visualize how similar or dissimilar multiple samples are to each other. "
         "This visualization helps identify clusters of highly similar samples and spot outliers.")

# Sample data
sample_data = {
    "samples": ["Article1", "Article2", "Article3", "Article4", "Article5"],
    "matrix": [
        [1.00, 0.85, 0.25, 0.15, 0.35],
        [0.85, 1.00, 0.30, 0.20, 0.40],
        [0.25, 0.30, 1.00, 0.70, 0.15],
        [0.15, 0.20, 0.70, 1.00, 0.10],
        [0.35, 0.40, 0.15, 0.10, 1.00]
    ]
}

# Data input section
st.header("Data Input")
st.write("Choose between sample data or input your own similarity matrix:")

data_source = st.radio("Choose data source:", ["Use sample data", "Input custom data"])

if data_source == "Use sample data":
    data = sample_data
else:
    st.write("Enter your similarity data in JSON format:")
    st.write("Example format:")
    st.code(json.dumps(sample_data, indent=2))
    
    json_input = st.text_area("Enter your JSON data:")
    if json_input:
        try:
            data = json.loads(json_input)
            # Validate the input data
            is_valid, error_msg = validate_pairwise_similarity(data)
            if not is_valid:
                st.error(f"Invalid data format: {error_msg}")
                st.stop()
        except json.JSONDecodeError:
            st.error("Invalid JSON format. Please check your input and try again.")
            st.stop()
        except Exception as e:
            st.error(f"Error: {str(e)}")
            st.stop()
    else:
        data = sample_data

# Display raw data
st.header("Raw Data")
if st.checkbox("Show raw data"):
    st.write("Samples:", data["samples"])
    st.write("Similarity Matrix:")
    st.write(pd.DataFrame(data["matrix"], 
                         index=data["samples"],
                         columns=data["samples"]))

# Visualization options
st.header("Visualization Options")

col1, col2 = st.columns(2)

# Color scale selection
with col1:
    color_scale = st.selectbox(
        "Select color scale:",
        ["Viridis", "Plasma", "Inferno", "Magma", "RdBu", "YlOrRd"]
    )

# Clustering option
with col2:
    enable_clustering = st.checkbox("Enable clustering", help="Reorder samples to reveal natural groupings")

# Process data for clustering if enabled
matrix = np.array(data["matrix"])
samples = data["samples"]

if enable_clustering:
    # Perform hierarchical clustering
    from scipy.cluster import hierarchy
    from scipy.spatial.distance import squareform
    
    # Convert similarity to distance (1 - similarity)
    distances = 1 - matrix
    # Make sure diagonal is 0
    np.fill_diagonal(distances, 0)
    
    # Perform clustering
    linkage = hierarchy.linkage(squareform(distances), method='ward')
    # Get the order of samples after clustering
    dendro = hierarchy.dendrogram(linkage, no_plot=True)
    order = dendro['leaves']
    
    # Reorder matrix and samples
    matrix = matrix[order][:, order]
    samples = [samples[i] for i in order]

# Selected sample highlighting
selected_sample = st.selectbox(
    "Select sample to highlight relationships:",
    ["None"] + samples
)

# Create heatmap
heatmap_data = go.Heatmap(
    z=matrix,
    x=samples,
    y=samples,
    colorscale=color_scale.lower(),
    zmin=0,
    zmax=1,
    hoverongaps=False,
    hovertemplate=(
        "Sample 1: %{y}<br>"
        "Sample 2: %{x}<br>"
        "Similarity: %{z:.3f}<br>"
        "<extra></extra>"
    )
)

fig = go.Figure(data=[heatmap_data])

# Add highlighting for selected sample
if selected_sample != "None":
    sample_idx = samples.index(selected_sample)
    
    # Add horizontal and vertical highlight lines
    fig.add_shape(
        type="rect",
        x0=-0.5,
        x1=len(samples)-0.5,
        y0=sample_idx-0.5,
        y1=sample_idx+0.5,
        fillcolor="rgba(255, 255, 0, 0.2)",
        line=dict(width=0),
        layer="below"
    )
    fig.add_shape(
        type="rect",
        x0=sample_idx-0.5,
        x1=sample_idx+0.5,
        y0=-0.5,
        y1=len(samples)-0.5,
        fillcolor="rgba(255, 255, 0, 0.2)",
        line=dict(width=0),
        layer="below"
    )

# Update layout
fig.update_layout(
    title={
        'text': "Pairwise Similarity Heatmap",
        'y':0.95,
        'x':0.5,
        'xanchor': 'center',
        'yanchor': 'top'
    },
    xaxis_title="Samples",
    yaxis_title="Samples",
    width=800,
    height=800,
    xaxis={'side': 'bottom', 'constrain': 'domain'},
    yaxis={'side': 'left', 'constrain': 'domain'},
    showlegend=False
)

# Display the plot
st.plotly_chart(fig)

# Understanding the visualization
st.header("Understanding the Visualization")
st.write("""
- The heatmap shows pairwise similarities between samples
- Darker/brighter colors indicate higher similarity
- Diagonal values are 1.0 (a sample is always fully similar to itself)
- Hover over cells to see exact similarity values
- Look for clusters of high similarity (bright regions)
- Identify outliers (rows/columns with consistently low similarity)
""")
