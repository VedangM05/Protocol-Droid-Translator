#!/bin/bash
cd "$(dirname "$0")"
echo "=============================================="
echo "  BhashaEngine – starting Streamlit..."
echo "  First run can take 1–2 minutes (loading ML libs)."
echo "  When ready, open: http://localhost:8501"
echo "=============================================="
exec .venv/bin/streamlit run app.py --server.headless true
