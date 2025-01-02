import json
import pytest
import sys
import os
from pathlib import Path

# Add the project root to Python path
project_root = str(Path(__file__).parent.parent)
if project_root not in sys.path:
    sys.path.append(project_root)

from pages.seventeen_Error_Dropout_Tracking import validate_data

def load_test_cases():
    """Load test cases from JSON file."""
    with open("data/error_dropout_test_cases.json", "r") as f:
        return json.load(f)

def test_valid_data_cases():
    """Test that valid data cases pass validation."""
    test_cases = load_test_cases()
    
    for case in test_cases["valid_cases"]:
        assert validate_data(case["data"]), \
            f"Valid case failed: {case['description']}"

def test_invalid_data_cases():
    """Test that invalid data cases fail validation."""
    test_cases = load_test_cases()
    
    for case in test_cases["invalid_cases"]:
        assert not validate_data(case["data"]), \
            f"Invalid case passed validation: {case['description']}"

def test_unique_node_ids():
    """Test that duplicate node IDs are rejected."""
    data = {
        "nodes": [
            {"id": 0, "name": "Node 1"},
            {"id": 0, "name": "Node 2"}
        ],
        "links": []
    }
    assert not validate_data(data), "Duplicate node IDs should be rejected"

def test_valid_references():
    """Test that links reference valid node IDs."""
    data = {
        "nodes": [
            {"id": 0, "name": "Node 1"},
            {"id": 1, "name": "Node 2"}
        ],
        "links": [
            {"source": 0, "target": 2, "value": 100}  # Invalid target
        ]
    }
    assert not validate_data(data), "Invalid node references should be rejected"

def test_non_negative_values():
    """Test that negative values are rejected."""
    data = {
        "nodes": [
            {"id": 0, "name": "Node 1"},
            {"id": 1, "name": "Node 2"}
        ],
        "links": [
            {"source": 0, "target": 1, "value": -100}
        ]
    }
    assert not validate_data(data), "Negative values should be rejected"

def test_required_fields():
    """Test that missing required fields are rejected."""
    data = {
        "nodes": [
            {"name": "Missing ID"},
            {"id": 1}  # Missing name
        ],
        "links": [
            {"source": 0, "target": 1}  # Missing value
        ]
    }
    assert not validate_data(data), "Missing required fields should be rejected"

def test_meaningful_dropouts():
    """Test that data must include at least one dropout path."""
    data = {
        "nodes": [
            {"id": 0, "name": "Start"},
            {"id": 1, "name": "Middle"},
            {"id": 2, "name": "End"}
        ],
        "links": [
            {"source": 0, "target": 1, "value": 100},
            {"source": 1, "target": 2, "value": 100}
        ]
    }
    assert not validate_data(data), "Data without dropout paths should be rejected"

def test_valid_node_structure():
    """Test that node structure is valid."""
    data = {
        "nodes": "not a list",  # Invalid type
        "links": []
    }
    assert not validate_data(data), "Invalid node structure should be rejected"

def test_valid_link_structure():
    """Test that link structure is valid."""
    data = {
        "nodes": [
            {"id": 0, "name": "Node 1"},
            {"id": 1, "name": "Node 2"}
        ],
        "links": "not a list"  # Invalid type
    }
    assert not validate_data(data), "Invalid link structure should be rejected"

def test_data_type():
    """Test that input data must be a dictionary."""
    assert not validate_data([]), "Non-dictionary data should be rejected"
    assert not validate_data("string"), "Non-dictionary data should be rejected"
    assert not validate_data(None), "None should be rejected"

def test_required_sections():
    """Test that data must contain both nodes and links sections."""
    assert not validate_data({"nodes": []}), "Missing links section should be rejected"
    assert not validate_data({"links": []}), "Missing nodes section should be rejected"
    assert not validate_data({}), "Empty data should be rejected"
