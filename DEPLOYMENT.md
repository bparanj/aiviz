# Deploying to Streamlit Cloud

Follow these steps to deploy the ML Visualization Dashboard to Streamlit Cloud:

1. **Create a GitHub Repository**
   - Create a new public repository on GitHub
   - Push the code to your repository:
     ```bash
     git remote add origin https://github.com/YOUR_USERNAME/streamlit-ml-viz.git
     git push -u origin master
     ```

2. **Sign up for Streamlit Cloud**
   - Go to [share.streamlit.io](https://share.streamlit.io)
   - Sign in with your GitHub account

3. **Deploy Your App**
   - Click "New app" in Streamlit Cloud
   - Select your repository and branch
   - Set the main file path to: `app.py`
   - Click "Deploy"

4. **Verify Installation**
   - Streamlit Cloud will automatically install dependencies from `requirements.txt`
   - The app will be available at: `https://YOUR_APP_NAME.streamlit.app`

5. **Update the App**
   - Any changes pushed to your GitHub repository will automatically trigger a new deployment

## Requirements
All required packages are listed in `requirements.txt` and will be automatically installed by Streamlit Cloud.

## Features
The deployed app includes:
- Hyperparameter Impact Visualization
- Dataset Variations Visualization
- Correlation Matrix Visualization
- Confusion Matrix Visualization
- Custom data input via JSON for each visualization
- Interactive features and comprehensive data validation

## Troubleshooting
- Make sure all files are committed and pushed to GitHub
- Check that `requirements.txt` contains all necessary dependencies
- Verify that the repository is public
- Ensure `app.py` is in the root directory
