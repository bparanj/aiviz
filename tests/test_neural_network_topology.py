import json
import pytest
from pathlib import Path
import sys

# Add the project root to the Python path
project_root = str(Path(__file__).parent.parent)
if project_root not in sys.path:
    sys.path.append(project_root)

from utils.data_validation import validate_neural_network_topology

def test_minimum_valid_tree():
    """Test a minimal valid tree with a single node."""
    valid_data = {
        "name": "SimpleModel",
        "type": "NeuralNetwork",
        "children": []
    }
    is_valid, message = validate_neural_network_topology(valid_data)
    assert is_valid
    assert "valid" in message.lower()

def test_complex_valid_tree():
    """Test a complex tree with multiple levels and node types."""
    valid_data = {
        "name": "EnsembleModel",
        "type": "Ensemble",
        "children": [
            {
                "name": "RandomForestModule",
                "type": "RandomForest",
                "children": [
                    {
                        "name": "DecisionTree1",
                        "type": "DecisionTree",
                        "children": []
                    },
                    {
                        "name": "DecisionTree2",
                        "type": "DecisionTree",
                        "children": []
                    }
                ]
            },
            {
                "name": "NeuralNetworkModule",
                "type": "NeuralNetwork",
                "children": [
                    {
                        "name": "ConvLayer1",
                        "type": "ConvolutionalLayer",
                        "children": []
                    },
                    {
                        "name": "DenseLayer1",
                        "type": "DenseLayer",
                        "children": []
                    }
                ]
            }
        ]
    }
    is_valid, message = validate_neural_network_topology(valid_data)
    assert is_valid
    assert "valid" in message.lower()

def test_missing_name():
    """Test that each node must have a name."""
    invalid_data = {
        "type": "NeuralNetwork",
        "children": []
    }
    is_valid, message = validate_neural_network_topology(invalid_data)
    assert not is_valid
    assert "name" in message.lower()

def test_missing_children():
    """Test that each node must have a children array."""
    invalid_data = {
        "name": "Model",
        "type": "NeuralNetwork"
    }
    is_valid, message = validate_neural_network_topology(invalid_data)
    assert not is_valid
    assert "children" in message.lower()

def test_invalid_children_type():
    """Test that children must be a list."""
    invalid_data = {
        "name": "Model",
        "type": "NeuralNetwork",
        "children": "not a list"
    }
    is_valid, message = validate_neural_network_topology(invalid_data)
    assert not is_valid
    assert "list" in message.lower()

def test_optional_type_field():
    """Test that type field is optional."""
    valid_data = {
        "name": "SimpleModel",
        "children": []
    }
    is_valid, message = validate_neural_network_topology(valid_data)
    assert is_valid
    assert "valid" in message.lower()

def test_empty_name():
    """Test that name cannot be empty."""
    invalid_data = {
        "name": "",
        "type": "NeuralNetwork",
        "children": []
    }
    is_valid, message = validate_neural_network_topology(invalid_data)
    assert not is_valid
    assert "empty" in message.lower()

def test_invalid_name_type():
    """Test that name must be a string."""
    invalid_data = {
        "name": 123,
        "type": "NeuralNetwork",
        "children": []
    }
    is_valid, message = validate_neural_network_topology(invalid_data)
    assert not is_valid
    assert "string" in message.lower()

def test_invalid_type_type():
    """Test that type must be a string if provided."""
    invalid_data = {
        "name": "Model",
        "type": 123,
        "children": []
    }
    is_valid, message = validate_neural_network_topology(invalid_data)
    assert not is_valid
    assert "string" in message.lower()

def test_nested_validation():
    """Test that validation checks all nested children."""
    invalid_data = {
        "name": "Model",
        "type": "Ensemble",
        "children": [
            {
                "name": "SubModel",
                "type": "NeuralNetwork",
                "children": [
                    {
                        "type": "Layer",  # Missing name
                        "children": []
                    }
                ]
            }
        ]
    }
    is_valid, message = validate_neural_network_topology(invalid_data)
    assert not is_valid
    assert "name" in message.lower()

def test_invalid_node_structure():
    """Test that nodes must have valid structure."""
    invalid_data = {
        "name": "Model",
        "type": "NeuralNetwork",
        "children": [
            {
                "name": "Layer1",
                "type": "Layer",
                "invalid_field": "value",  # Invalid field
                "children": []
            }
        ]
    }
    is_valid, message = validate_neural_network_topology(invalid_data)
    assert not is_valid
    assert "structure" in message.lower()

def test_empty_data():
    """Test validation with empty data."""
    is_valid, message = validate_neural_network_topology({})
    assert not is_valid
    assert "missing required field" in message.lower()

def test_duplicate_names():
    """Test that sibling nodes cannot have duplicate names."""
    invalid_data = {
        "name": "Model",
        "type": "Ensemble",
        "children": [
            {
                "name": "Layer1",
                "children": []
            },
            {
                "name": "Layer1",  # Duplicate name
                "children": []
            }
        ]
    }
    is_valid, message = validate_neural_network_topology(invalid_data)
    assert not is_valid
    assert "duplicate" in message.lower()

def test_max_depth():
    """Test that the tree doesn't exceed maximum allowed depth."""
    deep_data = {
        "name": "Level1",
        "children": [{
            "name": "Level2",
            "children": [{
                "name": "Level3",
                "children": [{
                    "name": "Level4",
                    "children": [{
                        "name": "Level5",
                        "children": [{
                            "name": "Level6",
                            "children": []
                        }]
                    }]
                }]
            }]
        }]
    }
    is_valid, message = validate_neural_network_topology(deep_data)
    assert not is_valid
    assert "depth" in message.lower()

def test_invalid_children_structure():
    """Test that children must be properly structured."""
    invalid_data = {
        "name": "Model",
        "type": "NeuralNetwork",
        "children": [
            "not an object",  # Invalid child structure
            {
                "name": "Layer1",
                "children": []
            }
        ]
    }
    is_valid, message = validate_neural_network_topology(invalid_data)
    assert not is_valid
    assert "invalid structure" in message.lower()

def test_circular_reference():
    """Test that circular references are not allowed."""
    # Note: This is a theoretical test as the JSON structure inherently prevents cycles
    invalid_data = {
        "name": "Model",
        "type": "NeuralNetwork",
        "children": [
            {
                "name": "Layer1",
                "children": [
                    {
                        "name": "Layer2",
                        "children": []
                    }
                ]
            }
        ]
    }
    is_valid, message = validate_neural_network_topology(invalid_data)
    assert is_valid  # Should pass as there's no way to create actual circular references in JSON
