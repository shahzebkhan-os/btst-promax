#!/usr/bin/env bash
set -e
python -m src.ingest.download_sample_data
python -m src.train --symbol RELIANCE --epochs 2 --demo
python -m src.pipeline.eta_demo
streamlit run src/ui/app.py
