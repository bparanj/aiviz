import pytest
import json
import os
import sys
from pathlib import Path

# Add the parent directory to the Python path
sys.path.append(str(Path(__file__).parent.parent))

from pages.page11_Node_Influence import validate_data

def load_test_cases():
    """Load test cases from the JSON file."""
    test_file = Path(__file__).parent.parent / 'data' / 'node_influence_test_cases.json'
    with open(test_file, 'r') as f:
        return json.load(f)

test_cases = load_test_cases()

def test_valid_data():
    """Test that valid data passes validation."""
    validate_data(test_cases['valid_case'])

def test_duplicate_node_ids():
    """Test that duplicate node IDs raise an error."""
    with pytest.raises(ValueError, match="Duplicate node ID found"):
        validate_data(test_cases['duplicate_node_ids'])

def test_invalid_influence_negative():
    """Test that negative influence values raise an error."""
    with pytest.raises(ValueError, match="invalid influence value"):
        validate_data(test_cases['invalid_influence_negative'])

def test_invalid_link_reference():
    """Test that invalid link references raise an error."""
    with pytest.raises(ValueError, match="Link target .* not found in nodes"):
        validate_data(test_cases['invalid_link_reference'])

def test_missing_influence():
    """Test that missing influence field raises an error."""
    with pytest.raises(ValueError, match="missing required 'influence' field"):
        validate_data(test_cases['missing_influence'])

def test_invalid_weight():
    """Test that invalid link weight raises an error."""
    with pytest.raises(ValueError, match="Link weight must be a positive number"):
        validate_data(test_cases['invalid_weight'])
