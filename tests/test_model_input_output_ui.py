import pytest
from pathlib import Path
import json
import sys

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

def test_load_sample_data():
    """Test loading sample data from JSON file."""
    sample_data_path = project_root / "data" / "model_input_output_sample.json"
    assert sample_data_path.exists(), "Sample data file should exist"
    
    with open(sample_data_path, "r") as f:
        data = json.load(f)
    
    # Verify data structure
    assert "nodes" in data, "Data should contain nodes"
    assert "links" in data, "Data should contain links"
    assert len(data["nodes"]) >= 2, "Should have at least 2 nodes"
    assert len(data["links"]) >= 1, "Should have at least 1 link"

def test_sankey_diagram_creation():
    """Test Sankey diagram creation with sample data."""
    import sys
    from pathlib import Path
    
    # Add pages directory to Python path
    pages_dir = project_root / "pages"
    if str(pages_dir) not in sys.path:
        sys.path.insert(0, str(pages_dir))
    
    # Import the module directly
    from fifteen_Model_Input_Output_Distribution import create_sankey_diagram
    
    # Load sample data
    with open(project_root / "data" / "model_input_output_sample.json", "r") as f:
        data = json.load(f)
    
    # Create diagram
    fig = create_sankey_diagram(data)
    
    # Verify figure properties
    assert fig.layout.title.text == "Model Input/Output Distribution"
    assert fig.layout.height == 600
    
    # Verify Sankey data
    sankey_trace = fig.data[0]
    assert sankey_trace.type == "sankey"
    
    # Verify nodes
    assert len(sankey_trace.node.label) == len(data["nodes"])
    assert all(isinstance(label, str) for label in sankey_trace.node.label)
    
    # Verify links
    assert len(sankey_trace.link.source) == len(data["links"])
    assert len(sankey_trace.link.target) == len(data["links"])
    assert len(sankey_trace.link.value) == len(data["links"])

def test_data_flow_statistics():
    """Test calculation of data flow statistics."""
    sample_data = {
        "nodes": [
            {"id": 0, "name": "Input"},
            {"id": 1, "name": "Hidden"},
            {"id": 2, "name": "Output"}
        ],
        "links": [
            {"source": 0, "target": 1, "value": 1000},
            {"source": 1, "target": 2, "value": 800}
        ]
    }
    
    # Calculate statistics
    total_input = sum(link["value"] for link in sample_data["links"] if link["source"] == 0)
    total_output = sum(link["value"] for link in sample_data["links"] if link["target"] == 2)
    retention_rate = (total_output / total_input * 100)
    
    # Verify calculations
    assert total_input == 1000, "Total input should be 1000"
    assert total_output == 800, "Total output should be 800"
    assert retention_rate == 80.0, "Retention rate should be 80%"

def test_filtering_functionality():
    """Test node filtering functionality."""
    import sys
    from pathlib import Path
    
    # Add pages directory to Python path
    pages_dir = project_root / "pages"
    if str(pages_dir) not in sys.path:
        sys.path.insert(0, str(pages_dir))
    
    # Import the module directly
    from fifteen_Model_Input_Output_Distribution import create_sankey_diagram
    
    # Sample data with multiple paths
    sample_data = {
        "nodes": [
            {"id": 0, "name": "Input"},
            {"id": 1, "name": "Process A"},
            {"id": 2, "name": "Process B"},
            {"id": 3, "name": "Output"}
        ],
        "links": [
            {"source": 0, "target": 1, "value": 500},
            {"source": 0, "target": 2, "value": 500},
            {"source": 1, "target": 3, "value": 400},
            {"source": 2, "target": 3, "value": 400}
        ]
    }
    
    # Create full diagram
    full_fig = create_sankey_diagram(sample_data)
    assert len(full_fig.data[0].node.label) == 4
    
    # Create filtered data (removing Process B)
    filtered_data = {
        "nodes": [node for node in sample_data["nodes"] if node["id"] != 2],
        "links": [link for link in sample_data["links"] 
                 if link["source"] != 2 and link["target"] != 2]
    }
    
    # Create filtered diagram
    filtered_fig = create_sankey_diagram(filtered_data)
    assert len(filtered_fig.data[0].node.label) == 3

def test_hover_tooltips():
    """Test hover tooltip content in Sankey diagram."""
    import sys
    from pathlib import Path
    
    # Add pages directory to Python path
    pages_dir = project_root / "pages"
    if str(pages_dir) not in sys.path:
        sys.path.insert(0, str(pages_dir))
    
    # Import the module directly
    from fifteen_Model_Input_Output_Distribution import create_sankey_diagram
    
    # Load sample data
    with open(project_root / "data" / "model_input_output_sample.json", "r") as f:
        data = json.load(f)
    
    # Create diagram
    fig = create_sankey_diagram(data)
    sankey_trace = fig.data[0]
    
    # Verify node hover template
    assert "Node:" in sankey_trace.node.hovertemplate
    assert "Total Flow:" in sankey_trace.node.hovertemplate
    
    # Verify link hover template
    assert "From:" in sankey_trace.link.hovertemplate
    assert "To:" in sankey_trace.link.hovertemplate
    assert "Flow:" in sankey_trace.link.hovertemplate
