import json
import pytest
from pathlib import Path
import streamlit as st
from streamlit.testing.v1 import AppTest

from pages.page22_Domain_Taxonomy import create_visualization, process_data_for_treemap, validate_node

def get_test_data():
    """Get test data for visualization testing."""
    return {
        "name": "All Categories",
        "count": 1000,
        "children": [
            {
                "name": "Electronics",
                "count": 400,
                "children": [
                    {"name": "Mobile Phones", "count": 250, "children": []},
                    {"name": "Laptops", "count": 150, "children": []}
                ]
            },
            {
                "name": "Books",
                "count": 300,
                "children": [
                    {"name": "Fiction", "count": 200, "children": []},
                    {"name": "Non-Fiction", "count": 100, "children": []}
                ]
            }
        ]
    }

def test_page_components():
    """Test that all required page components are present."""
    at = AppTest.from_file("../pages/page22_Domain_Taxonomy.py")
    at.run()
    
    # Check for title
    assert "Domain Taxonomy" in at.title[0].value
    
    # Check for visualization type selector
    assert at.radio is not None
    assert "Treemap" in at.radio[0].options
    assert "Sunburst" in at.radio[0].options
    assert "Collapsible Tree" in at.radio[0].options
    
    # Check for input method selector
    assert at.radio is not None
    assert "Use Sample Data" in at.radio[1].options
    assert "Paste JSON Data" in at.radio[1].options
    
    # Check for JSON input area
    assert at.text_area is not None

def test_user_input_methods():
    """Test all user input methods."""
    at = AppTest.from_file("../pages/page22_Domain_Taxonomy.py")
    at.run()
    
    # Test sample data
    at.radio[1].set_value("Use Sample Data")
    at.run()
    
    # Verify visualization through markdown output
    page_text = " ".join(str(m.value) for m in at.markdown)
    assert "visualization" in page_text.lower()
    
    # Test JSON input
    at.radio[1].set_value("Paste JSON Data")
    test_data = get_test_data()
    at.text_area[0].input(json.dumps(test_data, indent=2))
    at.run()
    
    # Verify data is displayed
    page_text = " ".join(str(m.value) for m in at.markdown)
    assert test_data["name"] in page_text
    for child in test_data["children"]:
        assert child["name"] in page_text

def test_json_input_handling():
    """Test JSON input functionality."""
    at = AppTest.from_file("../pages/page22_Domain_Taxonomy.py")
    at.run()
    
    # Select JSON input option
    at.radio[0].set_value("Paste JSON Data")
    at.run()
    
    # Input valid JSON
    test_data = get_test_data()
    at.text_area[0].input(json.dumps(test_data, indent=2))
    at.run()
    
    # Verify data display
    page_text = " ".join(str(m.value) for m in at.markdown)
    assert test_data["name"] in page_text
    for child in test_data["children"]:
        assert child["name"] in page_text

def test_invalid_json_handling():
    """Test handling of invalid JSON input."""
    at = AppTest.from_file("../pages/page22_Domain_Taxonomy.py")
    at.run()
    
    # Select JSON input option
    at.radio[0].set_value("Paste JSON Data")
    at.run()
    
    # Input invalid JSON
    at.text_area[0].input("{invalid json}")
    at.run()
    
    # Check for error message
    page_text = " ".join(str(m.value) for m in at.markdown)
    assert "error" in page_text.lower()

def test_visualization_layouts():
    """Test different visualization layout options."""
    at = AppTest.from_file("../pages/page22_Domain_Taxonomy.py")
    at.run()
    
    # Test each visualization type
    for viz_type in ["Treemap", "Sunburst", "Collapsible Tree"]:
        at.radio[0].set_value(viz_type)
        at.radio[1].set_value("Use Sample Data")
        at.run()
        
        # Verify visualization through markdown output
        page_text = " ".join(str(m.value) for m in at.markdown)
        assert "visualization" in page_text.lower()
        
        # Check visualization type-specific elements
        page_text = " ".join(str(m.value) for m in at.markdown)
        if viz_type == "Treemap":
            assert "area" in page_text.lower()
        elif viz_type == "Sunburst":
            assert "ring" in page_text.lower()
        else:  # Collapsible Tree
            assert "expand" in page_text.lower()

def test_interactive_features():
    """Test visualization interactivity for all chart types."""
    at = AppTest.from_file("../pages/page22_Domain_Taxonomy.py")
    at.run()
    
    # Test each visualization type
    for viz_type in ["Treemap", "Sunburst", "Collapsible Tree"]:
        at.radio[0].set_value(viz_type)
        at.radio[1].set_value("Use Sample Data")
        at.run()
        
        # Check for interactive elements in markdown
        page_text = " ".join(str(m.value) for m in at.markdown)
        
        
        # Common interactive features
        assert "hover" in page_text.lower()
        assert "count" in page_text.lower()
        assert "percentage" in page_text.lower()
        
        # Type-specific interactions
        if viz_type == "Treemap":
            assert "zoom" in page_text.lower()
            assert "click to focus" in page_text.lower()
        elif viz_type == "Sunburst":
            assert "click to zoom" in page_text.lower()
            assert "ring" in page_text.lower()
        else:  # Collapsible Tree
            assert "expand" in page_text.lower()
            assert "collapse" in page_text.lower()
        
        # Verify data display
        test_data = get_test_data()
        assert str(test_data["count"]) in page_text
        for child in test_data["children"]:
            assert str(child["count"]) in page_text
            
        # Test user interactions
        if viz_type != "Collapsible Tree":
            # Test JSON input
            at.radio[1].set_value("Paste JSON Data")
            at.text_area[0].input(json.dumps(test_data, indent=2))
            at.run()
            assert str(test_data["count"]) in " ".join(str(m.value) for m in at.markdown)

def test_visualization_data_processing():
    """Test data processing for all visualization types."""
    test_data = get_test_data()
    
    # Test treemap/sunburst data processing
    ids, labels, parents, values = process_data_for_treemap(test_data)
    
    # Verify basic data structure
    assert len(ids) == len(labels) == len(parents) == len(values)
    assert test_data["name"] in labels
    assert "" in parents  # Root node should have empty parent
    
    # Verify hierarchy
    for child in test_data["children"]:
        assert child["name"] in labels
        child_idx = labels.index(child["name"])
        assert parents[child_idx] == test_data["name"]
        assert values[child_idx] == child["count"]
        
        # Test nested children
        if child["children"]:
            for grandchild in child["children"]:
                assert grandchild["name"] in labels
                grandchild_idx = labels.index(grandchild["name"])
                assert parents[grandchild_idx] == child["name"]
                assert values[grandchild_idx] == grandchild["count"]
    
    # Test visualization creation for each type
    for viz_type in ["treemap", "sunburst"]:
        fig = create_visualization(test_data, viz_type)
        assert fig.data[0].type == viz_type.lower()
        assert len(fig.data[0].ids) == len(ids)
        assert "count" in fig.data[0].hovertemplate.lower()
        assert "percentage" in fig.data[0].hovertemplate.lower()
        
        # Verify color coding
        assert fig.data[0].marker.colors is not None
        assert len(set(fig.data[0].marker.colors)) > 1

def test_treemap_figure_creation():
    """Test that the treemap figure is created with correct properties."""
    test_data = get_test_data()
    ids, labels, parents, values = process_data_for_treemap(test_data)
    fig = create_visualization(test_data, "treemap")
    
    # Verify figure properties
    assert fig.data[0].type == "treemap"
    assert len(fig.data[0].ids) == len(ids)
    assert len(fig.data[0].labels) == len(labels)
    assert len(fig.data[0].parents) == len(parents)
    assert len(fig.data[0].values) == len(values)
    
    # Verify hover template
    assert "count" in fig.data[0].hovertemplate.lower()
    assert "percentage" in fig.data[0].hovertemplate.lower()

def test_error_handling():
    """Test error handling for invalid JSON input."""
    at = AppTest.from_file("../pages/page22_Domain_Taxonomy.py")
    at.run()
    
    # Select JSON paste option
    at.radio[0].set_value("Paste JSON Data")
    at.run()
    
    # Test invalid JSON
    at.text_area[0].input("{invalid json}")
    at.run()
    
    # Check for error message in markdown output
    page_text = " ".join(str(m.value) for m in at.markdown)
    assert "error" in page_text.lower()

def test_color_coding():
    """Test that the treemap uses distinct colors for categories."""
    test_data = get_test_data()
    fig = create_visualization(test_data, "treemap")
    
    # Verify color array exists and has unique values
    assert fig.data[0].marker.colors is not None
    assert len(set(fig.data[0].marker.colors)) > 1  # Should have multiple distinct colors

def test_data_validation():
    """Test data validation for domain taxonomy structure."""
    # Test valid data
    valid_data = {
        "name": "Test",
        "count": 100,
        "children": [
            {"name": "Child1", "count": 50, "children": []},
            {"name": "Child2", "count": 50, "children": []}
        ]
    }
    is_valid, message = validate_node(valid_data)
    assert is_valid is True, f"Valid data failed validation: {message}"
    
    # Test invalid data
    invalid_cases = [
        ({}, "empty object"),
        ({"name": "Test"}, "missing count"),
        ({"count": 100}, "missing name"),
        ({"name": "Test", "count": -1, "children": []}, "negative count"),
        ({"name": "Test", "count": 100, "children": None}, "invalid children type")
    ]
    
    for invalid_data, case in invalid_cases:
        is_valid, message = validate_node(invalid_data)
        assert not is_valid, f"Should fail for {case}, but validation passed with message: {message}"
