import sys
import os
import json
import pytest
from unittest.mock import MagicMock, patch
import streamlit as st
import plotly.graph_objects as go
from typing import Dict, List, Any, cast

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from pages.page18_Decision_Tree_Breakdown import create_tree_visualization, process_node, main

# Load test data
with open(os.path.join(os.path.dirname(__file__), '..', 'data', 'decision_tree_test_cases.json')) as f:
    TEST_CASES = json.load(f)['test_cases']

@pytest.fixture
def sample_tree_data():
    return TEST_CASES['valid']['basic_tree']

def test_process_node(sample_tree_data):
    """Test node processing for visualization."""
    x_coords, y_coords, node_info, node_ids, parent_ids, colors, edge_x, edge_y = process_node(sample_tree_data)
    
    # Check coordinates were generated
    assert len(x_coords) == 5  # Root + 2 intermediate + 2 leaf nodes
    assert len(y_coords) == 5  # Same number of nodes
    assert len(node_info) == 5  # Same number of nodes
    assert len(node_ids) == 5  # Same number of nodes
    assert len(colors) == 5  # Same number of nodes
    
    # Check root node information
    assert "Root" in node_info[0]
    assert "Age < 30" in node_info[0]
    assert "Samples: 100" in node_info[0]
    
    # Check color coding
    assert "#2ecc71" in colors  # Green for Approved
    assert "#e74c3c" in colors  # Red for Denied
    assert "#3498db" in colors  # Blue for others
    
    # Check edges were created
    assert len(edge_x) > 0
    assert len(edge_y) > 0
    
    # Check hierarchical structure
    assert node_ids[0] == "0"  # Root node
    assert any("0/0" in id for id in node_ids)  # First child
    assert any("0/1" in id for id in node_ids)  # Second child

def test_create_tree_visualization(sample_tree_data):
    """Test creation of Plotly figure for tree visualization."""
    fig = create_tree_visualization(sample_tree_data)
    
    # Check figure type
    assert isinstance(fig, go.Figure)
    
    # Check figure has data
    data = cast(List[Any], fig.data)
    assert len(data) > 0
    
    # Check layout configuration
    assert fig.layout.showlegend == False
    assert fig.layout.hovermode == 'closest'
    assert fig.layout.clickmode == 'event'

@patch('streamlit.file_uploader')
@patch('streamlit.text_area')
@patch('streamlit.plotly_chart')
def test_main_with_sample_data(mock_plotly_chart, mock_text_area, mock_file_uploader, sample_tree_data):
    """Test main function with sample data."""
    # Mock file uploader to return None
    mock_file_uploader.return_value = None
    
    # Mock text area to return None (no pasted JSON)
    mock_text_area.return_value = None
    
    # Run main function
    main()
    
    # Verify plotly chart was called with a figure
    assert mock_plotly_chart.called
    fig = mock_plotly_chart.call_args[0][0]
    assert isinstance(fig, go.Figure)

@patch('streamlit.file_uploader')
@patch('streamlit.text_area')
@patch('streamlit.error')
@patch('streamlit.radio')
def test_main_with_invalid_data(mock_error, mock_text_area, mock_file_uploader, mock_radio):
    """Test main function with invalid data."""
    mock_radio.return_value = "Paste JSON data"
    
    # Test with no data provided
    mock_text_area.return_value = None
    mock_file_uploader.return_value = None
    main()
    assert mock_error.called
    assert "No data provided" in str(mock_error.call_args_list[-1])
    # Test with invalid JSON structure in text area
    invalid_data = {
        "name": "Invalid Node",
        "samples": -1,  # Invalid: negative samples
        # Missing required field: condition
        "children": [
            {
                "name": "Invalid Child",
                # Missing samples and condition
            }
        ]
    }
    mock_text_area.return_value = json.dumps(invalid_data)
    mock_file_uploader.return_value = None
    main()
    assert mock_error.called
    assert mock_error.call_count >= 3  # Missing condition, negative samples, invalid child
    
    # Test with invalid JSON syntax in text area
    mock_error.reset_mock()
    mock_text_area.return_value = '{"invalid": json syntax'
    main()
    assert 'Invalid JSON' in str(mock_error.call_args_list[-1])
    
    # Test with invalid file upload
    mock_error.reset_mock()
    mock_text_area.return_value = None
    class MockFile:
        def read(self):
            return b'{"name": "Test", "samples": "not a number"}'  # Invalid samples type
    mock_file_uploader.return_value = MockFile()
    main()
    assert mock_error.called
    assert any('must be a number' in str(call) for call in mock_error.call_args_list)

@patch('streamlit.file_uploader')
@patch('streamlit.text_area')
@patch('streamlit.plotly_chart')
def test_visualization_interactivity(mock_plotly_chart, mock_text_area, mock_file_uploader, sample_tree_data):
    """Test interactive features of the visualization including hover, click, and path highlighting."""
    mock_file_uploader.return_value = None
    mock_text_area.return_value = json.dumps(sample_tree_data)
    
    # Run main function
    main()
    
    # Verify plotly chart was called
    assert mock_plotly_chart.called
    fig = mock_plotly_chart.call_args[0][0]
    
    # Check node trace (second trace) hover template
    assert len(fig.data) >= 2
    node_trace = fig.data[1]  # Node trace is second
    assert node_trace.hovertemplate is not None
    assert 'name' in node_trace.hovertemplate
    assert 'condition' in node_trace.hovertemplate
    assert 'samples' in node_trace.hovertemplate
    
    # Check interactive features
    assert fig.layout.clickmode == 'event'  # For node selection
    assert fig.layout.updatemenus is not None  # For expand/collapse
    
    # Check expand/collapse buttons
    buttons = []
    for menu in fig.layout.updatemenus:
        if hasattr(menu, 'buttons'):
            buttons.extend(menu.buttons)
    
    # Verify expand/collapse buttons exist
    expand_button = next((button for button in buttons if 'Expand All' in button.label), None)
    collapse_button = next((button for button in buttons if 'Collapse All' in button.label), None)
    clear_button = next((button for button in buttons if 'Clear Highlight' in button.label), None)
    
    assert expand_button is not None, "Expand All button not found"
    assert collapse_button is not None, "Collapse All button not found"
    assert clear_button is not None, "Clear Highlight button not found"
    
    # Verify button functionality
    assert expand_button.args[0].get('yaxis.range') is not None, "Expand button should set y-axis range"
    assert collapse_button.args[0].get('yaxis.range') == [0, 1], "Collapse button should show only root level"
    
    # Check path highlighting trace exists
    highlight_trace = next((trace for trace in fig.data if trace.name == 'highlighted_path'), None)
    assert highlight_trace is not None
    assert highlight_trace.line.color == '#2ecc71'  # Green highlight
    assert not highlight_trace.visible  # Hidden by default
    
    # Check color coding and hover information
    node_colors = node_trace.marker.color
    assert '#2ecc71' in node_colors  # Green for Approved
    assert '#e74c3c' in node_colors  # Red for Denied
    assert '#3498db' in node_colors  # Blue for others
    
    # Verify hover information
    hover_template = node_trace.hovertemplate
    assert 'name' in hover_template
    assert 'condition' in hover_template
    assert 'samples' in hover_template
    
    # Check path highlighting functionality
    highlight_trace = next((trace for trace in fig.data if trace.name == 'highlighted_path'), None)
    assert highlight_trace is not None
    assert not highlight_trace.visible  # Hidden by default
    
    # Verify node customdata for click handling
    node_customdata = node_trace.customdata
    assert all('id' in data for data in node_customdata)
    assert all('parent' in data for data in node_customdata)
    assert all('type' in data for data in node_customdata)
    assert all(data['type'] == 'node' for data in node_customdata)

if __name__ == '__main__':
    pytest.main([__file__])
