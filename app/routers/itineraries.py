from typing import Annotated

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.deps import get_current_user
from app.models.itinerary import Itinerary
from app.models.trip import Trip
from app.models.user import User
from app.schemas.itinerary import ItineraryCreate, ItineraryCreateResponse, ItineraryDayPublic, ItineraryPublic
from app.services.itinerary_manager import generate_itinerary_fast
from app.services.flight_search import search_affordable_airfare
from app.services.audit_log import record_itinerary_saved

router = APIRouter(tags=["Itineraries"])


def _trip_owned_or_404(db: Session, trip_id: int, user_id: int) -> Trip:
    trip = db.get(Trip, trip_id)
    if trip is None or trip.user_id != user_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Trip not found")
    return trip


def _payload_to_public_days(payload: list) -> list[ItineraryDayPublic]:
    ordered = sorted(payload, key=lambda row: row["day"])
    return [ItineraryDayPublic.model_validate(row) for row in ordered]


@router.post("/generate/{trip_id}", response_model=ItineraryCreateResponse)
def generate_and_save_ai_itinerary(
    trip_id: int,
    background_tasks: BackgroundTasks,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> ItineraryCreateResponse:
    trip = _trip_owned_or_404(db, trip_id, current_user.id)

    # Estimate airfare if user needs a flight
    airfare = None
    if getattr(trip, 'need_flight', False) and getattr(trip, 'origin', None):
        try:
            airfare = search_affordable_airfare(trip.origin, trip.destination)
        except Exception:
            airfare = None

    # Deduct airfare from budget when asking AI to plan daily costs
    budget_for_ai = float(trip.budget)
    if airfare:
        try:
            budget_for_ai = max(0.0, float(trip.budget) - float(airfare))
            # persist the estimate on the trip row
            trip.airfare_estimate = airfare
            db.add(trip)
            db.commit()
            db.refresh(trip)
        except Exception:
            # ignore persistence errors
            pass

    # Use the fast itinerary manager which runs providers in parallel and caches results
    ai_days = generate_itinerary_fast(trip.destination, trip.days, trip.trip_style, budget_for_ai)

    # Save to DB
    existing = db.scalars(select(Itinerary).where(Itinerary.trip_id == trip_id)).first()
    if existing is None:
        row = Itinerary(trip_id=trip_id, days_payload=ai_days)
        db.add(row)
    else:
        existing.days_payload = ai_days
        row = existing

    db.commit()
    db.refresh(row)

    background_tasks.add_task(
        record_itinerary_saved,
        trip_id=trip_id,
        user_id=current_user.id,
        day_count=len(ai_days),
    )

    return ItineraryCreateResponse(
        trip_id=trip_id,
        itinerary=_payload_to_public_days(row.days_payload),
        message="Itinerary generated successfully",
        airfare_estimate=float(row.__dict__.get('airfare_estimate')) if getattr(row, 'airfare_estimate', None) else None,
        budget_used_for_itinerary=float(budget_for_ai) if 'budget_for_ai' in locals() else float(trip.budget)
    )


@router.post("", response_model=ItineraryCreateResponse)
def create_or_update_itinerary(
    payload: ItineraryCreate,
    background_tasks: BackgroundTasks,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> ItineraryCreateResponse:
    _trip_owned_or_404(db, payload.trip_id, current_user.id)

    stored = [{"day": d.day, "activities": list(d.activities)} for d in payload.days]
    existing = db.scalars(select(Itinerary).where(Itinerary.trip_id == payload.trip_id)).first()

    if existing is None:
        row = Itinerary(trip_id=payload.trip_id, days_payload=stored)
        db.add(row)
    else:
        existing.days_payload = stored
        row = existing

    db.commit()
    db.refresh(row)

    background_tasks.add_task(
        record_itinerary_saved,
        trip_id=payload.trip_id,
        user_id=current_user.id,
        day_count=len(payload.days),
    )

    return ItineraryCreateResponse(
        trip_id=payload.trip_id,
        itinerary=_payload_to_public_days(row.days_payload),
        message="Itinerary created successfully",
    )


@router.get("/{trip_id}", response_model=ItineraryPublic)
def get_itinerary_for_trip(
    trip_id: int,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> ItineraryPublic:
    _trip_owned_or_404(db, trip_id, current_user.id)

    row = db.scalars(select(Itinerary).where(Itinerary.trip_id == trip_id)).first()
    if row is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Itinerary not found")

    return ItineraryPublic(
        trip_id=trip_id,
        itinerary=_payload_to_public_days(row.days_payload),
    )
