import json
from jsonschema import validate


def validate_alert(alert, schema_path):
    with open(schema_path, "r") as f:
        schema = json.load(f)
    validate(instance=alert, schema=schema)
    return True
