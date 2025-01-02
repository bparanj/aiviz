import streamlit as st
import json
import plotly.graph_objects as go
from pathlib import Path
import pandas as pd

def load_sample_data():
    sample_path = Path(__file__).parent.parent / "data" / "model_architecture_sample.json"
    with open(sample_path, 'r') as f:
        return json.load(f)

def validate_node(node, path="root"):
    """Validate a single node in the model architecture tree."""
    if not isinstance(node, dict):
        raise ValueError(f"Node at {path} must be a dictionary")
    
    if "name" not in node:
        raise ValueError(f"Node at {path} must have a 'name' field")
    
    if not isinstance(node["name"], str) or not node["name"].strip():
        raise ValueError(f"Node at {path} must have a non-empty string name")
    
    if "type" in node and (not isinstance(node["type"], str) or not node["type"].strip()):
        raise ValueError(f"Node at {path} has invalid type - must be a non-empty string if present")
    
    if "children" not in node:
        raise ValueError(f"Node at {path} must have a 'children' field (can be empty list)")
    
    if not isinstance(node["children"], list):
        raise ValueError(f"Node at {path} must have 'children' as a list")
    
    for i, child in enumerate(node["children"]):
        validate_node(child, f"{path}.{node['name']}.child{i}")

def process_data_for_tree(node, parent="", level=0):
    """Process the hierarchical data into a format suitable for Plotly's treemap."""
    result = {
        "ids": [],
        "labels": [],
        "parents": [],
        "text": [],
        "level": []
    }
    
    # Add current node
    node_id = f"{parent}_{node['name']}" if parent else node['name']
    result["ids"].append(node_id)
    result["labels"].append(node["name"])
    result["parents"].append(parent)
    result["text"].append(f"Type: {node.get('type', 'N/A')}")
    result["level"].append(level)
    
    # Process children
    for child in node["children"]:
        child_data = process_data_for_tree(child, node_id, level + 1)
        for key in result:
            result[key].extend(child_data[key])
    
    return result

def create_tree_chart(data):
    """Create an interactive tree chart using Plotly."""
    tree_data = process_data_for_tree(data)
    
    # Create color scale based on levels
    max_level = max(tree_data["level"])
    colors = [f"hsl({int(180 + (180 * i/max_level))}, 70%, 50%)" for i in range(max_level + 1)]
    
    fig = go.Figure(go.Treemap(
        ids=tree_data["ids"],
        labels=tree_data["labels"],
        parents=tree_data["parents"],
        text=tree_data["text"],
        hovertemplate="<b>%{label}</b><br>%{text}<br>Parent: %{parent}<extra></extra>",
        marker=dict(
            colors=[colors[level] for level in tree_data["level"]],
            colorscale=None,  # Using custom colors
            showscale=False
        ),
        root=dict(color="lightgrey")
    ))
    
    fig.update_layout(
        title="Model Architecture Visualization",
        width=800,
        height=600,
        margin=dict(t=50, l=25, r=25, b=25)
    )
    
    return fig

def main():
    st.title("Model Architecture Visualization")
    
    st.write("""
    Visualize the hierarchical structure of machine learning models, showing layers, 
    components, and their relationships. This visualization helps understand how different 
    parts of a model fit together.
    """)
    
    # Data input selection
    data_input = st.radio(
        "Select input method:",
        ["Use Sample Data", "Upload JSON File", "Paste JSON"]
    )
    
    try:
        if data_input == "Use Sample Data":
            data = load_sample_data()
            st.success("Sample data loaded successfully!")
            
        elif data_input == "Upload JSON File":
            uploaded_file = st.file_uploader("Upload JSON file", type=['json'])
            if uploaded_file:
                data = json.load(uploaded_file)
                st.success("File uploaded successfully!")
            else:
                st.info("Please upload a JSON file")
                return
                
        else:  # Paste JSON
            json_str = st.text_area(
                "Paste your JSON data here",
                height=300,
                help="Paste your model architecture JSON data here"
            )
            if json_str:
                data = json.loads(json_str)
                st.success("JSON parsed successfully!")
            else:
                st.info("Please paste your JSON data")
                return
        
        # Validate data
        validate_node(data)
        
        # Display raw data in expandable section
        with st.expander("View Raw Data"):
            st.json(data)
        
        # Create and display visualization
        fig = create_tree_chart(data)
        st.plotly_chart(fig, use_container_width=True)
        
        # Add instructions
        st.markdown("""
        ### Instructions
        - Click on a node to zoom in
        - Double click to zoom out
        - Hover over nodes to see details
        - Use the reset button to return to the original view
        """)
        
    except json.JSONDecodeError:
        st.error("Invalid JSON format. Please check your input.")
    except ValueError as e:
        st.error(f"Validation Error: {str(e)}")
    except Exception as e:
        st.error(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    main()
