# T-ALPHA Core (Local Prototype)

Local scaffold implementing the **alert schema**, **risk overrides**, and **JSON output** pipeline described by the spec. This is a deterministic *mock* generator with a validation step to ensure schema compliance.

## What’s Included
- `config.yaml` — thresholds and risk overrides
- `schema/alert_schema.json` — JSON schema for alerts
- `src/generator.py` — mock scanner + alert builder
- `src/validator.py` — JSON schema validation
- `src/heatmap.py` — heatmap summary builder (mock)
- `src/cli.py` — CLI entry point for scanning
- `outputs/sample_alert.json` — example output

## Run
```bash
cd t-alpha-core
python3 -m src.cli --market US
```

## Notes
- Uses mock data (replace with live data connectors later).
- Always emits required fields; missing data filled with `null` and listed in `data_gaps`.
