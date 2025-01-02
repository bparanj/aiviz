import json
from pathlib import Path
import sys
import pytest

# Add the parent directory to the Python path
sys.path.append(str(Path(__file__).parent.parent))

from pages.knowledge_graph import validate_knowledge_graph_data

def load_test_cases():
    test_cases_path = Path(__file__).parent.parent / "data" / "knowledge_graph_test_cases.json"
    with open(test_cases_path, "r") as f:
        return json.load(f)["test_cases"]

@pytest.mark.parametrize("test_case", load_test_cases())
def test_knowledge_graph_validation(test_case):
    """Test knowledge graph data validation with various test cases."""
    is_valid, message = validate_knowledge_graph_data(test_case["data"])
    assert is_valid == test_case["expected_valid"], \
        f"Test case '{test_case['name']}' failed. Expected valid={test_case['expected_valid']}, got {is_valid}. Message: {message}"

def test_valid_graph_structure():
    """Test a valid graph structure with all optional fields."""
    data = {
        "nodes": [
            {"id": "Person1", "label": "Alice"},
            {"id": "Person2", "label": "Bob"},
            {"id": "City1", "label": "Berlin"}
        ],
        "links": [
            {"source": "Person1", "target": "Person2", "type": "friends"},
            {"source": "Person1", "target": "City1", "type": "lives_in"}
        ]
    }
    is_valid, message = validate_knowledge_graph_data(data)
    assert is_valid, f"Valid graph structure test failed: {message}"

def test_missing_required_fields():
    """Test handling of missing required fields."""
    data = {
        "nodes": [
            {"label": "Alice"},  # Missing id
            {"id": "Person2", "label": "Bob"}
        ],
        "links": [
            {"source": "Person1", "target": "Person2"}
        ]
    }
    is_valid, message = validate_knowledge_graph_data(data)
    assert not is_valid, "Should fail when required fields are missing"

def test_empty_graph():
    """Test handling of empty graph."""
    data = {
        "nodes": [],
        "links": []
    }
    is_valid, message = validate_knowledge_graph_data(data)
    assert not is_valid, "Should fail with empty graph"
