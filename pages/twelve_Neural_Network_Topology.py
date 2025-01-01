import streamlit as st
import json
import plotly.graph_objects as go
import networkx as nx
from pathlib import Path
import sys

# Add the project root to the Python path
project_root = str(Path(__file__).parent.parent)
if project_root not in sys.path:
    sys.path.append(project_root)

from utils.data_validation import validate_json_structure

def load_sample_data():
    """Load sample neural network topology data."""
    sample_data_path = Path(project_root) / "data" / "neural_network_topology_sample.json"
    with open(sample_data_path, 'r') as f:
        return json.load(f)

def validate_neural_network_data(data):
    """Validate the neural network topology data structure."""
    required_fields = {
        "layers": list,
        "connections": list
    }
    
    if not validate_json_structure(data, required_fields):
        return False, "Data must contain 'layers' and 'connections' arrays"
    
    # Validate layers
    layer_ids = set()
    for layer in data["layers"]:
        if not isinstance(layer.get("layerIndex"), (int, float)):
            return False, "Each layer must have a numeric layerIndex"
        
        if not isinstance(layer.get("nodes"), list):
            return False, "Each layer must have a nodes array"
            
        for node in layer["nodes"]:
            if "id" not in node:
                return False, "Each node must have an id"
            if node["id"] in layer_ids:
                return False, f"Duplicate node id found: {node['id']}"
            layer_ids.add(node["id"])
    
    # Validate connections
    for conn in data["connections"]:
        if "source" not in conn or "target" not in conn:
            return False, "Each connection must have source and target"
        if conn["source"] not in layer_ids:
            return False, f"Invalid source node id: {conn['source']}"
        if conn["target"] not in layer_ids:
            return False, f"Invalid target node id: {conn['target']}"
        if "weight" in conn and not isinstance(conn["weight"], (int, float)):
            return False, "Connection weight must be numeric"
    
    return True, "Data validation successful"

def main():
    st.title("12. Neural Network Topology")
    
    st.markdown("""
    This visualization shows the structure of a neural network, including its layers and connections.
    The visualization uses multiple visual encodings to represent the network structure:
    - Nodes arranged in layers from input to output
    - Connections between nodes showing the flow of data
    - Line thickness/color representing connection weights
    
    Click on nodes to highlight their connections and see the flow of data through the network.
    """)
    
    # Data source selection
    data_source = st.radio(
        "Select data source:",
        ["Sample Data", "Upload JSON", "Paste JSON"]
    )
    
    try:
        if data_source == "Sample Data":
            data = load_sample_data()
        elif data_source == "Upload JSON":
            uploaded_file = st.file_uploader("Upload a JSON file", type="json")
            if uploaded_file:
                data = json.load(uploaded_file)
            else:
                st.info("Please upload a JSON file")
                return
        else:  # Paste JSON
            json_str = st.text_area("Paste your JSON data here")
            if json_str:
                data = json.loads(json_str)
            else:
                st.info("Please paste your JSON data")
                return
        
        # Validate data
        is_valid, message = validate_neural_network_data(data)
        if not is_valid:
            st.error(f"Invalid data: {message}")
            return
            
        # TODO: Implement visualization
        st.info("Neural network visualization will be implemented in the next step")
        
    except Exception as e:
        st.error(f"Error processing data: {str(e)}")

if __name__ == "__main__":
    main()
