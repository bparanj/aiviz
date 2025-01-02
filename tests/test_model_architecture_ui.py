import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import json
from pathlib import Path

def test_page_title(selenium):
    """Test that the page title is correctly displayed."""
    selenium.get("http://localhost:8501/Model_Architecture")
    title = WebDriverWait(selenium, 10).until(
        EC.presence_of_element_located((By.TAG_NAME, "h1"))
    )
    assert "Model Architecture Visualization" in title.text

def test_sample_data_loading(selenium):
    """Test that sample data loads and displays correctly."""
    selenium.get("http://localhost:8501/Model_Architecture")
    
    # Select sample data option
    radio = WebDriverWait(selenium, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, 'input[value="Use Sample Data"]'))
    )
    radio.click()
    
    # Check that the plot is rendered
    plot = WebDriverWait(selenium, 10).until(
        EC.presence_of_element_located((By.CLASS_NAME, "js-plotly-plot"))
    )
    assert plot.is_displayed()

def test_json_input(selenium):
    """Test JSON input functionality."""
    selenium.get("http://localhost:8501/Model_Architecture")
    
    # Select JSON input option
    radio = WebDriverWait(selenium, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, 'input[value="Paste JSON"]'))
    )
    radio.click()
    
    # Load sample JSON
    sample_path = Path(__file__).parent.parent / "data" / "model_architecture_sample.json"
    with open(sample_path, 'r') as f:
        sample_json = json.load(f)
    
    # Find and fill the text area
    textarea = WebDriverWait(selenium, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, 'textarea'))
    )
    textarea.send_keys(json.dumps(sample_json, indent=2))
    
    # Check that the plot is rendered
    plot = WebDriverWait(selenium, 10).until(
        EC.presence_of_element_located((By.CLASS_NAME, "js-plotly-plot"))
    )
    assert plot.is_displayed()

def test_invalid_json_input(selenium):
    """Test error handling for invalid JSON input."""
    selenium.get("http://localhost:8501/Model_Architecture")
    
    # Select JSON input option
    radio = WebDriverWait(selenium, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, 'input[value="Paste JSON"]'))
    )
    radio.click()
    
    # Input invalid JSON
    textarea = WebDriverWait(selenium, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, 'textarea'))
    )
    textarea.send_keys('{"invalid": "json"')
    
    # Check for error message
    error = WebDriverWait(selenium, 10).until(
        EC.presence_of_element_located((By.CLASS_NAME, "stError"))
    )
    assert "Invalid JSON format" in error.text

def test_treemap_interaction(selenium):
    """Test treemap interaction features."""
    selenium.get("http://localhost:8501/Model_Architecture")
    
    # Load sample data
    radio = WebDriverWait(selenium, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, 'input[value="Use Sample Data"]'))
    )
    radio.click()
    
    # Wait for plot to render
    plot = WebDriverWait(selenium, 10).until(
        EC.presence_of_element_located((By.CLASS_NAME, "js-plotly-plot"))
    )
    
    # Check that plot is interactive (has modebar)
    modebar = WebDriverWait(selenium, 10).until(
        EC.presence_of_element_located((By.CLASS_NAME, "modebar-container"))
    )
    assert modebar.is_displayed()

def test_instructions_display(selenium):
    """Test that usage instructions are displayed."""
    selenium.get("http://localhost:8501/Model_Architecture")
    
    # Check for instructions section
    instructions = WebDriverWait(selenium, 10).until(
        EC.presence_of_element_located((By.TAG_NAME, "h3"))
    )
    assert "Instructions" in instructions.text
    
    # Verify instruction content
    instruction_text = selenium.find_element(By.XPATH, "//h3[contains(text(),'Instructions')]/following-sibling::*")
    assert "Click" in instruction_text.text
    assert "zoom" in instruction_text.text.lower()
    assert "hover" in instruction_text.text.lower()

def test_raw_data_view(selenium):
    """Test raw data view functionality."""
    selenium.get("http://localhost:8501/Model_Architecture")
    
    # Load sample data
    radio = WebDriverWait(selenium, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, 'input[value="Use Sample Data"]'))
    )
    radio.click()
    
    # Find and click expander
    expander = WebDriverWait(selenium, 10).until(
        EC.presence_of_element_located((By.XPATH, "//div[contains(text(),'View Raw Data')]"))
    )
    expander.click()
    
    # Check that raw data is displayed
    raw_data = WebDriverWait(selenium, 10).until(
        EC.presence_of_element_located((By.CLASS_NAME, "stJson"))
    )
    assert raw_data.is_displayed()
