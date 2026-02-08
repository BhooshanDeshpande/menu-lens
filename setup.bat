@echo off
REM Setup script for Menu Lens (Windows)

REM Create virtual environment
echo Creating virtual environment...
python -m venv venv

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate

REM Install dependencies
echo Installing dependencies...
pip install --upgrade pip
pip install -r requirements.txt

echo Setup complete!
echo Add your .env file with API keys before running the app.
echo To run: call venv\Scripts\activate && streamlit run app.py
