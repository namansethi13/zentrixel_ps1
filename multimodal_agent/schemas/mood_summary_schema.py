from pydantic import BaseModel, Field


class MoodSummary(BaseModel):
    longitude: float = Field(..., description="Longitude of the location.")
    latitude: float = Field(..., description="Latitude of the location.")
    location: str = Field(..., description="Text name of the location.")
    summary: str = Field(..., description="Human-written event summary.")
    mood: str = Field(..., description="Categorized mood (e.g., angry, sad, happy, frustrated, etc.)")
    score: float = Field(..., description="Raw sentiment score from mood analysis (-1 to +1)")