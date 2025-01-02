import json
import pytest
from pathlib import Path

def load_test_cases():
    """Load test cases from JSON file."""
    test_cases_path = Path(__file__).parent.parent / "data" / "model_input_output_test_cases.json"
    with open(test_cases_path, "r") as f:
        return json.load(f)

def validate_model_input_output_data(data):
    """Validate model input/output distribution data."""
    errors = []
    
    # Check if data contains required keys
    if not isinstance(data, dict) or not all(key in data for key in ["nodes", "links"]):
        errors.append("Data must contain 'nodes' and 'links' keys")
        return errors
    
    # Check if nodes is a list
    if not isinstance(data["nodes"], list):
        errors.append("'nodes' must be a list")
        return errors
    
    # Check if links is a list
    if not isinstance(data["links"], list):
        errors.append("'links' must be a list")
        return errors
    
    # Check minimum number of nodes
    if len(data["nodes"]) < 2:
        errors.append("At least two nodes are required (input and output)")
    
    # Check for unique node IDs
    node_ids = [node.get("id") for node in data["nodes"]]
    if len(node_ids) != len(set(node_ids)):
        errors.append("Node IDs must be unique")
    
    # Check node structure
    for node in data["nodes"]:
        if not isinstance(node, dict):
            errors.append("Each node must be a dictionary")
            continue
        if "id" not in node or "name" not in node:
            errors.append("Each node must have 'id' and 'name' fields")
    
    # Check link structure and references
    valid_node_ids = set(node_ids)
    for link in data["links"]:
        if not isinstance(link, dict):
            errors.append("Each link must be a dictionary")
            continue
        
        if not all(key in link for key in ["source", "target", "value"]):
            errors.append("Each link must have 'source', 'target', and 'value' fields")
            continue
        
        # Check if source and target nodes exist
        if link["source"] not in valid_node_ids:
            errors.append(f"Link source {link['source']} references non-existent node")
        if link["target"] not in valid_node_ids:
            errors.append(f"Link target {link['target']} references non-existent node")
        
        # Check for non-negative values
        if not isinstance(link["value"], (int, float)) or link["value"] < 0:
            errors.append("Link values must be non-negative numbers")
    
    return errors

def test_valid_data():
    """Test validation with valid data."""
    test_cases = load_test_cases()
    valid_case = test_cases["valid_case"]
    errors = validate_model_input_output_data(valid_case)
    assert len(errors) == 0, f"Valid case should have no errors, but got: {errors}"


def test_duplicate_node_ids():
    """Test validation with duplicate node IDs."""
    test_cases = load_test_cases()
    invalid_case = test_cases["invalid_cases"]["duplicate_node_ids"]
    errors = validate_model_input_output_data(invalid_case)
    assert any("unique" in error.lower() for error in errors), "Should detect duplicate node IDs"

def test_invalid_link_reference():
    """Test validation with invalid link references."""
    test_cases = load_test_cases()
    invalid_case = test_cases["invalid_cases"]["invalid_link_reference"]
    errors = validate_model_input_output_data(invalid_case)
    assert any("non-existent node" in error for error in errors), "Should detect invalid node references"

def test_negative_value():
    """Test validation with negative link values."""
    test_cases = load_test_cases()
    invalid_case = test_cases["invalid_cases"]["negative_value"]
    errors = validate_model_input_output_data(invalid_case)
    assert any("non-negative" in error.lower() for error in errors), "Should detect negative values"

def test_single_node():
    """Test validation with insufficient nodes."""
    test_cases = load_test_cases()
    invalid_case = test_cases["invalid_cases"]["single_node"]
    errors = validate_model_input_output_data(invalid_case)
    assert any("two nodes" in error.lower() for error in errors), "Should detect insufficient nodes"
