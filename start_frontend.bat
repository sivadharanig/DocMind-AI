@echo off
echo Starting Streamlit Presentation Tier on port 8501...
python -m streamlit run frontend\app.py --server.port 8501
pause
