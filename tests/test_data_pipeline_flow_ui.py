import pytest
from pathlib import Path
import sys
import os
import json
import streamlit as st
from unittest.mock import MagicMock, patch

# Add the project root to the Python path
project_root = str(Path(__file__).parent.parent)
if project_root not in sys.path:
    sys.path.append(project_root)

from pages.thirteen_Data_Pipeline_Flow import main, create_sankey_diagram, validate_pipeline_data

@pytest.fixture
def sample_data():
    """Load sample data for testing."""
    sample_data_path = Path(project_root) / "data" / "data_pipeline_flow_sample.json"
    with open(sample_data_path, "r") as f:
        return json.load(f)

def test_sankey_diagram_creation(sample_data):
    """Test that Sankey diagram is created correctly with sample data."""
    fig = create_sankey_diagram(sample_data)
    assert fig is not None
    assert hasattr(fig, "data")  # Plotly figures have data attribute
    assert len(fig.data) > 0
    assert fig.data[0].type == "sankey"  # Check diagram type
    # Verify nodes and links are present
    assert hasattr(fig.data[0], "node")
    assert hasattr(fig.data[0], "link")

@pytest.mark.parametrize("input_method", ["Sample Data", "Upload JSON", "Paste JSON"])
def test_input_method_selection(input_method):
    """Test different input methods for data."""
    with patch("streamlit.sidebar") as mock_sidebar:
        mock_radio = MagicMock(return_value=input_method)
        mock_uploader = MagicMock(return_value=None)
        mock_text_area = MagicMock(return_value=None)
        mock_sidebar.radio = mock_radio
        mock_sidebar.file_uploader = mock_uploader
        mock_sidebar.text_area = mock_text_area
        
        with patch("streamlit.plotly_chart") as mock_plot:
            with patch("streamlit.session_state", new_callable=dict) as mock_state:
                # Initialize session state
                mock_state["show_filtered"] = True
                mock_state["clicked_node"] = None
                
                # Mock sample data
                sample_data = {
                    "nodes": [
                        {"id": 0, "name": "Start"},
                        {"id": 1, "name": "Process"},
                        {"id": 2, "name": "End"}
                    ],
                    "links": [
                        {"source": 0, "target": 1, "value": 100},
                        {"source": 1, "target": 2, "value": 90}
                    ]
                }
                
                # Mock load_sample_data for Sample Data option
                with patch("pages.13_Data_Pipeline_Flow.load_sample_data", return_value=sample_data):
                    main()
                
                # Verify radio button was shown
                mock_radio.assert_called_with(
                    "Select data source:",
                    ["Sample Data", "Upload JSON", "Paste JSON"]
                )
                
                # Verify appropriate input method was displayed
                if input_method == "Upload JSON":
                    mock_uploader.assert_called_with("Upload a JSON file", type="json")
                elif input_method == "Paste JSON":
                    mock_text_area.assert_called_with("Paste your JSON data here")
                elif input_method == "Sample Data":
                    assert mock_plot.call_count > 0, "Plot should be created for sample data"

def test_pipeline_statistics_display(sample_data):
    """Test that pipeline statistics are displayed correctly."""
    with patch("streamlit.subheader") as mock_subheader:
        with patch("streamlit.columns") as mock_columns:
            with patch("streamlit.metric") as mock_metric:
                with patch("streamlit.session_state", new_callable=dict) as mock_state:
                    # Mock session state
                    mock_state["show_filtered"] = True
                    mock_state["clicked_node"] = None
                    
                    # Mock sidebar components
                    with patch("streamlit.sidebar") as mock_sidebar:
                        mock_radio = MagicMock(return_value="Sample Data")
                        mock_sidebar.radio = mock_radio
                        
                        # Mock columns
                        mock_col = MagicMock()
                        mock_columns.return_value = [mock_col, mock_col, mock_col]
                        
                        # Run the main function
                        with patch("pages.13_Data_Pipeline_Flow.load_sample_data", return_value=sample_data):
                            main()
                        
                        # Verify statistics section is shown
                        mock_subheader.assert_any_call("Pipeline Statistics")
                    
                    
                    # Verify metrics are displayed
                    metric_calls = mock_metric.call_args_list
                    metrics_shown = set()
                    for call in metric_calls:
                        label = call[0][0]
                        metrics_shown.add(label)
                    
                    required_metrics = {
                        "Total Input Records",
                        "Filtered Out Records",
                        "Final Output Records",
                        "Data Retention Rate"
                    }
                    assert required_metrics.issubset(metrics_shown)

def test_node_highlighting():
    """Test node highlighting functionality."""
    with patch("streamlit.session_state", new_callable=dict) as mock_session:
        # Simulate node click
        mock_session["clicked_node"] = 1
        
        # Create diagram with highlighting
        sample_data_path = Path(project_root) / "data" / "data_pipeline_flow_sample.json"
        with open(sample_data_path, "r") as f:
            data = json.load(f)
        
        fig = create_sankey_diagram(data)
        
        # Verify highlighting is applied
        assert hasattr(fig.data[0].node, "color")
        colors = fig.data[0].node.color
        assert any(isinstance(c, str) and c.startswith("#") for c in colors)

def test_hover_tooltips(sample_data):
    """Test that hover tooltips are configured correctly."""
    fig = create_sankey_diagram(sample_data)
    
    # Verify hover template is configured for nodes and links
    assert hasattr(fig.data[0].node, "hovertemplate")
    assert hasattr(fig.data[0].link, "hovertemplate")
    
    # Verify hover templates contain required information
    node_template = fig.data[0].node.hovertemplate
    link_template = fig.data[0].link.hovertemplate
    
    assert "Node:" in node_template
    assert "ID:" in node_template
    assert "From:" in link_template
    assert "To:" in link_template
    assert "Records:" in link_template

def test_validation_rules():
    """Test all validation rules for pipeline data."""
    # Test duplicate node IDs
    invalid_data = {
        "nodes": [
            {"id": 0, "name": "Start"},
            {"id": 0, "name": "End"}
        ],
        "links": []
    }
    with pytest.raises(ValueError) as exc_info:
        validate_pipeline_data(invalid_data)
    assert "unique" in str(exc_info.value).lower()
    
    # Test invalid node references
    invalid_data = {
        "nodes": [
            {"id": 0, "name": "Start"},
            {"id": 1, "name": "End"}
        ],
        "links": [
            {"source": 0, "target": 2, "value": 100}
        ]
    }
    with pytest.raises(ValueError) as exc_info:
        validate_pipeline_data(invalid_data)
    assert "valid node IDs" in str(exc_info.value)
    
    # Test negative values
    invalid_data = {
        "nodes": [
            {"id": 0, "name": "Start"},
            {"id": 1, "name": "End"}
        ],
        "links": [
            {"source": 0, "target": 1, "value": -10}
        ]
    }
    with pytest.raises(ValueError) as exc_info:
        validate_pipeline_data(invalid_data)
    assert "non-negative" in str(exc_info.value).lower()
    
    # Test minimum nodes requirement
    invalid_data = {
        "nodes": [
            {"id": 0, "name": "Start"}
        ],
        "links": []
    }
    with pytest.raises(ValueError) as exc_info:
        validate_pipeline_data(invalid_data)
    assert "2 nodes" in str(exc_info.value)

def test_custom_json_input():
    """Test custom JSON input functionality."""
    custom_data = {
        "nodes": [
            {"id": 0, "name": "Start"},
            {"id": 1, "name": "Process"},
            {"id": 2, "name": "End"}
        ],
        "links": [
            {"source": 0, "target": 1, "value": 100},
            {"source": 1, "target": 2, "value": 90}
        ]
    }
    
    with patch("streamlit.sidebar") as mock_sidebar:
        mock_radio = MagicMock(return_value="Paste JSON")
        mock_text_area = MagicMock(return_value=json.dumps(custom_data))
        mock_sidebar.radio = mock_radio
        mock_sidebar.text_area = mock_text_area
        
        with patch("streamlit.plotly_chart") as mock_plot:
            with patch("streamlit.session_state", new_callable=dict) as mock_state:
                # Initialize session state
                mock_state["show_filtered"] = True
                mock_state["clicked_node"] = None
                
                # Mock error handling
                with patch("streamlit.error") as mock_error:
                    main()
                    mock_text_area.assert_called_with("Paste your JSON data here")
                    assert mock_plot.call_count > 0, "Plot should be created with custom data"
                    mock_error.assert_not_called()

def test_branch_selection():
    """Test branch filtering functionality."""
    with patch("streamlit.sidebar") as mock_sidebar:
        mock_checkbox = MagicMock(return_value=True)
        mock_radio = MagicMock(return_value="Sample Data")
        mock_sidebar.checkbox = mock_checkbox
        mock_sidebar.radio = mock_radio
        
        with patch("streamlit.plotly_chart") as mock_plot:
            with patch("streamlit.session_state", new_callable=dict) as mock_state:
                # Initialize session state
                mock_state["show_filtered"] = True
                mock_state["clicked_node"] = None
                mock_state["data"] = None
                
                # Mock sample data loading with filtered nodes
                sample_data = {
                    "nodes": [
                        {"id": 0, "name": "Start"},
                        {"id": 1, "name": "Process"},
                        {"id": 2, "name": "End"},
                        {"id": 3, "name": "Filtered Out"}
                    ],
                    "links": [
                        {"source": 0, "target": 1, "value": 100},
                        {"source": 1, "target": 2, "value": 90},
                        {"source": 1, "target": 3, "value": 10}
                    ]
                }
                
                with patch("pages.13_Data_Pipeline_Flow.load_sample_data", return_value=sample_data):
                    with patch("pages.13_Data_Pipeline_Flow.validate_pipeline_data", return_value=True):
                        # Test with filtered nodes shown
                        mock_state["show_filtered"] = True
                        main()
                        
                        # Verify branch selection checkbox is shown
                        mock_checkbox.assert_called_with(
                            "Show filtered branches",
                            value=True,
                            help="Toggle visibility of filtered data branches"
                        )
                        
                        # Get plot data with filtered nodes
                        assert mock_plot.call_count > 0, "Plot should be created with filtered nodes"
                        plot_with_filtered = mock_plot.call_args[0][0]
                        
                        # Test with filtered nodes hidden
                        mock_state["show_filtered"] = False
                        main()
                        
                        # Get plot data without filtered nodes
                        assert mock_plot.call_count > 1, "Plot should update when hiding filtered nodes"
                        plot_without_filtered = mock_plot.call_args[0][0]
                        
                        # Verify filtered nodes are actually hidden
                        assert len(plot_with_filtered.data[0].node.label) > len(plot_without_filtered.data[0].node.label), \
                            "Plot should have fewer nodes when filtered nodes are hidden"

if __name__ == "__main__":
    pytest.main([__file__])
