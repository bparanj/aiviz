import json
import pytest
from pathlib import Path
import sys

# Add the project root to the Python path
project_root = str(Path(__file__).parent.parent)
if project_root not in sys.path:
    sys.path.append(project_root)

from pages.twelve_Neural_Network_Topology import validate_neural_network_data

def test_valid_neural_network_data():
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
    assert "Valid" in message

def test_invalid_layer_index():
    invalid_data = {
        "layers": [
            {
                "layerIndex": "0",  # Should be numeric
                "layerType": "input",
                "nodes": [{"id": "in_1"}]
            }
        ],
        "connections": []
    }
    is_valid, message = validate_neural_network_data(invalid_data)
    assert not is_valid
    assert "layerIndex" in message

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

def test_invalid_connection_reference():
    invalid_data = {
        "layers": [
            {
                "layerIndex": 0,
                "nodes": [{"id": "node1"}]
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
    invalid_data = {
        "layers": [
            {
                "layerIndex": 0,
                "nodes": [{"id": "node1"}]
            },
            {
                "layerIndex": 1,
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
