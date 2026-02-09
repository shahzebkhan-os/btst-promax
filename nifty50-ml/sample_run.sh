#!/usr/bin/env bash
set -e
python3 -m src.ingest.download_sample_data
python3 -m src.train --symbol RELIANCE --epochs 2 --demo
python3 -m src.pipeline.eta_demo
python3 -m streamlit run src/ui/app.py
