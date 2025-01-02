import json
import pytest
from pathlib import Path
import sys

# Add the project root to the Python path
project_root = str(Path(__file__).parent.parent)
if project_root not in sys.path:
    sys.path.append(project_root)

from pages.twelve_Neural_Network_Topology import validate_neural_network_data

def test_minimum_valid_network():
    """Test a minimal valid network with just input and output layers."""
    valid_data = {
        "layers": [
            {
                "layerIndex": 0,
                "layerType": "input",
                "nodes": [{"id": "in_1"}]
            },
            {
                "layerIndex": 1,
                "layerType": "output",
                "nodes": [{"id": "out_1"}]
            }
        ],
        "connections": [
            {"source": "in_1", "target": "out_1", "weight": 1.0}
        ]
    }
    is_valid, message = validate_neural_network_data(valid_data)
    assert is_valid
    assert "successful" in message.lower()

def test_complex_valid_network():
    """Test a more complex network with hidden layers."""
    valid_data = {
        "layers": [
            {
                "layerIndex": 0,
                "layerType": "input",
                "nodes": [{"id": "in_1"}, {"id": "in_2"}]
            },
            {
                "layerIndex": 1,
                "layerType": "hidden",
                "nodes": [{"id": "h1_1"}, {"id": "h1_2"}]
            },
            {
                "layerIndex": 2,
                "layerType": "output",
                "nodes": [{"id": "out_1"}]
            }
        ],
        "connections": [
            {"source": "in_1", "target": "h1_1", "weight": 0.25},
            {"source": "in_1", "target": "h1_2", "weight": 0.75},
            {"source": "in_2", "target": "h1_1", "weight": -0.35},
            {"source": "in_2", "target": "h1_2", "weight": 0.45},
            {"source": "h1_1", "target": "out_1", "weight": 1.5},
            {"source": "h1_2", "target": "out_1", "weight": -0.8}
        ]
    }
    is_valid, message = validate_neural_network_data(valid_data)
    assert is_valid
    assert "successful" in message.lower()

def test_non_sequential_layers():
    """Test that layer indices must be sequential starting from 0."""
    invalid_data = {
        "layers": [
            {
                "layerIndex": 0,
                "layerType": "input",
                "nodes": [{"id": "in_1"}]
            },
            {
                "layerIndex": 2,  # Missing index 1
                "layerType": "output",
                "nodes": [{"id": "out_1"}]
            }
        ],
        "connections": [
            {"source": "in_1", "target": "out_1", "weight": 1.0}
        ]
    }
    is_valid, message = validate_neural_network_data(invalid_data)
    assert not is_valid
    assert "sequential" in message.lower()

def test_missing_input_layer():
    """Test that network must have an input layer."""
    invalid_data = {
        "layers": [
            {
                "layerIndex": 0,
                "layerType": "hidden",
                "nodes": [{"id": "h1"}]
            },
            {
                "layerIndex": 1,
                "layerType": "output",
                "nodes": [{"id": "out_1"}]
            }
        ],
        "connections": [
            {"source": "h1", "target": "out_1", "weight": 1.0}
        ]
    }
    is_valid, message = validate_neural_network_data(invalid_data)
    assert not is_valid
    assert "input layer" in message.lower()

def test_invalid_layer_type():
    """Test that layer types must be input, hidden, or output."""
    invalid_data = {
        "layers": [
            {
                "layerIndex": 0,
                "layerType": "invalid",
                "nodes": [{"id": "in_1"}]
            }
        ],
        "connections": []
    }
    is_valid, message = validate_neural_network_data(invalid_data)
    assert not is_valid
    assert "layer type" in message.lower()

def test_duplicate_node_ids():
    invalid_data = {
        "layers": [
            {
                "layerIndex": 0,
                "nodes": [{"id": "node1"}, {"id": "node1"}]  # Duplicate ID
            }
        ],
        "connections": []
    }
    is_valid, message = validate_neural_network_data(invalid_data)
    assert not is_valid
    assert "duplicate" in message.lower()

def test_invalid_connection_order():
    """Test that connections must flow forward through layers."""
    invalid_data = {
        "layers": [
            {
                "layerIndex": 0,
                "layerType": "input",
                "nodes": [{"id": "in_1"}]
            },
            {
                "layerIndex": 1,
                "layerType": "hidden",
                "nodes": [{"id": "h1"}]
            },
            {
                "layerIndex": 2,
                "layerType": "output",
                "nodes": [{"id": "out_1"}]
            }
        ],
        "connections": [
            {"source": "h1", "target": "in_1", "weight": 1.0}  # Backward connection
        ]
    }
    is_valid, message = validate_neural_network_data(invalid_data)
    assert not is_valid
    assert "before target layer" in message.lower()

def test_invalid_connection_reference():
    """Test that connections must reference existing nodes."""
    invalid_data = {
        "layers": [
            {
                "layerIndex": 0,
                "layerType": "input",
                "nodes": [{"id": "node1"}]
            },
            {
                "layerIndex": 1,
                "layerType": "output",
                "nodes": [{"id": "node2"}]
            }
        ],
        "connections": [
            {"source": "node1", "target": "nonexistent"}  # Invalid target
        ]
    }
    is_valid, message = validate_neural_network_data(invalid_data)
    assert not is_valid
    assert "Invalid" in message

def test_invalid_weight_type():
    """Test that connection weights must be numeric."""
    invalid_data = {
        "layers": [
            {
                "layerIndex": 0,
                "layerType": "input",
                "nodes": [{"id": "node1"}]
            },
            {
                "layerIndex": 1,
                "layerType": "output",
                "nodes": [{"id": "node2"}]
            }
        ],
        "connections": [
            {"source": "node1", "target": "node2", "weight": "0.5"}  # Weight should be numeric
        ]
    }
    is_valid, message = validate_neural_network_data(invalid_data)
    assert not is_valid
    assert "weight" in message.lower()

def test_empty_data():
    """Test validation with empty data."""
    is_valid, message = validate_neural_network_data({})
    assert not is_valid
    assert "must contain" in message.lower()

def test_empty_layers():
    """Test validation with empty layers array."""
    data = {
        "layers": [],
        "connections": []
    }
    is_valid, message = validate_neural_network_data(data)
    assert not is_valid
    assert "at least 2 layers" in message.lower()

def test_empty_layer_nodes():
    """Test validation with a layer containing no nodes."""
    data = {
        "layers": [
            {
                "layerIndex": 0,
                "layerType": "input",
                "nodes": []
            },
            {
                "layerIndex": 1,
                "layerType": "output",
                "nodes": [{"id": "out_1"}]
            }
        ],
        "connections": []
    }
    is_valid, message = validate_neural_network_data(data)
    assert not is_valid
    assert "has no nodes" in message.lower()

def test_missing_required_fields():
    """Test validation with missing required fields in layers and connections."""
    data = {
        "layers": [
            {
                "layerType": "input",  # Missing layerIndex
                "nodes": [{"id": "in_1"}]
            }
        ],
        "connections": [
            {"source": "in_1"}  # Missing target
        ]
    }
    is_valid, message = validate_neural_network_data(data)
    assert not is_valid
    assert "layerIndex" in message.lower()

def test_output_layer_not_last():
    """Test that output layer must be the last layer."""
    data = {
        "layers": [
            {
                "layerIndex": 0,
                "layerType": "input",
                "nodes": [{"id": "in_1"}]
            },
            {
                "layerIndex": 1,
                "layerType": "output",
                "nodes": [{"id": "out_1"}]
            },
            {
                "layerIndex": 2,
                "layerType": "hidden",
                "nodes": [{"id": "h1"}]
            }
        ],
        "connections": []
    }
    is_valid, message = validate_neural_network_data(data)
    assert not is_valid
    assert "output layer must be the last layer" in message.lower()
