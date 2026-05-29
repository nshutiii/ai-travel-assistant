from pydantic import BaseModel, ConfigDict, Field


class ItineraryDayInput(BaseModel):
    day: int = Field(ge=1, le=365)
    activities: list[str] = Field(default_factory=list)


class ItineraryCreate(BaseModel):
    trip_id: int = Field(ge=1)
    days: list[ItineraryDayInput]


class ItineraryDayPublic(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    day: int
    activities: list[str]
    accommodation: str | None = None
    accommodation_cost: float | None = None
    food_cost: float | None = None
    other_cost: float | None = None
    total_day_cost: float | None = None


class ItineraryPublic(BaseModel):
    trip_id: int
    itinerary: list[ItineraryDayPublic]


class ItineraryCreateResponse(ItineraryPublic):
    message: str = "Itinerary created successfully"
    airfare_estimate: float | None = None
    budget_used_for_itinerary: float | None = None
