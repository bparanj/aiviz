import pytest
from unittest.mock import MagicMock, patch
import json
from typing import Dict, List, Union, Optional, cast
import plotly.graph_objects as go
from plotly.graph_objs import Figure, Sankey
import streamlit as st
import pandas as pd
import sys
from pathlib import Path

# Add the project root to Python path
project_root = str(Path(__file__).parent.parent)
if project_root not in sys.path:
    sys.path.append(project_root)

from pages.seventeen_Error_Dropout_Tracking import create_sankey_diagram, calculate_statistics, main

@pytest.fixture
def sample_data():
    """Load sample data for testing."""
    with open("data/error_dropout_sample.json", "r") as f:
        return json.load(f)

def test_node_highlighting(sample_data):
    """Test that clicking a node highlights its connections."""
    fig = create_sankey_diagram(sample_data)
    sankey_trace = cast(Sankey, fig.data[0])
    
    # Verify that clicking behavior is configured
    assert hasattr(sankey_trace, 'node'), "Sankey trace should have node data"
    node = cast(Dict, getattr(sankey_trace, 'node', {}))
    
    # Check that node clicking is enabled
    assert node.get('clickmode') == 'event', "Node clicking should be enabled"
    
    # Verify that node style changes on click
    assert 'selectedpoints' in fig.to_dict(), "Figure should support node selection"
    
    # Check that connected links are highlighted
    assert hasattr(sankey_trace, 'link'), "Sankey trace should have link data"
    link = cast(Dict, getattr(sankey_trace, 'link', {}))
    assert 'color' in link, "Links should have color property for highlighting"

def test_hover_template_content(sample_data):
    """Test that hover templates show correct information."""
    fig = create_sankey_diagram(sample_data)
    sankey_trace = cast(Sankey, fig.data[0])
    
    # Get link data
    link = cast(Dict, getattr(sankey_trace, 'link', {}))
    hover_template = cast(str, link.get('hovertemplate', ''))
    
    # Verify hover template content
    assert "Stage:" in hover_template, "Should show stage name"
    assert "Samples:" in hover_template, "Should show sample count"
    assert "Drop Rate:" in hover_template, "Should show dropout rate"
    
    # Test hover template with actual data
    for i, value in enumerate(link.get('value', [])):
        if value > 0:
            # Format the expected hover text
            source_idx = link.get('source', [])[i]
            target_idx = link.get('target', [])[i]
            node = cast(Dict, getattr(sankey_trace, 'node', {}))
            source_label = node.get('label', [])[source_idx]
            target_label = node.get('label', [])[target_idx]
            
            # Verify that hover text includes all required information
            hover_text = hover_template.format(
                source={"label": source_label},
                target={"label": target_label},
                value=value
            )
            assert source_label in hover_text, f"Hover should show source: {source_label}"
            assert target_label in hover_text, f"Hover should show target: {target_label}"
            assert str(value) in hover_text, f"Hover should show value: {value}"
