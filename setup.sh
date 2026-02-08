#!/bin/bash
# Setup script for Menu Lens

# Create virtual environment
echo "Creating virtual environment..."
python -m venv venv

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

echo "Setup complete!"
echo "Add your .env file with API keys before running the app."
echo "To run: source venv/bin/activate && streamlit run app.py"
