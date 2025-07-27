from pydantic import BaseModel, Field, validator
from typing import Any


class ClaimSummary(BaseModel):
    longitude: float = Field(..., description="Longitude of the event location.")
    latitude: float = Field(..., description="Latitude of the event location.")
    location: str = Field(..., description="Textual description of the location (e.g., 'Marathahalli, Bangalore').")
    summary: str = Field(..., description="Short summary of the validated claim.")

    @validator("location", "summary")
    def non_empty_strings(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("Must not be empty.")
        return v