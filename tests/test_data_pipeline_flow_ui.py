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

from pages.page13_Data_Pipeline_Flow import main, create_sankey_diagram, validate_pipeline_data

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

# Create a session state mock that behaves more like the real thing
class SessionStateMock(dict):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._has_triggered_rerun = False
    
    def __getitem__(self, key):
        if key not in self:
            self[key] = None
        return super().__getitem__(key)
    
    def get(self, key, default=None):
        if key not in self:
            self[key] = default
        return super().get(key, default)

@pytest.mark.parametrize("input_method", ["Sample Data", "Upload JSON", "Paste JSON"])
def test_input_method_selection(input_method):
    """Test different input methods for data."""
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
    
    with patch("streamlit.sidebar") as mock_sidebar:
        mock_radio = MagicMock(return_value=input_method)
        mock_uploader = MagicMock()
        mock_text_area = MagicMock()
        mock_sidebar.radio = mock_radio
        mock_sidebar.file_uploader = mock_uploader
        mock_sidebar.text_area = mock_text_area
        
        # Configure input method mocks
        if input_method == "Upload JSON":
            uploaded_file = MagicMock()
            uploaded_file.read = lambda: json.dumps(sample_data).encode()
            mock_uploader.return_value = uploaded_file
        elif input_method == "Paste JSON":
            mock_text_area.return_value = json.dumps(sample_data)
        
        # Use our custom SessionStateMock
        with patch("streamlit.session_state", new_callable=SessionStateMock) as mock_state:
            # Initialize session state
            mock_state["show_filtered"] = True
            mock_state["clicked_node"] = None
            # Initialize data for Sample Data, other methods will set it during main()
            if input_method == "Sample Data":
                mock_state["data"] = sample_data
            else:
                mock_state["data"] = None  # Let main() set the data based on input method
            
            with patch("streamlit.title"):
                with patch("streamlit.write"):
                    with patch("streamlit.columns") as mock_columns:
                        # Mock columns return value
                        mock_col = MagicMock()
                        mock_columns.return_value = [mock_col, mock_col, mock_col]
                        
                        with patch("streamlit.metric"):
                            with patch("streamlit.subheader"):
                                with patch("streamlit.error") as mock_error:
                                    with patch("streamlit.info"):
                                        with patch("streamlit.rerun"):
                                            with patch("streamlit.checkbox", return_value=True):
                                                # Create a mock figure object
                                                mock_fig = MagicMock()
                                                mock_fig.data = [MagicMock()]
                                                mock_fig.data[0].type = "sankey"
                                                mock_fig.data[0].node = MagicMock()
                                                mock_fig.data[0].link = MagicMock()
                                                mock_fig.layout = MagicMock()
                                                
                                                with patch("pages.page13_Data_Pipeline_Flow.create_sankey_diagram", return_value=mock_fig):
                                                    with patch("pages.page13_Data_Pipeline_Flow.validate_pipeline_data", return_value=(True, "")):
                                                        with patch("pages.page13_Data_Pipeline_Flow.load_sample_data", return_value=sample_data):
                                                            with patch("streamlit.plotly_chart") as mock_plot:
                                                                # Configure mock_plot to handle custom_events
                                                                mock_plot.return_value = {"plotly_click": {"points": [{"customdata": 1}]}}
                                                                
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
                                                                
                                                                # Verify plotly_chart was called with correct arguments
                                                                mock_plot.assert_called_with(
                                                                    mock_fig,
                                                                    use_container_width=True,
                                                                    custom_events=['plotly_click']
                                                                )
                                                                assert mock_plot.call_count > 0, "Plot should be created"
                                                                mock_error.assert_not_called()

def test_pipeline_statistics_display(sample_data):
    """Test that pipeline statistics are displayed correctly."""
    # Use the SessionStateMock class defined in test_input_method_selection
    with patch("streamlit.subheader") as mock_subheader:
        with patch("streamlit.columns") as mock_columns:
            with patch("streamlit.metric") as mock_metric:
                with patch("streamlit.session_state", new_callable=SessionStateMock) as mock_state:
                    # Mock session state
                    mock_state["show_filtered"] = True
                    mock_state["clicked_node"] = None
                    mock_state["data"] = sample_data  # Initialize data in session state
                    
                    # Mock sidebar components
                    with patch("streamlit.sidebar") as mock_sidebar:
                        mock_radio = MagicMock(return_value="Sample Data")
                        mock_sidebar.radio = mock_radio
                        mock_sidebar.checkbox = MagicMock(return_value=True)
                        
                        # Mock columns
                        mock_col = MagicMock()
                        mock_columns.return_value = [mock_col, mock_col, mock_col]
                        
                        # Run the main function
                        with patch("pages.page13_Data_Pipeline_Flow.load_sample_data", return_value=sample_data):
                            with patch("pages.page13_Data_Pipeline_Flow.validate_pipeline_data", return_value=(True, "")):
                                with patch("pages.page13_Data_Pipeline_Flow.create_sankey_diagram") as mock_create_diagram:
                                    # Create a mock figure
                                    mock_fig = MagicMock()
                                    mock_fig.data = [MagicMock()]
                                    mock_fig.data[0].type = "sankey"
                                    mock_fig.data[0].node = MagicMock()
                                    mock_fig.data[0].link = MagicMock()
                                    mock_fig.layout = MagicMock()
                                    mock_create_diagram.return_value = mock_fig
                                    
                                    with patch("streamlit.plotly_chart") as mock_plot:
                                        # Configure mock_plot to handle custom_events
                                        mock_plot.return_value = {"plotly_click": {"points": [{"customdata": 1}]}}
                                        
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
    is_valid, error_msg = validate_pipeline_data(invalid_data)
    assert not is_valid
    assert "unique" in error_msg.lower()
    
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
    is_valid, error_msg = validate_pipeline_data(invalid_data)
    assert not is_valid
    assert "valid node IDs" in error_msg
    
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
    is_valid, error_msg = validate_pipeline_data(invalid_data)
    assert not is_valid
    assert "non-negative" in error_msg.lower()
    
    # Test minimum nodes requirement
    invalid_data = {
        "nodes": [
            {"id": 0, "name": "Start"}
        ],
        "links": []
    }
    is_valid, error_msg = validate_pipeline_data(invalid_data)
    assert not is_valid
    assert "2 nodes" in error_msg

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
        
        with patch("streamlit.session_state", new_callable=SessionStateMock) as mock_state:
            # Initialize session state without data - let main() set it from text area
            mock_state["show_filtered"] = True
            mock_state["clicked_node"] = None
            mock_state["data"] = None
            
            with patch("streamlit.title"):
                with patch("streamlit.write"):
                    with patch("streamlit.columns") as mock_columns:
                        # Mock columns return value
                        mock_col = MagicMock()
                        mock_columns.return_value = [mock_col, mock_col, mock_col]
                        
                        with patch("streamlit.metric"):
                            with patch("streamlit.subheader"):
                                with patch("streamlit.error") as mock_error:
                                    with patch("streamlit.info"):
                                        with patch("streamlit.rerun"):
                                            with patch("streamlit.checkbox", return_value=True):
                                                # Create a mock figure object
                                                mock_fig = MagicMock()
                                                mock_fig.data = [MagicMock()]
                                                mock_fig.data[0].type = "sankey"
                                                mock_fig.data[0].node = MagicMock()
                                                mock_fig.data[0].link = MagicMock()
                                                mock_fig.layout = MagicMock()
                                                
                                                with patch("pages.page13_Data_Pipeline_Flow.create_sankey_diagram", return_value=mock_fig):
                                                    with patch("pages.page13_Data_Pipeline_Flow.validate_pipeline_data", return_value=(True, "")):
                                                        with patch("streamlit.plotly_chart") as mock_plot:
                                                            # Configure mock_plot to handle custom_events
                                                            mock_plot.return_value = {"plotly_click": {"points": [{"customdata": 1}]}}
                                                            
                                                            main()
                                                            
                                                            mock_text_area.assert_called_with("Paste your JSON data here")
                                                            assert mock_plot.call_count > 0, "Plot should be created with custom data"
                                                            mock_error.assert_not_called()
                                                            mock_plot.assert_called_with(
                                                                mock_fig,
                                                                use_container_width=True,
                                                                custom_events=['plotly_click']
                                                            )

def test_branch_selection():
    """Test branch filtering functionality."""
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
    
    with patch("streamlit.sidebar") as mock_sidebar:
        mock_checkbox = MagicMock(return_value=True)
        mock_radio = MagicMock(return_value="Sample Data")
        mock_sidebar.checkbox = mock_checkbox
        mock_sidebar.radio = mock_radio
        
        with patch("streamlit.session_state", new_callable=SessionStateMock) as mock_state: 
            # Initialize session state
            mock_state["show_filtered"] = True
            mock_state["clicked_node"] = None
            mock_state["data"] = sample_data
            
            with patch("streamlit.title"):
                with patch("streamlit.write"):
                    with patch("streamlit.columns") as mock_columns:
                        # Mock columns return value
                        mock_col = MagicMock()
                        mock_columns.return_value = [mock_col, mock_col, mock_col]
                        
                        with patch("streamlit.metric"):
                            with patch("streamlit.subheader"):
                                with patch("streamlit.error"):
                                    with patch("streamlit.info"):
                                        with patch("streamlit.rerun"):
                                            # Create mock figures for both filtered and unfiltered cases
                                            mock_fig_filtered = MagicMock()
                                            mock_fig_filtered.data = [MagicMock()]
                                            mock_fig_filtered.data[0].type = "sankey"
                                            mock_fig_filtered.data[0].node = MagicMock()
                                            mock_fig_filtered.data[0].node.label = ["Start", "Process", "End", "Filtered Out"]
                                            mock_fig_filtered.data[0].link = MagicMock()
                                            mock_fig_filtered.layout = MagicMock()
                                            
                                            mock_fig_unfiltered = MagicMock()
                                            mock_fig_unfiltered.data = [MagicMock()]
                                            mock_fig_unfiltered.data[0].type = "sankey"
                                            mock_fig_unfiltered.data[0].node = MagicMock()
                                            mock_fig_unfiltered.data[0].node.label = ["Start", "Process", "End"]
                                            mock_fig_unfiltered.data[0].link = MagicMock()
                                            mock_fig_unfiltered.layout = MagicMock()
                                            
                                            with patch("pages.page13_Data_Pipeline_Flow.create_sankey_diagram") as mock_create_diagram:
                                                # Configure create_sankey_diagram to return different figures based on show_filtered
                                                def create_diagram_side_effect(*args, **kwargs):
                                                    return mock_fig_filtered if mock_state["show_filtered"] else mock_fig_unfiltered
                                                mock_create_diagram.side_effect = create_diagram_side_effect
                                                
                                                with patch("pages.page13_Data_Pipeline_Flow.validate_pipeline_data", return_value=(True, "")):
                                                    with patch("pages.page13_Data_Pipeline_Flow.load_sample_data", return_value=sample_data):
                                                        with patch("streamlit.plotly_chart") as mock_plot:
                                                            # Configure mock_plot to handle custom_events
                                                            mock_plot.return_value = {"plotly_click": {"points": [{"customdata": 1}]}}
                                                            
                                                            # Test with filtered nodes shown
                                                            mock_state["show_filtered"] = True
                                                            main()
                                                            
                                                            # Verify branch selection checkbox is shown
                                                            mock_checkbox.assert_called_with(
                                                                "Show filtered branches",
                                                                value=True,
                                                                help="Toggle visibility of filtered data branches"
                                                            )
                                                            
                                                            # Verify first call with filtered nodes
                                                            assert mock_plot.call_count > 0, "Plot should be created with filtered nodes"
                                                            first_call = mock_plot.call_args_list[0]
                                                            assert first_call[1]["use_container_width"] is True, "Plot should use container width"
                                                            assert first_call[1]["custom_events"] == ['plotly_click'], "Plot should handle click events"
                                                            assert len(first_call[0][0].data[0].node.label) == 4, "Should show all nodes including filtered"
                                                            
                                                            # Test with filtered nodes hidden
                                                            mock_state["show_filtered"] = False
                                                            main()
                                                            
                                                            # Verify second call with unfiltered nodes
                                                            assert mock_plot.call_count > 1, "Plot should update when hiding filtered nodes"
                                                            second_call = mock_plot.call_args_list[1]
                                                            assert second_call[1]["use_container_width"] is True, "Plot should use container width"
                                                            assert second_call[1]["custom_events"] == ['plotly_click'], "Plot should handle click events"
                                                            assert len(second_call[0][0].data[0].node.label) == 3, "Should show only unfiltered nodes"
                                                            
                                                            # Verify filtered nodes count difference
                                                            assert len(first_call[0][0].data[0].node.label) > len(second_call[0][0].data[0].node.label), \
                                                                "Plot should have fewer nodes when filtered nodes are hidden"

if __name__ == "__main__":
    pytest.main([__file__])
