import json
import pytest
from pathlib import Path
import sys
import os

# Add the parent directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pages.twenty_one_model_architecture import validate_node

def load_test_cases():
    test_cases_path = Path(__file__).parent.parent / "data" / "model_architecture_test_cases.json"
    with open(test_cases_path, 'r') as f:
        return json.load(f)

test_cases = load_test_cases()

@pytest.mark.parametrize(
    "test_case",
    test_cases["valid_cases"],
    ids=[case["name"] for case in test_cases["valid_cases"]]
)
def test_valid_cases(test_case):
    """Test that valid model architectures pass validation."""
    try:
        validate_node(test_case["data"])
    except ValueError as e:
        pytest.fail(f"Validation failed for valid case '{test_case['name']}': {str(e)}")

@pytest.mark.parametrize(
    "test_case",
    test_cases["invalid_cases"],
    ids=[case["name"] for case in test_cases["invalid_cases"]]
)
def test_invalid_cases(test_case):
    """Test that invalid model architectures fail validation with correct error messages."""
    with pytest.raises(ValueError) as exc_info:
        validate_node(test_case["data"])
    assert str(exc_info.value) == test_case["expected_error"], \
        f"Expected error '{test_case['expected_error']}' but got '{str(exc_info.value)}'"

def test_nested_validation():
    """Test validation of deeply nested structures."""
    deep_nested = {
        "name": "Root",
        "type": "Container",
        "children": [
            {
                "name": "Level1",
                "type": "Layer",
                "children": [
                    {
                        "name": "Level2",
                        "type": "Component",
                        "children": [
                            {
                                "name": "Level3",
                                "type": "Leaf",
                                "children": []
                            }
                        ]
                    }
                ]
            }
        ]
    }
    validate_node(deep_nested)  # Should not raise any exceptions

def test_multiple_children():
    """Test validation of nodes with multiple children."""
    multiple_children = {
        "name": "Parent",
        "type": "Container",
        "children": [
            {"name": "Child1", "type": "Layer", "children": []},
            {"name": "Child2", "type": "Layer", "children": []},
            {"name": "Child3", "type": "Layer", "children": []}
        ]
    }
    validate_node(multiple_children)  # Should not raise any exceptions

def test_empty_children():
    """Test validation of nodes with empty children arrays."""
    empty_children = {
        "name": "Leaf",
        "type": "Terminal",
        "children": []
    }
    validate_node(empty_children)  # Should not raise any exceptions
