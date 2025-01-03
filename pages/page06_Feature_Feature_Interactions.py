import streamlit as st
import plotly.graph_objects as go
from utils.data_validation import load_json_data, validate_feature_interactions

st.set_page_config(page_title="Feature-Feature Interactions", page_icon="⚙️")

st.title("Feature-Feature Interactions")
st.write("Visualize how features influence each other and identify potential redundant or synergistic feature pairs.")

# Sample data
SAMPLE_DATA = {
    "features": ["Height", "Weight", "HairLength", "RunningSpeed"],
    "matrix": [
        [1.00, 0.48, 0.15, 0.33],
        [0.48, 1.00, 0.05, 0.72],
        [0.15, 0.05, 1.00, 0.10],
        [0.33, 0.72, 0.10, 1.00]
    ]
}

# Data input section
st.header("Data Input")
st.write("Choose between sample data or input your own feature interaction matrix:")

data_source = st.radio("Choose data source:", ["Use sample data", "Input custom data"])

if data_source == "Use sample data":
    data = SAMPLE_DATA
else:
    st.write("Enter your feature interaction data in JSON format:")
    st.write("Example format:")
    st.code("""
    {
        "features": ["Feature1", "Feature2", "Feature3"],
        "matrix": [
            [1.00, 0.50, 0.30],
            [0.50, 1.00, 0.70],
            [0.30, 0.70, 1.00]
        ]
    }
    """)
    
    json_input = st.text_area("Enter your JSON data:", height=200)
    if json_input:
        loaded_data = load_json_data(json_input)
        if isinstance(loaded_data, tuple):
            st.error(loaded_data[1])
            st.stop()
        data = loaded_data
        valid, message = validate_feature_interactions(data)
        if not valid:
            st.error(message)
            st.stop()
    else:
        data = None

if data is not None:
    # Visualization options
    st.header("Visualization Options")
    col1, col2 = st.columns(2)
    
    with col1:
        color_scale = st.selectbox(
            "Select color scale:",
            ["Viridis", "RdYlBu", "YlOrRd", "Blues"],
            help="Choose the color scheme for the heatmap"
        )
    
    with col2:
        threshold = st.slider(
            "Interaction threshold:",
            min_value=0.0,
            max_value=1.0,
            value=0.0,
            step=0.05,
            help="Filter interactions below this threshold (they will appear faded)"
        )

    # Create masked matrix for threshold filtering
    matrix = data["matrix"]
    masked_matrix = [[val if val >= threshold else val/2 for val in row] for row in matrix]

    # Add highlighting controls
    highlight_feature = st.selectbox(
        "Highlight interactions for feature:",
        ["None"] + data["features"],
        help="Select a feature to highlight its interactions with other features"
    )

    # Create heatmap
    fig = go.Figure()

    # Add main heatmap
    heatmap = go.Heatmap(
        z=masked_matrix,
        x=data["features"],
        y=data["features"],
        colorscale=color_scale,
        zmin=0,
        zmax=1,
        text=[[f"{val:.2f}" for val in row] for row in matrix],
        texttemplate="%{text}",
        textfont={"size": 12},
        hoverongaps=False,
        hovertemplate="Feature 1: %{y}<br>Feature 2: %{x}<br>Interaction: %{text}<extra></extra>"
    )
    fig.add_trace(heatmap)

    # Add highlighting if a feature is selected
    if highlight_feature != "None":
        feature_idx = data["features"].index(highlight_feature)
        
        # Create highlighted row
        row_highlight = go.Scatter(
            x=data["features"],
            y=[highlight_feature] * len(data["features"]),
            mode='markers',
            marker=dict(
                symbol='square',
                size=40,
                color='rgba(255, 255, 0, 0.3)',
                line=dict(color='rgba(255, 255, 0, 0.5)', width=2)
            ),
            showlegend=False,
            hoverinfo='skip'
        )
        
        # Create highlighted column
        col_highlight = go.Scatter(
            x=[highlight_feature] * len(data["features"]),
            y=data["features"],
            mode='markers',
            marker=dict(
                symbol='square',
                size=40,
                color='rgba(255, 255, 0, 0.3)',
                line=dict(color='rgba(255, 255, 0, 0.5)', width=2)
            ),
            showlegend=False,
            hoverinfo='skip'
        )
        
        fig.add_trace(row_highlight)
        fig.add_trace(col_highlight)

    fig.update_layout(
        title={
            'text': "Feature-Feature Interactions Heatmap",
            'y':0.95,
            'x':0.5,
            'xanchor': 'center',
            'yanchor': 'top'
        },
        width=800,
        height=800,
        xaxis_title="Features",
        yaxis_title="Features",
        showlegend=False
    )

    st.plotly_chart(fig, use_container_width=True)

    # Add explanation
    st.subheader("Understanding the Visualization")
    st.write("""
    - **Darker colors** indicate stronger interactions between features
    - **Diagonal** values are always 1.0 (a feature's interaction with itself)
    - **Symmetric** matrix: the interaction between Feature A and Feature B is the same as B and A
    - Use the threshold slider to focus on stronger interactions
    """)

    # Display raw data
    with st.expander("View Raw Data"):
        st.json(data)
