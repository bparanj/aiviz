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

from pages.thirteen_Data_Pipeline_Flow import main, create_sankey_diagram

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
    assert isinstance(fig, dict)  # Plotly figures are dictionaries
    assert "data" in fig
    assert len(fig["data"]) > 0
    assert fig["data"][0]["type"] == "sankey"

@pytest.mark.parametrize("input_method", ["Sample Data", "Upload JSON", "Paste JSON"])
def test_input_method_selection(input_method):
    """Test different input methods for data."""
    with patch("streamlit.radio") as mock_radio:
        mock_radio.return_value = input_method
        with patch("streamlit.file_uploader") as mock_uploader:
            with patch("streamlit.text_area") as mock_text_area:
                with patch("streamlit.plotly_chart") as mock_plot:
                    # Run the main function
                    main()
                    
                    # Verify the radio button was shown
                    mock_radio.assert_called_once()
                    
                    # Check appropriate input method was displayed
                    if input_method == "Upload JSON":
                        mock_uploader.assert_called_once()
                    elif input_method == "Paste JSON":
                        mock_text_area.assert_called_once()

def test_pipeline_statistics_display(sample_data):
    """Test that pipeline statistics are displayed correctly."""
    with patch("streamlit.subheader") as mock_subheader:
        with patch("streamlit.write") as mock_write:
            # Mock session state
            st.session_state.data = sample_data
            
            # Run the main function
            main()
            
            # Verify statistics section is shown
            mock_subheader.assert_any_call("Pipeline Statistics")
            
            # Verify statistics calculations
            calls = mock_write.call_args_list
            stats_shown = False
            for call in calls:
                args = call[0][0]
                if isinstance(args, str):
                    if "Total input records:" in args:
                        stats_shown = True
                        break
            assert stats_shown

def test_node_highlighting():
    """Test node highlighting functionality."""
    with patch("streamlit.session_state") as mock_session:
        # Simulate node click
        mock_session.clicked_node = 1
        
        # Create diagram with highlighting
        sample_data_path = Path(project_root) / "data" / "data_pipeline_flow_sample.json"
        with open(sample_data_path, "r") as f:
            data = json.load(f)
        
        fig = create_sankey_diagram(data)
        
        # Verify highlighting is applied
        assert fig["data"][0]["node"]["color"] is not None

def test_hover_tooltips(sample_data):
    """Test that hover tooltips are configured correctly."""
    fig = create_sankey_diagram(sample_data)
    
    # Verify hover text is configured
    assert "hovertext" in fig["data"][0]["node"]
    assert "hovertext" in fig["data"][0]["link"]
    
    # Verify hover template is set
    assert "hovertemplate" in fig["data"][0]["node"]
    assert "hovertemplate" in fig["data"][0]["link"]

if __name__ == "__main__":
    pytest.main([__file__])
