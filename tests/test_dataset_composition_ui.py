import sys
from pathlib import Path
import pytest
import streamlit as st
from streamlit.testing.v1 import AppTest
import json
import time

# Add the parent directory to the Python path
parent_dir = str(Path(__file__).parent.parent)
sys.path.append(parent_dir)

def wait_for_render(at):
    """Wait for the app to render."""
    time.sleep(2)  # Give more time for components to render and session state to update
    at.rerun()  # Force a rerun to ensure state is updated
    time.sleep(1)  # Wait for rerun to complete

def test_chart_type_selection():
    """Test that users can switch between bar and pie charts."""
    at = AppTest.from_file(str(Path(parent_dir) / "pages" / "23_Dataset_Composition.py"))
    at.run()
    
    # Check if chart type radio buttons are present
    assert at.radio(key="dataset_composition_chart_type").value in ["Bar Chart", "Pie Chart"]

def test_data_input_methods():
    """Test different data input methods."""
    at = AppTest.from_file(str(Path(parent_dir) / "pages" / "23_Dataset_Composition.py"))
    at.run()
    
    # Check if input method radio buttons are present
    assert at.radio(key="dataset_composition_input_method").value in [
        "Use sample data",
        "Upload JSON file",
        "Paste JSON data"
    ]

def test_sorting_options():
    """Test sorting functionality for bar chart."""
    at = AppTest.from_file(str(Path(parent_dir) / "pages" / "23_Dataset_Composition.py"))
    at.run()
    wait_for_render(at)
    
    # Select sample data first
    input_method = at.radio(key="dataset_composition_input_method")
    assert input_method is not None, "Input method radio button not found"
    input_method.set_value("Use sample data")
    wait_for_render(at)
    
    # Select bar chart
    chart_type = at.radio(key="dataset_composition_chart_type")
    assert chart_type is not None, "Chart type radio button not found"
    chart_type.set_value("Bar Chart")
    wait_for_render(at)
    
    # Check if sorting options are present and can be selected
    sort_order = at.selectbox(key="dataset_composition_sort_order")
    assert sort_order is not None, "Sort order selectbox not found"
    
    # Test each sorting option
    for option in ["Original", "Ascending", "Descending"]:
        sort_order.set_value(option)
        wait_for_render(at)
        assert sort_order.value == option, f"Sort order not set to {option}"
        
        # Verify chart updates after sorting
        assert "dataset_composition_chart" in at.session_state, f"Chart not updated after sorting to {option}"
        assert "dataset_composition_sorted_data" in at.session_state, f"Sorted data not in session state for {option}"

def test_data_validation():
    """Test data validation for JSON input."""
    at = AppTest.from_file(str(Path(parent_dir) / "pages" / "23_Dataset_Composition.py"))
    at.run()
    wait_for_render(at)
    
    # Select JSON paste option
    input_method = at.radio(key="dataset_composition_input_method")
    input_method.set_value("Paste JSON data")
    wait_for_render(at)
    
    text_input = at.text_area(key="dataset_composition_text_input")
    assert text_input is not None, "Text area not found"
    
    # Test missing required fields
    invalid_json = '[{"count": 50}]'  # Missing class field
    text_input.set_value(invalid_json)
    wait_for_render(at)
    assert "dataset_composition_error" in at.session_state, "No error for missing class field"
    
    # Test invalid count type
    invalid_json = '[{"class": "Dog", "count": "50"}]'  # Count should be number
    text_input.set_value(invalid_json)
    wait_for_render(at)
    assert "dataset_composition_error" in at.session_state, "No error for invalid count type"
    
    # Test negative count
    invalid_json = '[{"class": "Dog", "count": -1}]'
    text_input.set_value(invalid_json)
    wait_for_render(at)
    assert "dataset_composition_error" in at.session_state, "No error for negative count"
    
    # Test empty class name
    invalid_json = '[{"class": "", "count": 50}]'
    text_input.set_value(invalid_json)
    wait_for_render(at)
    assert "dataset_composition_error" in at.session_state, "No error for empty class name"
    
    # Test too few entries
    invalid_json = '[{"class": "Dog", "count": 50}]'  # Only one entry
    text_input.set_value(invalid_json)
    wait_for_render(at)
    assert "dataset_composition_error" in at.session_state, "No error for too few entries"

def test_sample_data_loading():
    """Test that sample data is loaded and displayed correctly."""
    at = AppTest.from_file(str(Path(parent_dir) / "pages" / "23_Dataset_Composition.py"))
    at.run()
    wait_for_render(at)
    
    # Select sample data option
    input_method = at.radio(key="dataset_composition_input_method")
    assert input_method is not None, "Input method radio button not found"
    input_method.set_value("Use sample data")
    wait_for_render(at)
    
    # Check if chart type selector exists and both options work
    chart_type = at.radio(key="dataset_composition_chart_type")
    assert chart_type is not None, "Chart type selector not found"
    
    # Test bar chart
    chart_type.set_value("Bar Chart")
    wait_for_render(at)
    assert chart_type.value == "Bar Chart", "Bar chart not selected"
    assert "dataset_composition_chart" in at.session_state, "Bar chart not rendered"
    
    # Test pie chart
    chart_type.set_value("Pie Chart")
    wait_for_render(at)
    assert chart_type.value == "Pie Chart", "Pie chart not selected"
    assert "dataset_composition_chart" in at.session_state, "Pie chart not rendered"

def test_interactive_features():
    """Test interactive features like tooltips and highlighting."""
    at = AppTest.from_file(str(Path(parent_dir) / "pages" / "23_Dataset_Composition.py"))
    at.run()
    wait_for_render(at)
    
    # Initialize session state
    at.session_state["dataset_composition_input_method"] = "Use sample data"
    at.session_state["dataset_composition_chart_type"] = "Bar Chart"
    at.session_state["dataset_composition_highlight"] = None
    at.session_state["dataset_composition_tooltip"] = None
    wait_for_render(at)
    
    # Select bar chart
    chart_type = at.radio(key="dataset_composition_chart_type")
    chart_type.set_value("Bar Chart")
    wait_for_render(at)
    
    # Verify tooltips are initialized
    assert "dataset_composition_tooltip" in at.session_state, "Tooltips not enabled"
    
    # Test highlighting functionality
    assert "dataset_composition_highlight" in at.session_state, "Highlighting not enabled"
    assert at.session_state["dataset_composition_highlight"] is None, "Initial highlight should be None"
    
    # Find and click the highlight button for each class
    sample_data = at.session_state.get("dataset_composition_data", [])
    for item in sample_data:
        class_name = item["class"]
        highlight_button = at.button(key=f"highlight_{class_name}")
        assert highlight_button is not None, f"Highlight button not found for {class_name}"
        highlight_button.click()
        wait_for_render(at)
        
        # Verify highlighting worked
        assert at.session_state["dataset_composition_highlight"] == class_name, f"Highlighting not working for {class_name}"
        assert at.session_state["dataset_composition_tooltip"] is not None, "Tooltip should be set after highlight"
        
        # Test tooltip data format
        tooltip_data = at.session_state.get("dataset_composition_tooltip", {})
        assert "class" in tooltip_data, "Tooltip missing class information"
        assert "count" in tooltip_data, "Tooltip missing count information"
        assert isinstance(tooltip_data["count"], (int, float)), "Invalid count type in tooltip"
        assert tooltip_data["class"] == class_name, f"Wrong class in tooltip for {class_name}"

def test_invalid_json_input():
    """Test handling of invalid JSON input."""
    at = AppTest.from_file(str(Path(parent_dir) / "pages" / "23_Dataset_Composition.py"))
    at.run()
    wait_for_render(at)
    
    # Initialize session state for JSON input
    at.session_state["dataset_composition_input_method"] = "Paste JSON data"
    at.session_state["dataset_composition_text_input"] = ""
    wait_for_render(at)
    
    # Test various invalid inputs
    test_cases = [
        ("invalid json", "Invalid JSON format"),
        ("[{]", "Invalid JSON format"),
        ("[]", "At least one class is required"),
        ('[{"wrong": "value"}]', "Each item must have a non-empty class name"),
        ('[{"class": "", "count": 50}]', "Each item must have a non-empty class name"),
        ('[{"class": "Dog", "count": "50"}]', "Each item must have a non-negative count"),
        ('[{"class": "Dog", "count": -1}]', "Each item must have a non-negative count"),
        ('[{"class": 123, "count": 50}]', "Each item must have a non-empty class name")
    ]
    
    for invalid_input, expected_error in test_cases:
        at.session_state["dataset_composition_text_input"] = invalid_input
        wait_for_render(at)
        
        # Check if error message is displayed
        assert "dataset_composition_error" in at.session_state, f"No error state set for input: {invalid_input}"
        assert at.session_state["dataset_composition_error"] is not None, f"No error message for input: {invalid_input}"
        
    # Test valid input clears error
    valid_input = '[{"class": "Dog", "count": 50}]'
    at.session_state["dataset_composition_text_input"] = valid_input
    wait_for_render(at)
    assert at.session_state["dataset_composition_error"] is None, "Error not cleared for valid input"

def test_chart_visualization():
    """Test chart visualization properties."""
    at = AppTest.from_file(str(Path(parent_dir) / "pages" / "23_Dataset_Composition.py"))
    at.run()
    wait_for_render(at)
    
    # Initialize session state
    at.session_state["dataset_composition_input_method"] = "Use sample data"
    at.session_state["dataset_composition_chart_type"] = "Bar Chart"
    wait_for_render(at)
    
    # Test bar chart
    chart_type = at.radio(key="dataset_composition_chart_type")
    chart_type.set_value("Bar Chart")
    wait_for_render(at)
    
    # Verify bar chart properties
    chart = at.session_state.get("dataset_composition_chart")
    assert chart is not None, "Bar chart not created"
    
    # Check bar chart layout
    layout = chart.layout
    assert layout.xaxis.title.text == "Class", "X-axis title incorrect"
    assert layout.yaxis.title.text == "Count", "Y-axis title incorrect"
    
    # Check bar chart data
    data = chart.data[0]
    assert data.type == "bar", "Chart type is not bar"
    assert len(data.x) > 0, "No class names on x-axis"
    assert len(data.y) > 0, "No count values on y-axis"
    assert all(isinstance(y, (int, float)) for y in data.y), "Invalid count values"
    
    # Test pie chart
    chart_type.set_value("Pie Chart")
    wait_for_render(at)
    
    # Verify pie chart properties
    chart = at.session_state.get("dataset_composition_chart")
    assert chart is not None, "Pie chart not created"
    
    # Check pie chart data
    data = chart.data[0]
    assert data.type == "pie", "Chart type is not pie"
    assert len(data.labels) > 0, "No class labels in pie chart"
    assert len(data.values) > 0, "No count values in pie chart"
    assert all(isinstance(v, (int, float)) for v in data.values), "Invalid count values"
    
    # Verify total percentage adds up to 100%
    total = sum(data.values)
    percentages = [v/total * 100 for v in data.values]
    assert abs(sum(percentages) - 100) < 0.01, "Pie chart percentages don't add up to 100%"

if __name__ == "__main__":
    pytest.main([__file__])
