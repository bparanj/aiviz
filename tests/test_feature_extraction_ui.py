import pytest
from pathlib import Path
import sys
import json

# Add the project root to the Python path
project_root = str(Path(__file__).parent.parent)
if project_root not in sys.path:
    sys.path.append(project_root)

import streamlit as st
from pages.page14_Feature_Extraction import (
    create_sankey_diagram,
    load_sample_data,
    validate_feature_extraction_data
)

def test_sample_data_visualization():
    """Test that sample data is visualized correctly."""
    # Load sample data
    data = load_sample_data()
    
    # Validate data structure
    is_valid, _ = validate_feature_extraction_data(data)
    assert is_valid, "Sample data should be valid"
    
    # Create visualization
    fig = create_sankey_diagram(data)
    assert fig is not None
    assert hasattr(fig, "data")
    assert fig.data[0].type == "sankey"
    
    # Verify nodes and links
    assert len(fig.data[0].node.label) == len(data["nodes"])
    assert len(fig.data[0].link.value) == len(data["links"])
    
    # Verify node colors
    assert all(isinstance(color, str) for color in fig.data[0].node.color)

def test_hover_tooltips():
    """Test that hover tooltips contain required information."""
    data = load_sample_data()
    fig = create_sankey_diagram(data)
    
    # Check node hover template contains required information
    assert "label" in fig.data[0].node.hovertemplate
    assert "Description" in fig.data[0].node.hovertemplate
    
    # Check link hover template contains required information
    assert "From:" in fig.data[0].link.hovertemplate
    assert "To:" in fig.data[0].link.hovertemplate
    assert "Value:" in fig.data[0].link.hovertemplate
    assert "Description:" in fig.data[0].link.hovertemplate

def test_path_highlighting():
    """Test that clicking a node highlights related paths."""
    data = load_sample_data()
    
    # Test highlighting first node
    fig = create_sankey_diagram(data, highlight_node=0)
    assert fig.data[0].node.color[0] == "#FFD700"  # Highlighted color
    
    # Test highlighting middle node
    mid_node = len(data["nodes"]) // 2
    fig = create_sankey_diagram(data, highlight_node=mid_node)
    assert fig.data[0].node.color[mid_node] == "#FFD700"

def test_data_transformation_visualization():
    """Test that data transformation flow is visualized correctly."""
    data = load_sample_data()
    fig = create_sankey_diagram(data)
    
    # Verify link values represent data flow
    link_values = fig.data[0].link.value
    assert all(isinstance(val, (int, float)) for val in link_values)
    assert all(val >= 0 for val in link_values)
    
    # Verify node connections
    node_labels = fig.data[0].node.label
    assert "Raw Data" in node_labels
    assert any("Features" in label for label in node_labels)

def test_feature_importance_visualization():
    """Test that feature importance is reflected in visualization."""
    data = load_sample_data()
    fig = create_sankey_diagram(data)
    
    # Verify link widths correspond to values
    link_values = fig.data[0].link.value
    assert len(set(link_values)) > 1, "Should show different importance levels"
    
    # Check that link colors or widths reflect values
    assert hasattr(fig.data[0].link, "color") or hasattr(fig.data[0].link, "width")

if __name__ == "__main__":
    pytest.main([__file__])
