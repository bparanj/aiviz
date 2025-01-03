import pytest
import streamlit as st
import plotly.graph_objects as go
import json
import numpy as np
import pandas as pd
from typing import cast, List, Dict, Union, Any
from unittest.mock import MagicMock, patch
from pages.page16_Resource_Consumption import main, create_resource_chart

# Type hints for Plotly objects
Figure = Any
Bar = Any

# Mock streamlit session state
class MockSessionState:
    def __init__(self):
        self._state = {}
    
    def __getattr__(self, name):
        if name not in self._state:
            self._state[name] = None
        return self._state[name]
    
    def __setattr__(self, name, value):
        if name == '_state':
            super().__setattr__(name, value)
        else:
            self._state[name] = value

@pytest.fixture
def mock_session_state():
    return MockSessionState()

@pytest.fixture
def mock_streamlit():
    with patch('streamlit.file_uploader') as mock_uploader, \
         patch('streamlit.text_area') as mock_text_area, \
         patch('streamlit.selectbox') as mock_select, \
         patch('streamlit.plotly_chart') as mock_chart, \
         patch('streamlit.error') as mock_error:
        
        yield {
            'uploader': mock_uploader,
            'text_area': mock_text_area,
            'select': mock_select,
            'chart': mock_chart,
            'error': mock_error
        }

def test_user_input_handling(mock_streamlit, mock_session_state):
    """Test user input handling through different methods."""
    # Mock sample data
    sample_data = [
        {"id": 0, "name": "Stage 1", "time": 60, "compute": 25},
        {"id": 1, "name": "Stage 2", "time": 120, "compute": 40}
    ]
    
    # Mock file upload
    class MockUploadedFile:
        def __init__(self, content):
            self.content = content
        def read(self):
            return json.dumps(self.content).encode()
    
    # Set up mock returns
    mock_streamlit['uploader'].return_value = MockUploadedFile(sample_data)
    mock_streamlit['text_area'].return_value = json.dumps(sample_data)
    mock_streamlit['select'].return_value = "time"
    
    # Run main function with mocked session state
    with patch('streamlit.session_state', mock_session_state):
        main()
    
    # Verify file upload handling
    mock_streamlit['uploader'].assert_called_once()
    assert "json" in mock_streamlit['uploader'].call_args[1]['type']
    
    # Verify JSON input handling
    mock_streamlit['text_area'].assert_called_once()
    
    # Verify metric selection
    mock_streamlit['select'].assert_called_once()
    assert "time" in mock_streamlit['select'].call_args[1]['options']
    
    # Verify chart creation
    mock_streamlit['chart'].assert_called_once()
    
    # Verify no errors occurred
    mock_streamlit['error'].assert_not_called()

def test_error_handling():
    """Test error handling for invalid inputs."""
    # Test missing required fields
    invalid_data = [
        {"id": 0, "time": 60},  # Missing name
        {"id": 1, "name": "Stage 2"}  # Missing time/compute
    ]
    with pytest.raises(ValueError) as exc_info:
        create_resource_chart(invalid_data, "time")
    assert "Missing required field" in str(exc_info.value)
    
    # Test invalid metric type
    valid_data = [
        {"id": 0, "name": "Stage 1", "time": 60, "compute": 25},
        {"id": 1, "name": "Stage 2", "time": 120, "compute": 40}
    ]
    with pytest.raises(ValueError) as exc_info:
        create_resource_chart(valid_data, "invalid_metric")
    assert "Invalid metric type" in str(exc_info.value)
    
    # Test non-numeric values
    invalid_numeric = [
        {"id": 0, "name": "Stage 1", "time": "invalid", "compute": 25},
        {"id": 1, "name": "Stage 2", "time": 120, "compute": 40}
    ]
    with pytest.raises(ValueError) as exc_info:
        create_resource_chart(invalid_numeric, "time")
    assert "must be numeric" in str(exc_info.value)

def test_interactive_features():
    """Test interactive features like hover tooltips and sorting."""
    sample_data = [
        {"id": 0, "name": "Stage 1", "time": 60, "compute": 25},
        {"id": 1, "name": "Stage 2", "time": 120, "compute": 40}
    ]
    
    # Test time metric visualization
    fig_time: Figure = create_resource_chart(sample_data, "time")
    assert isinstance(fig_time, go.Figure)
    
    # Get the bar trace
    assert isinstance(fig_time.data, (list, tuple))
    assert len(fig_time.data) == 1
    trace: Bar = cast(Bar, fig_time.data[0])
    assert isinstance(trace, go.Bar)
    
    # Test hover template
    hover_template = getattr(trace, 'hovertemplate', '')
    assert isinstance(hover_template, str)
    assert "Stage:" in hover_template
    assert "Time:" in hover_template
    assert "%{y}" in hover_template  # Stage name
    assert "%{x}" in hover_template  # Value
    
    # Test compute metric visualization
    fig_compute: Figure = create_resource_chart(sample_data, "compute")
    assert isinstance(fig_compute, go.Figure)
    assert isinstance(fig_compute.data, (list, tuple))
    assert len(fig_compute.data) == 1
    trace = cast(Bar, fig_compute.data[0])
    assert isinstance(trace, go.Bar)
    
    # Test hover template for compute
    hover_template = getattr(trace, 'hovertemplate', '')
    assert isinstance(hover_template, str)
    assert "Stage:" in hover_template
    assert "Compute:" in hover_template.lower()
    assert "%{y}" in hover_template  # Stage name
    assert "%{x}" in hover_template  # Value
    
    # Test bar chart properties
    assert trace.orientation == "h"
    x_values = [float(x) for x in trace.x] if trace.x else []
    y_values = [str(y) for y in trace.y] if trace.y else []
    assert len(x_values) == len(sample_data)
    assert len(y_values) == len(sample_data)
    assert all(isinstance(x, float) for x in x_values)
    assert all(isinstance(y, str) for y in y_values)
    
    # Test layout configuration
    layout = fig_compute.layout
    assert getattr(layout, 'dragmode', None) == "zoom"  # Enable zooming
    assert getattr(layout, 'hovermode', None) == "closest"  # Hover interaction
    assert getattr(layout, 'clickmode', None) == "event+select"  # Click interaction
    
    # Test sorting functionality
    df = pd.DataFrame(sample_data)
    
    # Test ascending sort
    df_asc = df.sort_values(by="compute", ascending=True)
    compute_values_asc = list(df_asc["compute"])
    assert compute_values_asc == [25, 40], "Ascending compute sort"
    
    # Test descending sort
    df_desc = df.sort_values(by="compute", ascending=False)
    compute_values_desc = list(df_desc["compute"])
    assert compute_values_desc == [40, 25], "Descending compute sort"

def test_chart_layout():
    """Test chart layout requirements."""
    sample_data = [
        {"id": 0, "name": "Stage 1", "time": 60, "compute": 25},
        {"id": 1, "name": "Stage 2", "time": 120, "compute": 40}
    ]
    
    # Create chart
    fig: Figure = create_resource_chart(sample_data, "time")
    assert isinstance(fig, go.Figure)
    
    # Test layout properties
    layout = fig.layout
    
    # Test axes labels
    xaxis_title = getattr(layout.xaxis, 'title', None)
    yaxis_title = getattr(layout.yaxis, 'title', None)
    assert xaxis_title is not None
    assert yaxis_title is not None
    assert getattr(xaxis_title, 'text', '') == "Time (seconds)"
    assert getattr(yaxis_title, 'text', '') == "Pipeline Stage"
    
    # Test orientation and bar properties
    assert isinstance(fig.data, (list, tuple))
    assert len(fig.data) == 1
    trace: Bar = cast(Bar, fig.data[0])
    assert isinstance(trace, go.Bar)
    assert trace.orientation == "h"
    
    # Test bar lengths correspond to values
    x_values = [float(x) for x in trace.x] if trace.x else []
    y_values = [str(y) for y in trace.y] if trace.y else []
    assert x_values == [60.0, 120.0]
    assert y_values == ["Stage 1", "Stage 2"]
    
    # Test chart responsiveness and interactivity
    assert getattr(layout, 'autosize', False) is True
    assert getattr(layout, 'margin', {}).get('autoexpand', False) is True
    assert getattr(layout, 'showlegend', True) is False  # No legend needed for single trace
    assert getattr(layout, 'barmode', '') == 'relative'  # Default bar mode for single trace
