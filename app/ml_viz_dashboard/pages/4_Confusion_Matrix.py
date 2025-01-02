import streamlit as st
import plotly.graph_objects as go
from utils.data_validation import load_json_data, validate_confusion_matrix

st.set_page_config(page_title="Confusion Matrix", page_icon="🎯")

st.title("Confusion Matrix")
st.write("Visualize classification model performance across different classes")

# Sample data
sample_data = {
    "classes": ["Email", "Spam", "Promotion", "Social"],
    "matrix": [
        [145, 12, 8, 5],
        [10, 178, 15, 7],
        [6, 12, 156, 16],
        [4, 8, 13, 165]
    ]
}

# Data input section
st.header("Data Input")
st.write("Enter your confusion matrix data in JSON format:")
st.write("Example format:")
st.code("""
{
    "classes": ["Class1", "Class2", "Class3"],
    "matrix": [
        [10, 3, 2],
        [1, 12, 2],
        [2, 4, 15]
    ]
}
""")

# User input
json_input = st.text_area("Enter your JSON data:", height=200)
if json_input:
    loaded_data = load_json_data(json_input)
    if isinstance(loaded_data, tuple):
        st.error(loaded_data[1])
        st.stop()
    data = loaded_data
    valid, message = validate_confusion_matrix(data)
    if not valid:
        st.error(message)
        st.stop()
else:
    data = sample_data

if data is not None:
    # Create heatmap
    fig = go.Figure(data=go.Heatmap(
        z=data["matrix"],
        x=data["classes"],
        y=data["classes"],
        hoverongaps=False,
        text=[[str(val) for val in row] for row in data["matrix"]],
        texttemplate="%{text}",
        textfont={"size": 16},
        hovertemplate="Actual: %{y}<br>Predicted: %{x}<br>Count: %{text}<extra></extra>",
        colorscale=st.selectbox("Select Color Scale", 
            ["Viridis", "RdBu", "Plasma", "YlOrRd", "Hot"], 
            help="Choose the color scheme for the heatmap"
        )
    ))

    # Calculate percentages for each row (actual class)
    row_sums = [sum(row) for row in data["matrix"]]
    percentages = [[f"{(val/row_sum)*100:.1f}%" if row_sum > 0 else "0%" 
                   for val in row] 
                   for row, row_sum in zip(data["matrix"], row_sums)]

    # Add percentage annotations
    annotations = []
    for i in range(len(data["classes"])):
        for j in range(len(data["classes"])):
            annotations.append(dict(
                x=data["classes"][j],
                y=data["classes"][i],
                text=percentages[i][j],
                showarrow=False,
                font=dict(size=10),
                yshift=10
            ))

    # Update layout with enhanced features
    fig.update_layout(
        title={
            'text': "Confusion Matrix Heatmap",
            'y':0.95,
            'x':0.5,
            'xanchor': 'center',
            'yanchor': 'top'
        },
        xaxis_title="Predicted Class",
        yaxis_title="Actual Class",
        width=800,
        height=800,
        annotations=annotations,
        hoverlabel=dict(
            bgcolor="white",
            font_size=16,
            font_family="Rockwell"
        )
    )

    # Add buttons for highlighting options
    st.subheader("Highlighting Options")
    col1, col2 = st.columns(2)
    
    with col1:
        selected_actual = st.selectbox(
            "Highlight Actual Class",
            ["None"] + data["classes"],
            help="Highlight a row to see all predictions for an actual class"
        )
    
    with col2:
        selected_predicted = st.selectbox(
            "Highlight Predicted Class",
            ["None"] + data["classes"],
            help="Highlight a column to see all predictions for a predicted class"
        )

    # Apply highlighting based on selection
    if selected_actual != "None" or selected_predicted != "None":
        highlighted_cells = []
        if selected_actual != "None":
            row_idx = data["classes"].index(selected_actual)
            highlighted_cells.extend([(row_idx, j) for j in range(len(data["classes"]))])
        if selected_predicted != "None":
            col_idx = data["classes"].index(selected_predicted)
            highlighted_cells.extend([(i, col_idx) for i in range(len(data["classes"]))])
        
        # Create a mask for highlighting
        mask = [[0 for _ in row] for row in data["matrix"]]
        for i, j in highlighted_cells:
            mask[i][j] = 1
            
        # Add highlight layer
        fig.add_trace(go.Heatmap(
            z=mask,
            x=data["classes"],
            y=data["classes"],
            showscale=False,
            opacity=0.3,
            colorscale=[[0, 'rgba(0,0,0,0)'], [1, 'yellow']],
            hoverongaps=False,
            hoverinfo='skip'
        ))

    # Display plot
    st.plotly_chart(fig)

    # Calculate and display metrics
    total = sum(sum(row) for row in data["matrix"])
    correct = sum(data["matrix"][i][i] for i in range(len(data["classes"])))
    accuracy = correct / total if total > 0 else 0

    st.subheader("Summary Statistics")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Predictions", total)
    with col2:
        st.metric("Correct Predictions", correct)
    with col3:
        st.metric("Accuracy", f"{accuracy:.2%}")

    # Display raw data
    with st.expander("View Raw Data"):
        st.json(data)

    # Add testing section in debug mode
    if st.checkbox("Enable Test Mode", help="Load and test various confusion matrix examples"):
        st.subheader("Test Cases")
        
        import json
        with open("data/confusion_matrix_test_cases.json", "r") as f:
            test_cases = json.load(f)
        
        test_type = st.radio("Select Test Type", ["Valid Cases", "Invalid Cases"])
        
        if test_type == "Valid Cases":
            selected_case = st.selectbox(
                "Select Test Case",
                [case["name"] for case in test_cases["valid_cases"]]
            )
            case_data = next(case["data"] for case in test_cases["valid_cases"] if case["name"] == selected_case)
        else:
            selected_case = st.selectbox(
                "Select Test Case",
                [case["name"] for case in test_cases["invalid_cases"]]
            )
            case_data = next(case["data"] for case in test_cases["invalid_cases"] if case["name"] == selected_case)
        
        if st.button("Load Test Case"):
            # Display the test case data
            st.subheader(f"Test Case: {selected_case}")
            st.json(case_data)
            
            # Validate the test case
            valid, message = validate_confusion_matrix(case_data)
            
            if valid:
                st.success(f"Validation passed: {message}")
                # Update the data for visualization
                data = case_data
                st.rerun()
            else:
                st.error(f"Validation failed: {message}")
                
            # Display validation details
            st.write("Validation Checks:")
            checks = {
                "Is dictionary": isinstance(case_data, dict),
                "Has required keys": isinstance(case_data, dict) and all(k in case_data for k in ["classes", "matrix"]),
                "Classes is list": isinstance(case_data.get("classes", None), list),
                "Matrix is list": isinstance(case_data.get("matrix", None), list),
                "At least 2 classes": isinstance(case_data.get("classes", []), list) and len(case_data.get("classes", [])) >= 2,
                "Square matrix": isinstance(case_data.get("matrix", []), list) and \
                               all(isinstance(row, list) and len(row) == len(case_data.get("classes", [])) 
                                   for row in case_data.get("matrix", [])),
                "Non-negative values": isinstance(case_data.get("matrix", []), list) and \
                                     all(isinstance(val, (int, float)) and val >= 0 
                                         for row in case_data.get("matrix", []) for val in row)
            }
            for check, result in checks.items():
                st.write(f"- {check}: {'✅' if result else '❌'}")
