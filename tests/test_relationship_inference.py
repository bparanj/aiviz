import sys
from pathlib import Path
import json
import pytest

# Add the project root to the Python path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

# Import validate_data from the correct module
from pages.nine_Relationship_Inference import validate_data

def load_test_cases():
    """Load test cases from JSON file."""
    test_file = project_root / "data" / "relationship_inference_test_cases.json"
    with open(test_file, 'r') as f:
        return json.load(f)['test_cases']

@pytest.mark.parametrize("test_case", load_test_cases())
def test_validate_data(test_case):
    """Test data validation with various test cases."""
    is_valid, message = validate_data(test_case['data'])
    assert is_valid == test_case['expected'], \
        f"Test case '{test_case['name']}' failed: {message}"
    if not is_valid:
        assert message, "Error message should not be empty for invalid data"

def test_valid_data_structure():
    """Test validation of a valid data structure."""
    data = {
        "nodes": [
            {"id": "1", "label": "Node 1"},
            {"id": "2", "label": "Node 2"},
            {"id": "3", "label": "Node 3"}
        ],
        "links": [
            {"source": "1", "target": "2", "type": "test"},
            {"source": "2", "target": "3", "type": "test"}
        ]
    }
    is_valid, message = validate_data(data)
    assert is_valid, f"Valid data structure was rejected: {message}"

def test_invalid_node_structure():
    """Test validation of invalid node structure."""
    data = {
        "nodes": [
            {"id": "1", "label": "Node 1"},
            {"label": "Missing ID"},  # Missing ID
            {"id": "3", "label": "Node 3"}
        ],
        "links": [
            {"source": "1", "target": "3"}
        ]
    }
    is_valid, message = validate_data(data)
    assert not is_valid, "Invalid node structure was accepted"
    assert "must have an 'id' field" in message

def test_invalid_link_references():
    """Test validation of invalid link references."""
    data = {
        "nodes": [
            {"id": "1", "label": "Node 1"},
            {"id": "2", "label": "Node 2"},
            {"id": "3", "label": "Node 3"}
        ],
        "links": [
            {"source": "1", "target": "4"}  # Non-existent target
        ]
    }
    is_valid, message = validate_data(data)
    assert not is_valid, "Invalid link reference was accepted"
    assert "not found in nodes" in message
