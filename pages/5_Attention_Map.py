import streamlit as st
import plotly.graph_objects as go
from utils.data_validation import validate_attention_map_data, load_json_data

st.set_page_config(page_title="Attention Map", page_icon="🔎")

st.title("Attention Map")
st.markdown("Visualize how a transformer model allocates attention between tokens in an input sequence.")

# Sample data with different content from display
sample_data = {
    "tokens": ["The", "quick", "brown", "fox", "jumps"],
    "attentionMaps": [
        {
            "layerIndex": 0,
            "heads": [
                {
                    "headIndex": 0,
                    "matrix": [
                        [0.80, 0.05, 0.05, 0.05, 0.05],
                        [0.10, 0.70, 0.10, 0.05, 0.05],
                        [0.05, 0.15, 0.60, 0.15, 0.05],
                        [0.05, 0.05, 0.10, 0.70, 0.10],
                        [0.05, 0.05, 0.05, 0.15, 0.70]
                    ]
                },
                {
                    "headIndex": 1,
                    "matrix": [
                        [0.60, 0.20, 0.10, 0.05, 0.05],
                        [0.05, 0.65, 0.20, 0.05, 0.05],
                        [0.05, 0.10, 0.70, 0.10, 0.05],
                        [0.05, 0.05, 0.15, 0.65, 0.10],
                        [0.05, 0.05, 0.05, 0.20, 0.65]
                    ]
                }
            ]
        },
        {
            "layerIndex": 1,
            "heads": [
                {
                    "headIndex": 0,
                    "matrix": [
                        [0.75, 0.10, 0.05, 0.05, 0.05],
                        [0.10, 0.65, 0.15, 0.05, 0.05],
                        [0.05, 0.15, 0.65, 0.10, 0.05],
                        [0.05, 0.05, 0.15, 0.65, 0.10],
                        [0.05, 0.05, 0.05, 0.15, 0.70]
                    ]
                }
            ]
        }
    ]
}

# Data input section
st.subheader("Data Input")
data_source = st.radio("Choose data source:", ["Use sample data", "Input custom data"])

if data_source == "Use sample data":
    data = sample_data
else:
    json_input = st.text_area("Enter your JSON data:", height=200,
                             help="Provide attention map data in JSON format with tokens and attention matrices.")
    if json_input:
        loaded_data = load_json_data(json_input)
        if isinstance(loaded_data, tuple):
            st.error(loaded_data[1])
            st.stop()
        valid, message = validate_attention_map_data(loaded_data)
        if not valid:
            st.error(message)
            st.stop()
        data = loaded_data
    else:
        data = None

if data:
    # Layer and head selection
    st.subheader("Visualization Controls")
    col1, col2 = st.columns(2)
    
    with col1:
        layer_indices = [layer["layerIndex"] for layer in data["attentionMaps"]]
        selected_layer_idx = st.selectbox("Select Layer:", layer_indices)
        current_layer = next(l for l in data["attentionMaps"] if l["layerIndex"] == selected_layer_idx)
    
    with col2:
        head_indices = [head["headIndex"] for head in current_layer["heads"]]
        selected_head_idx = st.selectbox("Select Head:", head_indices)
        current_head = next(h for h in current_layer["heads"] if h["headIndex"] == selected_head_idx)

    # Visualization
    st.subheader(f"Attention Heatmap - Layer {selected_layer_idx}, Head {selected_head_idx}")
    
    # Create heatmap
    fig = go.Figure(data=go.Heatmap(
        z=current_head["matrix"],
        x=data["tokens"],
        y=data["tokens"],
        colorscale="Blues",
        hoverongaps=False,
        hovertemplate="Source: %{y}<br>Target: %{x}<br>Attention: %{z:.3f}<extra></extra>"
    ))

    # Update layout
    fig.update_layout(
        width=700,
        height=600,
        xaxis_title="Target Tokens",
        yaxis_title="Source Tokens",
        xaxis={'side': 'bottom'},
        title={
            'text': f"Attention Distribution",
            'y': 0.95,
            'x': 0.5,
            'xanchor': 'center',
            'yanchor': 'top'
        }
    )

    # Display the plot
    st.plotly_chart(fig, use_container_width=True)

    # Add explanation
    st.markdown("""
    ### How to Read the Heatmap
    - Each cell shows the attention score from a source token (y-axis) to a target token (x-axis)
    - Darker colors indicate higher attention scores
    - Hover over cells to see exact attention values
    - Use the layer and head selectors above to explore different attention patterns
    """)

    # Display raw data
    with st.expander("View Raw Data"):
        st.json(data)
