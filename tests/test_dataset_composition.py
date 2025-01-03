import json
import sys
from pathlib import Path
import pytest
import importlib.util

# Add the parent directory to the Python path
parent_dir = str(Path(__file__).parent.parent)
sys.path.append(parent_dir)

def import_validate_data():
    """Import the validate_data function from the Dataset Composition module."""
    module_path = Path(parent_dir) / "pages" / "page23_Dataset_Composition.py"
    if not module_path.exists():
        raise ImportError(f"Module file not found: {module_path}")
    
    try:
        spec = importlib.util.spec_from_file_location(
            "dataset_composition",
            str(module_path)
        )
        if spec is None or spec.loader is None:
            raise ImportError("Failed to create module spec")
        
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        
        if not hasattr(module, 'validate_data'):
            raise ImportError("validate_data function not found in module")
        
        return module.validate_data
    except Exception as e:
        raise ImportError(f"Failed to import validate_data: {str(e)}")

# Get the validate_data function
validate_data = import_validate_data()

def load_test_cases():
    """Load test cases from the JSON file."""
    test_cases_path = Path(__file__).parent.parent / "data" / "dataset_composition_test_cases.json"
    with open(test_cases_path, 'r') as f:
        return json.load(f)

def test_valid_cases():
    """Test cases that should pass validation."""
    test_cases = load_test_cases()
    
    for case in test_cases['valid_cases']:
        is_valid, message = validate_data(case['data'])
        assert is_valid, f"Case '{case['name']}' should be valid but got error: {message}"

def test_invalid_cases():
    """Test cases that should fail validation."""
    test_cases = load_test_cases()
    
    for case in test_cases['invalid_cases']:
        is_valid, message = validate_data(case['data'])
        assert not is_valid, f"Case '{case['name']}' should be invalid"
        assert message == case['error'], f"Case '{case['name']}' expected error '{case['error']}' but got '{message}'"

def test_non_list_input():
    """Test that non-list inputs are rejected."""
    invalid_inputs = [
        None,
        42,
        "string",
        {"key": "value"},
        True
    ]
    
    for data in invalid_inputs:
        is_valid, message = validate_data(data)
        assert not is_valid
        assert message == "Data must be a list of class objects"

def test_invalid_item_type():
    """Test that non-dict items are rejected."""
    invalid_data = [
        "string",
        42,
        None
    ]
    
    is_valid, message = validate_data(invalid_data)
    assert not is_valid
    assert message == "Each item must be a dictionary"
