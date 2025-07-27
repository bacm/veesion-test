"""Models for the Alert Service."""

from pydantic import BaseModel

class Alert(BaseModel):
    """Alert model for the alert service."""
    uid: str
    video: str
    timestamp: float
    store: str

