import pytest
from streamlit.testing.v1 import AppTest
import sys
import json
from pathlib import Path

# Add the project root to the Python path
project_root = str(Path(__file__).parent.parent)
sys.path.append(project_root)

def test_node_hover():
    """Test node hover functionality."""
    at = AppTest.from_file("pages/12_Neural_Network_Topology.py")
    at.run()
    
    # Verify hover info is displayed in session state
    at.session_state.hovered_node = "in_1"
    at.run()
    
    # Check that hover info is displayed
    assert any("Node ID: in_1" in str(text) for text in at.info)
    
    # Clear hover
    at.session_state.hovered_node = None
    at.run()
    assert not any("Node ID:" in str(text) for text in at.info)

def test_node_click():
    """Test node click functionality."""
    at = AppTest.from_file("pages/12_Neural_Network_Topology.py")
    at.run()
    
    # Simulate node click
    at.session_state.clicked_node = "h1_1"
    at.run()
    
    # Check that node info is displayed
    assert any("Selected Node: h1_1" in str(text) for text in at.info)
    
    # Check that connected edges are highlighted
    assert "highlighted_edges" in at.session_state
    
    # Clear selection
    clear_button = at.button("Clear Selection")
    clear_button.click().run()
    assert "clicked_node" not in at.session_state
    assert "highlighted_edges" not in at.session_state

def test_weight_visualization():
    """Test weight visualization controls."""
    at = AppTest.from_file("pages/12_Neural_Network_Topology.py")
    at.run()
    
    # Get weight controls
    show_weights = at.sidebar.checkbox("Show connection weights")
    line_width = at.sidebar.slider("Connection line width")
    
    # Test weight visibility toggle
    assert show_weights.value is True
    show_weights.set_value(False).run()
    assert not at.session_state.show_weights
    
    # Test line width adjustment
    assert line_width.value == 2
    line_width.set_value(4).run()
    assert at.session_state.line_width == 4

def test_network_interaction():
    """Test combined network interaction features."""
    at = AppTest.from_file("pages/12_Neural_Network_Topology.py")
    at.run()
    
    # Test hover while node is selected
    at.session_state.clicked_node = "in_1"
    at.session_state.hovered_node = "h1_1"
    at.run()
    
    # Both hover and selection info should be visible
    assert any("Selected Node: in_1" in str(text) for text in at.info)
    assert any("Node ID: h1_1" in str(text) for text in at.info)
    
    # Clear hover and selection
    at.session_state.hovered_node = None
    at.button("Clear Selection").click().run()
    assert "clicked_node" not in at.session_state
    assert not any("Node ID:" in str(text) for text in at.info)
