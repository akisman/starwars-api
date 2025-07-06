import pytest
from fastapi import HTTPException
from app.api.dependencies import enforce_json_content_type


def test_enforce_json_content_type_accepts_json():
    enforce_json_content_type("application/json")  # should not raise

def test_enforce_json_content_type_rejects_other():
    with pytest.raises(HTTPException) as exc:
        enforce_json_content_type("text/plain")
    assert exc.value.status_code == 415

def test_enforce_json_content_type_none_header():
    with pytest.raises(HTTPException) as exc:
        enforce_json_content_type(None)
    assert exc.value.status_code == 415
