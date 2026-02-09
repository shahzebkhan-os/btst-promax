from src.pipeline.progress_api import app

def test_progress_endpoint():
    # minimal import test
    assert app is not None
