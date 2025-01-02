import json
import os
import pytest
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from pages.decision_tree_breakdown import validate_tree_data, validate_node

# Load test cases
with open(os.path.join(os.path.dirname(__file__), '..', 'data', 'decision_tree_test_cases.json')) as f:
    TEST_CASES = json.load(f)['test_cases']

def test_valid_cases():
    """Test that valid tree structures pass validation."""
    for case_name, data in TEST_CASES['valid'].items():
        errors = validate_tree_data(data)
        assert len(errors) == 0, f"Valid case '{case_name}' failed validation with errors: {errors}"

def test_invalid_cases():
    """Test that invalid tree structures fail validation with appropriate errors."""
    for case_name, data in TEST_CASES['invalid'].items():
        errors = validate_tree_data(data)
        assert len(errors) > 0, f"Invalid case '{case_name}' should have validation errors"
        
        if case_name == 'missing_name':
            assert any('name' in err.lower() for err in errors)
        elif case_name == 'empty_condition':
            assert any('condition' in err.lower() for err in errors)
        elif case_name == 'negative_samples':
            assert any('samples' in err.lower() and 'non-negative' in err.lower() for err in errors)
        elif case_name == 'invalid_children_type':
            assert any('children' in err.lower() and 'array' in err.lower() for err in errors)
        elif case_name == 'invalid_child_object':
            assert any('child' in err.lower() and 'object' in err.lower() for err in errors)
        elif case_name == 'missing_required_in_child':
            assert any('child' in err.lower() and 'condition' in err.lower() for err in errors)

def test_node_validation():
    """Test individual node validation function."""
    # Test valid node
    valid_node = {
        "name": "Test Node",
        "condition": "X > 0",
        "samples": 100
    }
    errors = validate_node(valid_node)
    assert len(errors) == 0, "Valid node should pass validation"
    
    # Test invalid node - missing field
    invalid_node = {
        "name": "Test Node",
        "samples": 100
    }
    errors = validate_node(invalid_node)
    assert len(errors) > 0, "Node missing required field should fail validation"
    assert any('condition' in err.lower() for err in errors)
    
    # Test invalid node - wrong type
    invalid_node = {
        "name": "Test Node",
        "condition": 123,  # Should be string
        "samples": 100
    }
    errors = validate_node(invalid_node)
    assert len(errors) > 0, "Node with wrong type should fail validation"
    assert any('condition' in err.lower() and 'string' in err.lower() for err in errors)

def test_recursive_validation():
    """Test validation of nested tree structures."""
    nested_tree = {
        "name": "Root",
        "condition": "A > 0",
        "samples": 100,
        "children": [
            {
                "name": "Child",
                "condition": "B > 0",
                "samples": 50,
                "children": [
                    {
                        "name": "Grandchild",
                        "condition": "C > 0",
                        "samples": 25
                    }
                ]
            }
        ]
    }
    errors = validate_tree_data(nested_tree)
    assert len(errors) == 0, "Valid nested tree should pass validation"
    
    # Introduce error in grandchild
    nested_tree['children'][0]['children'][0]['samples'] = -1
    errors = validate_tree_data(nested_tree)
    assert len(errors) > 0, "Tree with invalid grandchild should fail validation"
    assert any('child 0' in err.lower() and 'samples' in err.lower() for err in errors)

if __name__ == '__main__':
    pytest.main([__file__])
