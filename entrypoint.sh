#!/bin/sh
echo "App is running at: http://localhost:8501"
exec streamlit run app.py --server.port=8501 --server.address=0.0.0.0
