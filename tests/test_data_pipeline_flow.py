import json
import pytest
from pathlib import Path
import sys
import os

# Add the project root to the Python path
project_root = str(Path(__file__).parent.parent)
if project_root not in sys.path:
    sys.path.append(project_root)

from pages.page13_Data_Pipeline_Flow import validate_pipeline_data

def load_test_cases():
    """Load test cases from JSON file."""
    test_cases_path = Path(project_root) / "data" / "data_pipeline_flow_test_cases.json"
    with open(test_cases_path, "r") as f:
        return json.load(f)

def test_valid_pipeline_data():
    """Test validation of valid pipeline data."""
    test_cases = load_test_cases()
    
    for case in test_cases["valid_cases"]:
        is_valid, message = validate_pipeline_data(case["data"])
        assert is_valid, f"Failed validation for valid case: {case['description']}\nError: {message}"

def test_invalid_pipeline_data():
    """Test validation of invalid pipeline data."""
    test_cases = load_test_cases()
    
    for case in test_cases["invalid_cases"]:
        is_valid, message = validate_pipeline_data(case["data"])
        assert not is_valid, f"Failed to catch invalid case: {case['description']}"
        assert message == case["expected_error"], \
            f"Wrong error message for {case['description']}\nExpected: {case['expected_error']}\nGot: {message}"

def test_non_dict_input():
    """Test validation of non-dictionary input."""
    invalid_inputs = [
        None,
        42,
        "string",
        [],
        [1, 2, 3]
    ]
    
    for data in invalid_inputs:
        is_valid, message = validate_pipeline_data(data)
        assert not is_valid
        assert message == "Data must be a dictionary"

def test_missing_required_node_fields():
    """Test validation of nodes missing required fields."""
    data = {
        "nodes": [
            { "id": 0 },  # Missing name
            { "name": "Processed" }  # Missing id
        ],
        "links": [
            { "source": 0, "target": 1, "value": 100 }
        ]
    }
    is_valid, message = validate_pipeline_data(data)
    assert not is_valid
    assert message == "Each node must have 'id' and 'name' fields"

def test_missing_required_link_fields():
    """Test validation of links missing required fields."""
    data = {
        "nodes": [
            { "id": 0, "name": "Raw Data" },
            { "id": 1, "name": "Processed" }
        ],
        "links": [
            { "source": 0, "value": 100 },  # Missing target
            { "source": 0, "target": 1 }    # Missing value
        ]
    }
    is_valid, message = validate_pipeline_data(data)
    assert not is_valid
    assert message == "Each link must have 'source', 'target', and 'value' fields"

if __name__ == "__main__":
    pytest.main([__file__])
