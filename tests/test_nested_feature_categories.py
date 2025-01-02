import json
import os
import pytest
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from pages.twenty_nested_feature_categories import validate_node

def load_test_cases():
    """Load test cases from JSON file."""
    test_cases_path = os.path.join(
        os.path.dirname(os.path.dirname(__file__)),
        "data",
        "nested_feature_categories_test_cases.json"
    )
    with open(test_cases_path, 'r') as f:
        return json.load(f)

def test_valid_cases():
    """Test that valid data structures pass validation."""
    test_cases = load_test_cases()
    
    for case in test_cases['valid_cases']:
        errors = validate_node(case['data'], is_root=True)
        assert len(errors) == 0, f"Valid case '{case['description']}' failed validation with errors: {errors}"

def test_invalid_cases():
    """Test that invalid data structures fail validation with expected errors."""
    test_cases = load_test_cases()
    
    for case in test_cases['invalid_cases']:
        errors = validate_node(case['data'], is_root=True)
        assert len(errors) > 0, f"Invalid case '{case['description']}' passed validation when it should have failed"
        
        # Check that all expected errors are present
        for expected_error in case['expected_errors']:
            assert any(expected_error in error for error in errors), \
                f"Expected error '{expected_error}' not found in validation errors for case '{case['description']}'"

def test_minimum_node_requirement():
    """Test that data must have at least one root node."""
    data = {}  # Empty data
    errors = validate_node(data, is_root=True)
    assert len(errors) > 0, "Empty data should fail validation"
    assert any("must have a non-empty string name" in error for error in errors)

def test_hierarchy_consistency():
    """Test that child counts cannot exceed parent count."""
    data = {
        "name": "Parent",
        "count": 5,
        "children": [
            {
                "name": "Child 1",
                "count": 3,
                "children": []
            },
            {
                "name": "Child 2",
                "count": 3,
                "children": []
            }
        ]
    }
    errors = validate_node(data, is_root=True)
    assert len(errors) > 0, "Total child count exceeding parent count should fail validation"
    assert any("less than sum of children" in error for error in errors)

def test_name_validation():
    """Test various invalid name scenarios."""
    test_cases = [
        ({"name": "", "count": 0, "children": []}, "empty string"),
        ({"name": " ", "count": 0, "children": []}, "whitespace only"),
        ({"name": None, "count": 0, "children": []}, "None"),
        ({"name": 123, "count": 0, "children": []}, "non-string"),
    ]
    
    for data, case_desc in test_cases:
        errors = validate_node(data, is_root=True)
        assert len(errors) > 0, f"Name validation should fail for {case_desc}"
        assert any("must have a non-empty string name" in error for error in errors)

def test_count_validation():
    """Test various invalid count scenarios."""
    test_cases = [
        ({"name": "Test", "count": -1, "children": []}, "negative"),
        ({"name": "Test", "count": "0", "children": []}, "string"),
        ({"name": "Test", "count": None, "children": []}, "None"),
        ({"name": "Test", "count": 1.5, "children": []}, "float"),
    ]
    
    for data, case_desc in test_cases:
        errors = validate_node(data, is_root=True)
        assert len(errors) > 0, f"Count validation should fail for {case_desc}"
        assert any("must have a non-negative integer count" in error for error in errors)

def test_children_validation():
    """Test various invalid children scenarios."""
    test_cases = [
        ({"name": "Test", "count": 0, "children": None}, "None children"),
        ({"name": "Test", "count": 0, "children": "not a list"}, "string children"),
        ({"name": "Test", "count": 0, "children": 42}, "number children"),
        ({"name": "Test", "count": 0, "children": {}}, "dict children"),
    ]
    
    for data, case_desc in test_cases:
        errors = validate_node(data, is_root=True)
        assert len(errors) > 0, f"Children validation should fail for {case_desc}"
        assert any("children must be an array" in error for error in errors)
