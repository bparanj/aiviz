import sys
import os
import json
import pytest
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

# Import the page module
from pages.sixteen_Resource_Consumption import validate_data, create_resource_chart

def load_test_cases():
    """Load test cases from JSON file."""
    with open(os.path.join(project_root, "data", "resource_consumption_test_cases.json"), "r") as f:
        return json.load(f)

def test_data_validation():
    """Test data validation function with various test cases."""
    # Test valid data
    valid_data = [
        {"id": 0, "name": "Stage 1", "time": 60, "compute": 25},
        {"id": 1, "name": "Stage 2", "time": 120, "compute": 40}
    ]
    is_valid, error_msg = validate_data(valid_data)
    assert is_valid
    assert error_msg == ""
    
    # Test various invalid cases
    test_cases = [
        (
            [],
            "At least one pipeline stage is required"
        ),
        (
            [{"id": 0, "name": "Stage 1", "time": 60}],
            "At least two pipeline stages are recommended"
        ),
        (
            [{"name": "Stage 1", "time": 60}, {"name": "Stage 2", "time": 120}],
            "missing required fields"
        ),
        (
            [
                {"id": "0", "name": "Stage 1", "time": 60},
                {"id": 1, "name": "Stage 2", "time": 120}
            ],
            "ID must be an integer"
        ),
        (
            [
                {"id": 0, "name": "", "time": 60},
                {"id": 1, "name": "Stage 2", "time": 120}
            ],
            "name cannot be empty"
        ),
        (
            [
                {"id": 0, "name": "Stage 1", "time": -60},
                {"id": 1, "name": "Stage 2", "time": 120}
            ],
            "time value must be non-negative"
        ),
        (
            [
                {"id": 0, "name": "Stage 1", "compute": -25},
                {"id": 1, "name": "Stage 2", "compute": 40}
            ],
            "compute value must be non-negative"
        ),
        (
            [
                {"id": 0, "name": "Stage 1", "time": 60},
                {"id": 0, "name": "Stage 2", "time": 120}
            ],
            "Duplicate stage ID"
        )
    ]
    
    for data, expected_error in test_cases:
        is_valid, error_msg = validate_data(data)
        assert not is_valid
        assert expected_error in error_msg, f"Expected '{expected_error}' in '{error_msg}'"

def test_chart_creation():
    """Test chart creation and visualization features."""
    sample_data = [
        {"id": 0, "name": "Data Ingestion", "time": 60, "compute": 25},
        {"id": 1, "name": "Data Cleaning", "time": 120, "compute": 40},
        {"id": 2, "name": "Feature Extract", "time": 90, "compute": 35}
    ]
    
    # Test time metric visualization
    fig_time = create_resource_chart(sample_data, "time")
    assert isinstance(fig_time, go.Figure)
    
    # Test basic chart properties
    assert isinstance(fig_time.data, tuple)
    assert len(fig_time.data) == 1  # One trace for bar chart
    trace = fig_time.data[0]
    assert isinstance(trace, go.Bar)
    assert trace.orientation == "h"
    
    # Test data points
    x_values = np.array(trace.x)
    y_values = np.array(trace.y)
    assert len(x_values) == len(sample_data)
    assert len(y_values) == len(sample_data)
    
    # Test x values are numeric and match input
    expected_x = np.array([d["time"] for d in sample_data])
    np.testing.assert_array_equal(x_values, expected_x)
    
    # Test y values are strings and match input
    expected_y = np.array([d["name"] for d in sample_data])
    np.testing.assert_array_equal(y_values, expected_y)
    
    # Test layout
    layout = fig_time.layout
    assert isinstance(layout.title.text, str)
    assert isinstance(layout.xaxis.title.text, str)
    assert isinstance(layout.yaxis.title.text, str)
    
    assert "Pipeline Stage Time Consumption" in layout.title.text
    assert "seconds" in layout.xaxis.title.text.lower()
    assert "Pipeline Stage" in layout.yaxis.title.text
    
    # Test hover template
    assert isinstance(trace.hovertemplate, str)
    assert "time" in trace.hovertemplate.lower()
    assert "%{y}" in trace.hovertemplate  # Stage name
    assert "%{x}" in trace.hovertemplate  # Value
    
    # Test compute metric visualization
    fig_compute = create_resource_chart(sample_data, "compute")
    assert isinstance(fig_compute, go.Figure)
    assert isinstance(fig_compute.data, tuple)
    assert len(fig_compute.data) == 1
    
    # Test compute chart properties
    trace = fig_compute.data[0]
    assert isinstance(trace, go.Bar)
    assert trace.orientation == "h"
    
    # Test compute data points
    x_values = np.array(trace.x)
    y_values = np.array(trace.y)
    assert len(x_values) == len(sample_data)
    assert len(y_values) == len(sample_data)
    
    # Test x values are numeric and match input
    expected_x = np.array([d["compute"] for d in sample_data])
    np.testing.assert_array_equal(x_values, expected_x)
    
    # Test y values are strings and match input
    expected_y = np.array([d["name"] for d in sample_data])
    np.testing.assert_array_equal(y_values, expected_y)
    
    # Test compute layout
    layout = fig_compute.layout
    assert isinstance(layout.title.text, str)
    assert isinstance(layout.xaxis.title.text, str)
    assert isinstance(layout.yaxis.title.text, str)
    
    assert "Pipeline Stage Compute Consumption" in layout.title.text
    assert "utilization" in layout.xaxis.title.text.lower()
    assert "Pipeline Stage" in layout.yaxis.title.text

def test_data_sorting():
    """Test data sorting functionality."""
    sample_data = [
        {"id": 0, "name": "Stage 1", "time": 60, "compute": 25},
        {"id": 1, "name": "Stage 2", "time": 120, "compute": 40},
        {"id": 2, "name": "Stage 3", "time": 90, "compute": 35}
    ]
    
    # Test time metric sorting
    fig_time_asc = create_resource_chart(sample_data, "time")
    assert isinstance(fig_time_asc, go.Figure)
    assert isinstance(fig_time_asc.data, tuple)
    trace_asc = fig_time_asc.data[0]
    x_values = list(trace_asc.x)
    assert x_values == [60, 120, 90], "Original order maintained"
    
    # Test compute metric sorting
    fig_compute_asc = create_resource_chart(sample_data, "compute")
    assert isinstance(fig_compute_asc, go.Figure)
    assert isinstance(fig_compute_asc.data, tuple)
    trace_asc = fig_compute_asc.data[0]
    x_values = list(trace_asc.x)
    assert x_values == [25, 40, 35], "Original order maintained"
    
    # Test DataFrame sorting (underlying functionality)
    df = pd.DataFrame(sample_data)
    
    # Time metric
    df_time_asc = df.sort_values(by="time", ascending=True)
    assert list(df_time_asc["time"]) == [60, 90, 120], "Ascending time sort"
    
    df_time_desc = df.sort_values(by="time", ascending=False)
    assert list(df_time_desc["time"]) == [120, 90, 60], "Descending time sort"
    
    # Compute metric
    df_compute_asc = df.sort_values(by="compute", ascending=True)
    assert list(df_compute_asc["compute"]) == [25, 35, 40], "Ascending compute sort"
    
    df_compute_desc = df.sort_values(by="compute", ascending=False)
    assert list(df_compute_desc["compute"]) == [40, 35, 25], "Descending compute sort"

if __name__ == "__main__":
    pytest.main([__file__])
