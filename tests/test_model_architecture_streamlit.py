import pytest
import streamlit as st
import json
from pathlib import Path
import sys
import os

# Add the project root to Python path to enable imports
project_root = str(Path(__file__).parent.parent)
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Import from the module
from pages.twenty_one_model_architecture import validate_node, process_data_for_tree, create_tree_chart

def load_test_cases():
    test_cases_path = Path(__file__).parent.parent / "data" / "model_architecture_test_cases.json"
    with open(test_cases_path, 'r') as f:
        return json.load(f)

def test_data_processing():
    """Test that data is correctly processed for visualization."""
    sample_data = {
        "name": "TestModel",
        "type": "Ensemble",
        "children": [
            {
                "name": "Layer1",
                "type": "Dense",
                "children": []
            }
        ]
    }
    
    # Process data for visualization
    processed_data = process_data_for_tree(sample_data)
    
    # Check that processed data has required fields
    assert "ids" in processed_data
    assert "labels" in processed_data
    assert "parents" in processed_data
    assert "text" in processed_data
    assert "level" in processed_data
    
    # Check that root node is processed correctly
    assert "TestModel" in processed_data["labels"]
    assert "" in processed_data["parents"]  # Root node has empty parent
    assert "Type: Ensemble" in processed_data["text"][0]

def test_tree_visualization():
    """Test that tree visualization is created correctly."""
    sample_data = {
        "name": "Root",
        "type": "Container",
        "children": [
            {
                "name": "Child1",
                "type": "Layer",
                "children": []
            }
        ]
    }
    
    fig = create_tree_chart(sample_data)
    assert fig.data[0].type == "treemap"
    assert "Root" in fig.data[0].labels
    assert "Child1" in fig.data[0].labels
    assert fig.layout.title.text == "Model Architecture Visualization"

def test_hover_text_generation():
    """Test that hover text is generated correctly."""
    sample_data = {
        "name": "TestModel",
        "type": "Neural Network",
        "children": []
    }
    
    processed_data = process_data_for_tree(sample_data)
    assert "text" in processed_data
    hover_text = processed_data["text"][0]
    assert "Type: Neural Network" in hover_text

def test_invalid_data_handling():
    """Test that invalid data is handled appropriately."""
    invalid_data = {
        "name": "",  # Empty name should raise error
        "type": "Test",
        "children": []
    }
    
    with pytest.raises(ValueError):
        validate_node(invalid_data)

def test_missing_children_handling():
    """Test handling of nodes with missing children field."""
    invalid_data = {
        "name": "Test",
        "type": "Layer"
        # Missing children field
    }
    
    with pytest.raises(ValueError):
        validate_node(invalid_data)

def test_nested_structure_processing():
    """Test processing of deeply nested structures."""
    nested_data = {
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
                        "children": []
                    }
                ]
            }
        ]
    }
    
    processed_data = process_data_for_tree(nested_data)
    
    # Check that all levels are processed
    assert len(processed_data["labels"]) == 3  # Root + Level1 + Level2
    assert len(processed_data["parents"]) == 3
    assert "Root" in processed_data["labels"]
    assert "Level1" in processed_data["labels"]
    assert "Level2" in processed_data["labels"]
    
    # Check level information
    assert processed_data["level"][0] == 0  # Root level
    assert processed_data["level"][1] == 1  # Level1
    assert processed_data["level"][2] == 2  # Level2

def test_optional_type_field():
    """Test handling of nodes without type field."""
    data_without_type = {
        "name": "TestNode",
        "children": []
    }
    
    # Should not raise error
    validate_node(data_without_type)
    
    processed_data = process_data_for_tree(data_without_type)
    assert "TestNode" in processed_data["labels"]
    assert "Type: N/A" in processed_data["text"][0]  # Check default type text
