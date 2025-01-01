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
    test_cases = load_test_cases()
    
    # Test valid cases
    for case in test_cases["valid_cases"]:
        assert validate_data(case["data"]) == case["expected"], f"Failed on valid case: {case['name']}"
    
    # Test invalid cases
    for case in test_cases["invalid_cases"]:
        assert validate_data(case["data"]) == case["expected"], f"Failed on invalid case: {case['name']}"

def test_chart_creation():
    """Test chart creation with sample data."""
    sample_data = [
        {"id": 0, "name": "Stage 1", "time": 60, "compute": 25},
        {"id": 1, "name": "Stage 2", "time": 120, "compute": 40}
    ]
    
    # Test time metric
    fig_time = create_resource_chart(sample_data, "time")
    assert isinstance(fig_time, go.Figure)
    assert len(fig_time.data) > 0
    
    # Test compute metric
    fig_compute = create_resource_chart(sample_data, "compute")
    assert isinstance(fig_compute, go.Figure)
    assert len(fig_compute.data) > 0

def test_data_sorting():
    """Test data sorting functionality."""
    sample_data = [
        {"id": 0, "name": "Stage 1", "time": 60},
        {"id": 1, "name": "Stage 2", "time": 120},
        {"id": 2, "name": "Stage 3", "time": 90}
    ]
    df = pd.DataFrame(sample_data)
    
    # Test ascending sort
    df_asc = df.sort_values(by="time", ascending=True)
    assert df_asc.iloc[0]["time"] == 60
    assert df_asc.iloc[-1]["time"] == 120
    
    # Test descending sort
    df_desc = df.sort_values(by="time", ascending=False)
    assert df_desc.iloc[0]["time"] == 120
    assert df_desc.iloc[-1]["time"] == 60

if __name__ == "__main__":
    pytest.main([__file__])
