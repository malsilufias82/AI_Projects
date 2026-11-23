& .\venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -q -r requirements.txt
streamlit run streamlit_app.py
