import streamlit as st
import pytest
from unittest.mock import MagicMock, patch
import json
import plotly.graph_objects as go
from pages.nineteen_Hierarchical_Clustering import (
    create_cluster_visualization,
    process_node,
    main
)

def test_create_cluster_visualization_layout():
    """Test that the visualization has the correct layout properties."""
    data = {
        "name": "Root",
        "children": [
            {
                "name": "Child A",
                "children": [{"name": "Grandchild A1"}]
            },
            {
                "name": "Child B",
                "children": [{"name": "Grandchild B1"}]
            }
        ]
    }
    
    fig = create_cluster_visualization(data)
    
    # Check layout properties
    assert isinstance(fig, go.Figure)
    layout_dict = fig.to_dict()['layout']
    
    # Check title
    assert layout_dict['title']['text'] == 'Hierarchical Clustering Visualization'
    
    # Check general layout properties
    assert layout_dict['showlegend'] == False
    assert layout_dict['hovermode'] == 'closest'
    
    # Check axis properties
    assert layout_dict['xaxis']['title']['text'] == 'Cluster Level'
    assert layout_dict['xaxis']['showgrid'] == False
    assert layout_dict['yaxis']['showgrid'] == False
    
    # Check that we have both nodes and edges
    fig_dict = fig.to_dict()
    trace_types = [trace.get('mode', '') for trace in fig_dict['data']]
    assert any('markers' in mode for mode in trace_types), "No node markers found"
    assert any('lines' in mode for mode in trace_types), "No edges found"

def test_node_hover_information():
    """Test that nodes have correct hover information."""
    data = {
        "name": "Root",
        "children": [{"name": "Child"}]
    }
    
    fig = create_cluster_visualization(data)
    
    # Check hover text for nodes
    fig_dict = fig.to_dict()
    node_traces = [trace for trace in fig_dict['data'] if 'mode' in trace and 'markers' in trace['mode']]
    for trace in node_traces:
        assert trace['hoverinfo'] == 'text'
        assert all('Cluster:' in text for text in trace['hovertext'])

def test_color_coding():
    """Test that different levels have different colors."""
    data = {
        "name": "Root",
        "children": [
            {
                "name": "Level 1",
                "children": [{"name": "Level 2"}]
            }
        ]
    }
    
    fig = create_cluster_visualization(data)
    
    # Get colors from node traces
    fig_dict = fig.to_dict()
    colors = set()
    for trace in fig_dict['data']:
        if 'marker' in trace and 'color' in trace['marker']:
            colors.add(trace['marker']['color'])
    
    # Should have at least 2 different colors for different levels
    assert len(colors) >= 2, "Not enough color variation for different levels"

@pytest.mark.parametrize("input_method", ["Use sample data", "Upload JSON file", "Paste JSON data"])
def test_input_methods(input_method):
    """Test different input methods in the Streamlit interface."""
    with patch('streamlit.radio') as mock_radio:
        mock_radio.return_value = input_method
        
        if input_method == "Use sample data":
            with patch('pages.nineteen_Hierarchical_Clustering.load_sample_data') as mock_load:
                mock_load.return_value = {"name": "Root", "children": [{"name": "Child"}]}
                main()
                mock_load.assert_called_once()
        
        elif input_method == "Upload JSON file":
            with patch('streamlit.file_uploader') as mock_uploader:
                mock_file = MagicMock()
                mock_file.read.return_value = json.dumps({"name": "Root", "children": [{"name": "Child"}]}).encode()
                mock_uploader.return_value = mock_file
                main()
                mock_uploader.assert_called_once_with("Upload JSON file", type=['json'])
        
        else:  # Paste JSON data
            with patch('streamlit.text_area') as mock_text_area:
                mock_text_area.return_value = json.dumps({"name": "Root", "children": [{"name": "Child"}]})
                main()
                mock_text_area.assert_called_once()

def test_error_display():
    """Test that invalid data displays appropriate error messages."""
    with patch('streamlit.radio') as mock_radio, \
         patch('streamlit.text_area') as mock_text_area, \
         patch('streamlit.error') as mock_error:
        
        mock_radio.return_value = "Paste JSON data"
        mock_text_area.return_value = json.dumps({"name": "Root"})  # Invalid: root must have children
        
        main()
        
        # Check that error was displayed
        mock_error.assert_called()
        error_calls = [call.args[0] for call in mock_error.call_args_list]
        assert any("Root node must have children" in str(err) for err in error_calls)

def test_raw_data_display():
    """Test that raw data is displayed in expandable section."""
    test_data = {"name": "Root", "children": [{"name": "Child"}]}
    
    with patch('streamlit.radio') as mock_radio, \
         patch('pages.nineteen_Hierarchical_Clustering.load_sample_data') as mock_load, \
         patch('streamlit.expander') as mock_expander, \
         patch('streamlit.json') as mock_json:
        
        mock_radio.return_value = "Use sample data"
        mock_load.return_value = test_data
        
        main()
        
        mock_expander.assert_called_with("View Raw Data")
        mock_json.assert_called_with(test_data)
