"""
Common API dependencies, such as content-type enforcement.
"""
from fastapi import Header, HTTPException, status
from typing import Optional


def enforce_json_content_type(content_type: Optional[str] = Header(None)):
    """
    Dependency that ensures requests have the Content-Type header set to application/json.

    Raises:
        HTTPException: If Content-Type is not application/json.
    """
    if content_type != "application/json":
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail="Content-Type must be application/json"
        )
