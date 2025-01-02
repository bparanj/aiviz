import pytest
import json
from pathlib import Path
import sys
import os

# Add the project root to the Python path
project_root = str(Path(__file__).parent.parent)
if project_root not in sys.path:
    sys.path.append(project_root)

import sys
from pathlib import Path

# Add the project root to the Python path
project_root = str(Path(__file__).parent.parent)
if project_root not in sys.path:
    sys.path.append(project_root)

from pages.fourteen_Feature_Extraction import validate_feature_extraction_data, create_sankey_diagram

def load_test_cases():
    """Load test cases from JSON file."""
    test_cases_path = Path(project_root) / "data" / "feature_extraction_test_cases.json"
    with open(test_cases_path, "r") as f:
        return json.load(f)

def test_valid_feature_extraction_data():
    """Test validation of valid feature extraction data."""
    test_cases = load_test_cases()
    
    for case in test_cases["valid_cases"]:
        is_valid, message = validate_feature_extraction_data(case["data"])
        assert is_valid, f"Failed validation for valid case: {case['description']}\nError: {message}"

def test_invalid_feature_extraction_data():
    """Test validation of invalid feature extraction data."""
    test_cases = load_test_cases()
    
    for case in test_cases["invalid_cases"]:
        is_valid, message = validate_feature_extraction_data(case["data"])
        assert not is_valid, f"Failed to catch invalid case: {case['description']}"
        assert message == case["expected_error"], \
            f"Wrong error message for {case['description']}\nExpected: {case['expected_error']}\nGot: {message}"

def test_sankey_diagram_creation():
    """Test that Sankey diagram is created correctly."""
    sample_data = {
        "nodes": [
            {"id": 0, "name": "Raw Data"},
            {"id": 1, "name": "Features"}
        ],
        "links": [
            {"source": 0, "target": 1, "value": 100}
        ]
    }
    
    fig = create_sankey_diagram(sample_data)
    assert fig is not None
    assert hasattr(fig, "data")
    assert len(fig.data) > 0
    assert fig.data[0].type == "sankey"
    
    # Verify nodes and links
    assert hasattr(fig.data[0], "node")
    assert hasattr(fig.data[0], "link")
    assert len(fig.data[0].node.label) == len(sample_data["nodes"])
    assert len(fig.data[0].link.value) == len(sample_data["links"])

def test_node_highlighting():
    """Test node highlighting functionality."""
    sample_data = {
        "nodes": [
            {"id": 0, "name": "Raw Data"},
            {"id": 1, "name": "Features"}
        ],
        "links": [
            {"source": 0, "target": 1, "value": 100}
        ]
    }
    
    # Test without highlighting
    fig = create_sankey_diagram(sample_data)
    assert all(color != "#FFD700" for color in fig.data[0].node.color)
    
    # Test with highlighting
    fig = create_sankey_diagram(sample_data, highlight_node=0)
    assert fig.data[0].node.color[0] == "#FFD700"
    assert fig.data[0].node.color[1] != "#FFD700"

if __name__ == "__main__":
    pytest.main([__file__])
