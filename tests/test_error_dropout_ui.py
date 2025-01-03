import pytest
from unittest.mock import MagicMock, patch
import json
from typing import Dict, List, Union, Optional, cast
import plotly.graph_objects as go
from plotly.graph_objs import Figure, Sankey
import streamlit as st
import pandas as pd
import numpy as np
import sys
from pathlib import Path

# Add the project root to Python path
project_root = str(Path(__file__).parent.parent)
if project_root not in sys.path:
    sys.path.append(project_root)

from pages.page17_Error_Dropout_Tracking import create_sankey_diagram, calculate_statistics, main

def validate_sankey_diagram(fig: Figure, sample_data: Dict) -> None:
    """Helper function to validate Sankey diagram properties.
    
    Validates:
    - Node ordering and presence
    - Link values and proportions
    - Hover template content
    - Link thickness proportionality
    """
    # Verify figure type and data
    assert isinstance(fig, Figure), "Result should be a Plotly Figure"
    assert hasattr(fig, 'data'), "Figure should have data attribute"
    assert isinstance(fig.data, (list, tuple)), "Figure data should be a sequence"
    assert len(fig.data) > 0, "Figure should have at least one trace"
    
    # Get and validate the Sankey trace
    sankey_trace = cast(Sankey, fig.data[0])
    assert isinstance(sankey_trace, go.Sankey), "First trace should be a Sankey diagram"
    
    # Access node data safely
    node = cast(Dict, getattr(sankey_trace, 'node', {}))
    assert isinstance(node, dict), "Node data should be a dictionary"
    node_labels = cast(List[str], node.get('label', []))
    assert len(node_labels) == len(sample_data["nodes"]), "Should have correct number of node labels"
    
    # Verify node ordering (left-to-right)
    assert "Raw Data" in node_labels, "Should include 'Raw Data' node"
    assert "Discarded" in node_labels, "Should include 'Discarded' node"
    raw_data_idx = node_labels.index("Raw Data")
    discarded_idx = node_labels.index("Discarded")
    assert raw_data_idx < discarded_idx, "Raw Data should appear before Discarded node"
    
    # Access link data safely
    link = cast(Dict, getattr(sankey_trace, 'link', {}))
    assert isinstance(link, dict), "Link data should be a dictionary"
    sources = cast(List[int], link.get('source', []))
    targets = cast(List[int], link.get('target', []))
    values = cast(List[Union[int, float]], link.get('value', []))
    
    # Verify link counts
    assert len(sources) == len(sample_data["links"]), "Should have correct number of link sources"
    assert len(targets) == len(sample_data["links"]), "Should have correct number of link targets"
    assert len(values) == len(sample_data["links"]), "Should have correct number of link values"
    
    # Verify link values and thickness proportionality
    assert all(isinstance(v, (int, float)) for v in values), "Link values should be numeric"
    assert all(v >= 0 for v in values), "Link values should be non-negative"
    
    # Verify that link thickness is proportional to sample count
    if len(values) >= 2:
        ratio_1 = values[0] / values[1]  # Ratio of first two link values
        width_1 = link.get('width', [])[0] / link.get('width', [])[1]  # Ratio of their widths
        assert abs(ratio_1 - width_1) < 0.1, "Link thickness should be proportional to sample count"
    
    # Verify dropout paths
    has_dropout = False
    for i, target in enumerate(targets):
        if node_labels[target] == "Discarded":
            has_dropout = True
            assert values[i] > 0, "Dropout path should have positive sample count"
    assert has_dropout, "Should have at least one dropout path"
    
    # Verify hover template
    hover_template = cast(str, link.get('hovertemplate', ''))
    assert isinstance(hover_template, str), "Hover template should be a string"
    assert "%{source.label}" in hover_template, "Should show source node in hover"
    assert "%{target.label}" in hover_template, "Should show target node in hover"
    assert "%{value}" in hover_template, "Should show sample count in hover"

@pytest.fixture
def sample_data():
    """Load sample data for testing."""
    with open("data/error_dropout_sample.json", "r") as f:
        return json.load(f)

def test_sankey_diagram_creation(sample_data):
    """Test that Sankey diagram is created with correct properties."""
    fig = create_sankey_diagram(sample_data)
    validate_sankey_diagram(fig, sample_data)

def test_statistics_calculation(sample_data):
    """Test that statistics are calculated correctly."""
    stats_df = calculate_statistics(sample_data)
    
    # Verify DataFrame structure
    assert isinstance(stats_df, pd.DataFrame)
    expected_columns = ["Stage", "Incoming Samples", "Outgoing Samples", 
                       "Dropped Samples", "Drop Rate (%)"]
    assert all(col in stats_df.columns for col in expected_columns)
    
    # Verify calculations for first stage
    first_stage = stats_df.iloc[0]
    assert first_stage["Stage"] == "Raw Data"
    assert first_stage["Incoming Samples"] == 10000
    assert first_stage["Outgoing Samples"] == 8500
    assert first_stage["Dropped Samples"] == 1500
    assert first_stage["Drop Rate (%)"] == pytest.approx(15.0)

@pytest.fixture
def mock_streamlit():
    """Mock Streamlit components."""
    with patch("streamlit.title") as mock_title, \
         patch("streamlit.write") as mock_write, \
         patch("streamlit.subheader") as mock_subheader, \
         patch("streamlit.radio") as mock_radio, \
         patch("streamlit.checkbox") as mock_checkbox, \
         patch("streamlit.plotly_chart") as mock_plotly, \
         patch("streamlit.dataframe") as mock_df, \
         patch("streamlit.columns") as mock_cols, \
         patch("streamlit.metric") as mock_metric:
        
        mock_radio.return_value = "Use sample data"
        mock_checkbox.return_value = True
        mock_cols.return_value = [MagicMock(), MagicMock()]
        
        yield {
            "title": mock_title,
            "write": mock_write,
            "subheader": mock_subheader,
            "radio": mock_radio,
            "checkbox": mock_checkbox,
            "plotly_chart": mock_plotly,
            "dataframe": mock_df,
            "columns": mock_cols,
            "metric": mock_metric
        }

def test_main_page_layout(mock_streamlit):
    """Test the main page layout and components."""
    main()
    
    # Verify page title and description
    mock_streamlit["title"].assert_called_once_with("Error/Dropout Tracking")
    assert mock_streamlit["write"].call_count >= 1
    
    # Verify input controls
    mock_streamlit["radio"].assert_called_once()
    mock_streamlit["checkbox"].assert_called_once_with(
        "Show dropout paths", value=True, help=pytest.approx(str)
    )
    
    # Verify visualization components
    mock_streamlit["plotly_chart"].assert_called_once()
    mock_streamlit["dataframe"].assert_called_once()
    assert mock_streamlit["metric"].call_count == 2

def test_data_input_handling(mock_streamlit, sample_data):
    """Test different data input methods."""
    # Test sample data
    mock_streamlit["radio"].return_value = "Use sample data"
    main()
    mock_streamlit["plotly_chart"].assert_called_once()
    fig = cast(Figure, mock_streamlit["plotly_chart"].call_args[0][0])
    validate_sankey_diagram(fig, sample_data)
    
    # Test file upload
    mock_streamlit["radio"].return_value = "Upload JSON file"
    with patch("streamlit.file_uploader") as mock_uploader:
        # Test successful file upload
        mock_uploader.return_value = MagicMock()
        mock_uploader.return_value.read.return_value = json.dumps(sample_data).encode()
        main()
        mock_uploader.assert_called_with("Upload JSON file", type="json")
        fig = cast(Figure, mock_streamlit["plotly_chart"].call_args[0][0])
        validate_sankey_diagram(fig, sample_data)
        
        # Test failed upload
        mock_uploader.return_value = None
        main()
        mock_streamlit["error"].assert_called_with("Please upload a JSON file")
    
    # Test JSON paste
    mock_streamlit["radio"].return_value = "Paste JSON data"
    with patch("streamlit.text_area") as mock_text_area:
        # Test successful JSON paste
        mock_text_area.return_value = json.dumps(sample_data)
        main()
        mock_text_area.assert_called_with("Paste JSON data here")
        fig = cast(Figure, mock_streamlit["plotly_chart"].call_args[0][0])
        validate_sankey_diagram(fig, sample_data)
        
        # Test empty paste
        mock_text_area.return_value = ""
        main()
        mock_streamlit["error"].assert_called_with("Please enter JSON data")

def test_dropout_path_filtering(sample_data, mock_streamlit):
    """Test the dropout path filtering functionality."""
    # Test with dropouts shown
    mock_streamlit["checkbox"].return_value = True
    main()
    fig_with_dropouts = cast(Figure, mock_streamlit["plotly_chart"].call_args[0][0])
    
    # Validate full diagram with dropouts
    sankey_with_dropouts = cast(Sankey, fig_with_dropouts.data[0])
    link_data = cast(Dict, getattr(sankey_with_dropouts, 'link', {}))
    sources = cast(List[int], link_data.get('source', []))
    assert len(sources) == len(sample_data["links"]), "Should show all links with dropouts"
    
    # Test with dropouts hidden
    mock_streamlit["checkbox"].return_value = False
    main()
    fig_without_dropouts = cast(Figure, mock_streamlit["plotly_chart"].call_args[0][0])
    
    # Validate filtered diagram without dropouts
    sankey_without_dropouts = cast(Sankey, fig_without_dropouts.data[0])
    filtered_link_data = cast(Dict, getattr(sankey_without_dropouts, 'link', {}))
    filtered_sources = cast(List[int], filtered_link_data.get('source', []))
    assert len(filtered_sources) < len(sample_data["links"]), "Should hide dropout paths"
    
    # Verify that only non-dropout paths remain
    node_data = cast(Dict, getattr(sankey_without_dropouts, 'node', {}))
    node_labels = cast(List[str], node_data.get('label', []))
    targets = cast(List[int], filtered_link_data.get('target', []))
    for target in targets:
        assert node_labels[target] != "Discarded", "Should not have links to Discarded node when filtered"

def test_error_handling(mock_streamlit):
    """Test error handling for invalid inputs."""
    # Test invalid JSON syntax
    mock_streamlit["radio"].return_value = "Paste JSON data"
    with patch("streamlit.text_area") as mock_text_area, \
         patch("streamlit.error") as mock_error:
        mock_text_area.return_value = "invalid json"
        main()
        mock_error.assert_called_once()
        assert "Invalid JSON" in str(mock_error.call_args[0][0])
    
    # Test missing required fields
    with patch("streamlit.text_area") as mock_text_area, \
         patch("streamlit.error") as mock_error:
        mock_text_area.return_value = '{"invalid": "format"}'
        main()
        mock_error.assert_called_once()
        assert "Missing required fields" in str(mock_error.call_args[0][0])
    
    # Test invalid node format
    with patch("streamlit.text_area") as mock_text_area, \
         patch("streamlit.error") as mock_error:
        mock_text_area.return_value = '{"nodes": [{"invalid": "node"}], "links": []}'
        main()
        mock_error.assert_called_once()
        assert "Invalid node format" in str(mock_error.call_args[0][0])
    
    # Test missing Discarded node
    with patch("streamlit.text_area") as mock_text_area, \
         patch("streamlit.error") as mock_error:
        mock_text_area.return_value = '''
        {
            "nodes": [
                {"id": 0, "name": "Raw Data"},
                {"id": 1, "name": "Processed"}
            ],
            "links": [
                {"source": 0, "target": 1, "value": 100}
            ]
        }
        '''
        main()
        mock_error.assert_called_once()
        assert "Missing Discarded node" in str(mock_error.call_args[0][0])
    
    # Test invalid link format
    with patch("streamlit.text_area") as mock_text_area, \
         patch("streamlit.error") as mock_error:
        mock_text_area.return_value = '''
        {
            "nodes": [
                {"id": 0, "name": "Raw Data"},
                {"id": 1, "name": "Discarded"}
            ],
            "links": [
                {"invalid": "link"}
            ]
        }
        '''
        main()
        mock_error.assert_called_once()
        assert "Invalid link format" in str(mock_error.call_args[0][0])
