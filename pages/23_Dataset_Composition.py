import streamlit as st
import plotly.graph_objects as go
import json
from pathlib import Path
import pandas as pd

def load_sample_data():
    """Load sample dataset composition data from JSON file."""
    sample_path = Path(__file__).parent.parent / "data" / "dataset_composition_sample.json"
    with open(sample_path, 'r') as f:
        return json.load(f)

def validate_data(data):
    """Validate the input data format."""
    if not isinstance(data, list):
        return False, "Data must be a list of class objects"
    
    if len(data) == 0:
        return False, "At least one class is required"
    
    for item in data:
        if not isinstance(item, dict):
            return False, "Each item must be a dictionary"
        
        if 'class' not in item or not isinstance(item['class'], str) or not item['class'].strip():
            return False, "Each item must have a non-empty class name"
        
        if 'count' not in item or not isinstance(item['count'], (int, float)) or item['count'] < 0:
            return False, "Each item must have a non-negative count"
    
    return True, "Valid data"

def create_bar_chart(data, sort_order=None):
    """Create an interactive bar chart showing class distribution."""
    df = pd.DataFrame(data)
    
    if sort_order == 'ascending':
        df = df.sort_values('count')
    elif sort_order == 'descending':
        df = df.sort_values('count', ascending=False)
    
    # Store sorted data in session state
    st.session_state['dataset_composition_sorted_data'] = df.to_dict('records')
    
    # Initialize tooltip data
    st.session_state['dataset_composition_tooltip'] = {
        'class': df['class'].iloc[0] if not df.empty else None,
        'count': df['count'].iloc[0] if not df.empty else None
    }
    
    # Initialize highlight state if not exists
    if 'dataset_composition_highlight' not in st.session_state:
        st.session_state['dataset_composition_highlight'] = None
    
    fig = go.Figure(data=[
        go.Bar(
            x=df['class'],
            y=df['count'],
            text=df['count'],
            textposition='auto',
            hovertemplate="Class: %{x}<br>Count: %{y}<extra></extra>",
            marker_color=['rgb(55, 83, 109)' if x != st.session_state['dataset_composition_highlight'] 
                         else 'rgb(255, 165, 0)' for x in df['class']],
            customdata=df['class']  # Store class names for click events
        )
    ])
    
    fig.update_layout(
        title="Dataset Composition by Class (Bar Chart)",
        xaxis_title="Class",
        yaxis_title="Count",
        showlegend=False,
        height=500,
        clickmode='event+select'
    )
    
    # Add click event handler
    fig.update_traces(
        hoverinfo='none',
        hovertemplate=None,
        hoverlabel=None,
        hovertext=None
    )
    
    # Store chart in session state
    st.session_state['dataset_composition_chart'] = fig
    
    return fig

def create_pie_chart(data):
    """Create an interactive pie chart showing class distribution."""
    df = pd.DataFrame(data)
    total = df['count'].sum()
    
    fig = go.Figure(data=[
        go.Pie(
            labels=df['class'],
            values=df['count'],
            hovertemplate="Class: %{label}<br>Count: %{value}<br>Percentage: %{percent}<extra></extra>",
            marker=dict(colors=['rgb(55, 83, 109)', 'rgb(26, 118, 255)', 
                              'rgb(178, 86, 209)', 'rgb(238, 130, 238)', 
                              'rgb(147, 112, 219)'])
        )
    ])
    
    fig.update_layout(
        title="Dataset Composition by Class (Pie Chart)",
        height=500,
        clickmode='event+select'
    )
    
    return fig

def main():
    # Initialize all session state variables
    session_state_keys = {
        "dataset_composition_text_input": "",
        "dataset_composition_highlight": None,
        "dataset_composition_tooltip": None,
        "dataset_composition_error": None,
        "dataset_composition_data": load_sample_data(),
        "dataset_composition_chart_type": "Bar Chart",
        "dataset_composition_sort_order": "Original",
        "dataset_composition_input_method": "Use sample data"
    }
    
    # Always reset these values on page load to ensure consistent state
    for key, default_value in session_state_keys.items():
        st.session_state[key] = default_value

    st.title("Dataset Composition by Class")
    st.write("""
    Visualize the distribution of samples across different classes in your dataset. 
    This helps identify class imbalance issues that might affect model training.
    """)
    
    # Initialize session state variables if they don't exist
    if 'dataset_composition_tooltip' not in st.session_state:
        st.session_state['dataset_composition_tooltip'] = {}
    if 'dataset_composition_highlight' not in st.session_state:
        st.session_state['dataset_composition_highlight'] = None
    if 'dataset_composition_error' not in st.session_state:
        st.session_state['dataset_composition_error'] = None
    
    # Data input method selection
    # Initialize input method in session state if not present
    if "dataset_composition_input_method" not in st.session_state:
        st.session_state["dataset_composition_input_method"] = "Use sample data"
    
    input_method = st.radio(
        "Select input method",
        ["Use sample data", "Upload JSON file", "Paste JSON data"],
        key="dataset_composition_input_method"
    )
    
    data = None
    
    if input_method == "Use sample data":
        data = load_sample_data()
        st.write("Using sample data:")
        st.write(data)
    
    elif input_method == "Upload JSON file":
        uploaded_file = st.file_uploader("Upload JSON file", type=['json'], key="dataset_composition_uploader")
        if uploaded_file:
            try:
                data = json.load(uploaded_file)
            except json.JSONDecodeError:
                st.error("Error: Invalid JSON file")
    
    else:  # Paste JSON data
        # Create text area with empty default value
        json_str = st.text_area(
            "Paste JSON data",
            value="",  # Always start empty
            key="dataset_composition_text_input",
            help="""Enter your JSON data here. Example format:
            [
                {"class": "Dog", "count": 50},
                {"class": "Cat", "count": 30}
            ]"""
        )
        
        # Handle text area changes
        if json_str:
            st.session_state["dataset_composition_text_input"] = json_str
            st.session_state["dataset_composition_error"] = None  # Clear previous errors
        if json_str:
            try:
                data = json.loads(json_str)
                # Clear any previous error
                st.session_state['dataset_composition_error'] = None
            except json.JSONDecodeError:
                st.session_state['dataset_composition_error'] = "Invalid JSON format"
                st.error("Error: Invalid JSON format")
                return
    
    if data:
        # Validate data
        is_valid, message = validate_data(data)
        if not is_valid:
            st.session_state['dataset_composition_error'] = message
            st.error(f"Invalid data: {message}")
            return
        
        # Clear any previous error
        st.session_state['dataset_composition_error'] = None
        
        
        # Chart type selection
        chart_type = st.radio(
            "Select chart type",
            ["Bar Chart", "Pie Chart"],
            key="dataset_composition_chart_type"
        )
        
        if chart_type == "Bar Chart":
            # Sorting options for bar chart
            sort_order = st.selectbox(
                "Sort order",
                ["Original", "Ascending", "Descending"],
                key="dataset_composition_sort_order"
            )
            
            sort_map = {
                "Original": None,
                "Ascending": "ascending",
                "Descending": "descending"
            }
            
            fig = create_bar_chart(data, sort_map[sort_order])
            
            # Display the chart first
            st.plotly_chart(
                fig,
                use_container_width=True,
                config={
                    'displayModeBar': True,
                    'modeBarButtonsToRemove': ['zoom', 'pan', 'select', 'lasso2d']
                }
            )
            
            # Add highlight buttons in a more compact layout
            st.write("Click to highlight a class:")
            button_cols = st.columns(min(4, len(data)))  # Max 4 buttons per row
            
            # Store current data in session state for reference
            st.session_state["dataset_composition_data"] = data
            
            for idx, item in enumerate(data):
                col_idx = idx % 4
                button_key = f"highlight_{item['class']}"
                
                if button_cols[col_idx].button(
                    item['class'],
                    key=button_key,
                    help=f"Click to highlight {item['class']}"
                ):
                    # Update session state before rerun
                    st.session_state['dataset_composition_highlight'] = item['class']
                    st.session_state['dataset_composition_tooltip'] = {
                        'class': item['class'],
                        'count': item['count']
                    }
                    st.rerun()
            
            # Add note about bar chart interaction
            st.info("Click on a class button to highlight its bar. Use the sort options to reorder the classes.")
        else:
            fig = create_pie_chart(data)
            # Add note about pie chart interaction
            st.info("Click on a slice to highlight it. Hover to see detailed information.")
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Display total samples and class distribution
        total_samples = sum(item['count'] for item in data)
        st.write(f"Total number of samples: {total_samples}")
        
        # Display class distribution details with percentages
        st.write("Class Distribution Details:")
        df = pd.DataFrame(data)
        df['percentage'] = (df['count'] / total_samples * 100).round(2)
        df['percentage'] = df['percentage'].apply(lambda x: f"{x}%")
        st.dataframe(df.style.format({'count': '{:,}'}))

if __name__ == "__main__":
    main()
