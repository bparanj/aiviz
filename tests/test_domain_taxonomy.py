import json
import pytest
from pathlib import Path
import sys
import os

# Add the parent directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pages.domain_taxonomy import validate_node, process_data_for_treemap

def load_test_cases():
    test_cases_path = Path(__file__).parent.parent / "data" / "domain_taxonomy_test_cases.json"
    with open(test_cases_path, 'r') as f:
        return json.load(f)

test_cases = load_test_cases()

@pytest.mark.parametrize("test_case", test_cases["valid_cases"])
def test_valid_cases(test_case):
    """Test that valid data structures pass validation."""
    is_valid, message = validate_node(test_case["data"])
    assert is_valid, f"Failed on valid case '{test_case['name']}': {message}"

@pytest.mark.parametrize("test_case", test_cases["invalid_cases"])
def test_invalid_cases(test_case):
    """Test that invalid data structures fail validation with correct error messages."""
    is_valid, message = validate_node(test_case["data"])
    assert not is_valid, f"Invalid case '{test_case['name']}' passed validation"
    assert message == test_case["error"], f"Wrong error message for '{test_case['name']}'"

def test_process_data_for_treemap():
    """Test that the treemap data processing function works correctly."""
    sample_data = {
        "name": "Root",
        "count": 100,
        "children": [
            {
                "name": "Child1",
                "count": 60,
                "children": []
            },
            {
                "name": "Child2",
                "count": 40,
                "children": [
                    {
                        "name": "Grandchild",
                        "count": 20,
                        "children": []
                    }
                ]
            }
        ]
    }
    
    ids, labels, parents, values = process_data_for_treemap(sample_data)
    
    # Check lengths
    assert len(ids) == 4, "Should have 4 nodes total"
    assert len(labels) == 4, "Should have 4 labels"
    assert len(parents) == 4, "Should have 4 parent references"
    assert len(values) == 4, "Should have 4 values"
    
    # Check root node
    assert "Root" in labels, "Root node should be present"
    root_idx = labels.index("Root")
    assert parents[root_idx] == "", "Root should have empty parent"
    assert values[root_idx] == 100, "Root should have correct value"
    
    # Check child nodes
    assert "Child1" in labels, "Child1 should be present"
    assert "Child2" in labels, "Child2 should be present"
    assert "Grandchild" in labels, "Grandchild should be present"

def test_empty_children():
    """Test that nodes with empty children arrays are processed correctly."""
    data = {
        "name": "Root",
        "count": 10,
        "children": []
    }
    ids, labels, parents, values = process_data_for_treemap(data)
    assert len(ids) == 1, "Should only have root node"
    assert labels == ["Root"], "Should only have root label"
    assert parents == [""], "Root should have empty parent"
    assert values == [10], "Should have correct value"
