import pytest
from streamlit.testing.v1 import AppTest
import sys
import json
from pathlib import Path

# Add the project root to the Python path
project_root = str(Path(__file__).parent.parent)
sys.path.append(project_root)

def test_initial_state():
    """Test the initial state of the application."""
    at = AppTest.from_file("pages/12_Neural_Network_Topology.py")
    at.run()
    
    # Check that the basic UI elements are present
    assert at.sidebar
    
    # Test data source selection
    data_source = at.selectbox("Select data source:")
    assert data_source.value == "Sample Data"
    
    # Check that there are no error messages initially
    assert not at.error
    
    # Verify session state initialization
    assert 'clicked_node' not in at.session_state
    assert 'show_weights' in at.session_state
    assert at.session_state.show_weights is True
    
    # Verify visualization controls exist and have default values
    show_weights = at.sidebar.checkbox("Show connection weights")
    assert show_weights.value is True
    
    node_size = at.sidebar.slider("Node size")
    assert node_size.value == 20
    
    line_width = at.sidebar.slider("Connection line width")
    assert line_width.value == 2

def test_data_source_selection():
    """Test the data source selection functionality."""
    at = AppTest.from_file("pages/12_Neural_Network_Topology.py")
    at.run()
    
    # Get data source selector
    data_source = at.selectbox("Select data source:")
    
    # Test Sample Data selection
    data_source.set_value("Sample Data").run()
    assert not at.error
    
    # Test JSON input selection
    data_source.set_value("Paste JSON").run()
    json_input = at.text_area("Enter JSON data:")
    assert json_input.value == ""

def test_json_validation():
    """Test JSON input validation."""
    at = AppTest.from_file("pages/12_Neural_Network_Topology.py")
    at.run()
    
    # Select JSON input mode
    data_source = at.selectbox("Select data source:")
    data_source.set_value("Paste JSON").run()
    
    # Get JSON input field
    json_input = at.text_area("Enter JSON data:")
    
    # Test invalid JSON format
    invalid_json = "{ invalid json }"
    json_input.input(invalid_json).run()
    assert any("Invalid JSON" in str(err) for err in at.error)
    
    # Test valid JSON but invalid structure
    invalid_structure = json.dumps({"invalid": "structure"})
    json_input.input(invalid_structure).run()
    assert any("must contain" in str(err) for err in at.error)
    
    # Test valid JSON with proper structure
    valid_json = json.dumps({
        "layers": [
            {
                "layerIndex": 0,
                "layerType": "input",
                "nodes": [{"id": "in_1"}]
            },
            {
                "layerIndex": 1,
                "layerType": "output",
                "nodes": [{"id": "out_1"}]
            }
        ],
        "connections": [
            {"source": "in_1", "target": "out_1", "weight": 1.0}
        ]
    })
    json_input.input(valid_json).run()
    assert not at.error
    
    # Test valid JSON with proper structure
    valid_json = json.dumps({
        "layers": [
            {
                "layerIndex": 0,
                "layerType": "input",
                "nodes": [{"id": "in_1"}]
            },
            {
                "layerIndex": 1,
                "layerType": "output",
                "nodes": [{"id": "out_1"}]
            }
        ],
        "connections": [
            {"source": "in_1", "target": "out_1", "weight": 1.0}
        ]
    })
    at.text_area(label="Enter JSON data:", key="json_input").input(valid_json).run()
    assert not at.error
    
    # Test valid minimal network
    valid_json = json.dumps({
        "layers": [
            {
                "layerIndex": 0,
                "layerType": "input",
                "nodes": [{"id": "in_1"}]
            },
            {
                "layerIndex": 1,
                "layerType": "output",
                "nodes": [{"id": "out_1"}]
            }
        ],
        "connections": [
            {"source": "in_1", "target": "out_1", "weight": 1.0}
        ]
    })
    at.text_area(label="Enter JSON data:").input(valid_json).run()
    assert not at.error

def test_node_selection_state():
    """Test node selection state management."""
    at = AppTest.from_file("pages/12_Neural_Network_Topology.py")
    at.run()
    
    # Initially no node should be selected
    assert 'clicked_node' not in at.session_state
    
    # Simulate node selection by setting session state
    at.session_state['clicked_node'] = 'in_1'
    at.run()
    
    # Clear selection using the button
    at.button(label="Clear Selection").click()
    assert 'clicked_node' not in at.session_state

def test_sidebar_controls():
    """Test sidebar control initialization and updates."""
    at = AppTest.from_file("pages/12_Neural_Network_Topology.py")
    at.run()
    
    # Get sidebar controls
    show_weights = at.sidebar.checkbox("Show connection weights")
    node_size = at.sidebar.slider("Node size")
    line_width = at.sidebar.slider("Connection line width")
    
    # Check default values
    assert show_weights.value is True
    assert node_size.value == 20
    assert line_width.value == 2
    
    # Test checkbox toggle
    show_weights.set_value(False).run()
    assert not at.session_state.show_weights
    
    # Test slider value updates
    node_size.set_value(30).run()
    assert at.session_state.node_size == 30
    
    line_width.set_value(3).run()
    assert at.session_state.line_width == 3
