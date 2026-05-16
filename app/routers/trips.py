from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.deps import get_current_user
from app.models.trip import Trip
from app.models.user import User
from app.schemas.trip import TripCreate, TripPublic, TripUpdate

router = APIRouter(tags=["Trips"])


@router.post("", response_model=TripPublic)
def create_trip(
    payload: TripCreate,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> Trip:
    trip = Trip(
        user_id=current_user.id,
        destination=payload.destination,
        days=payload.days,
        budget=payload.budget,
        trip_style=payload.trip_style,
    )
    db.add(trip)
    db.commit()
    db.refresh(trip)
    return trip


@router.get("", response_model=list[TripPublic])
def list_trips(
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> list[Trip]:
    query = select(Trip).where(Trip.user_id == current_user.id).order_by(Trip.id)
    return list(db.scalars(query))


@router.get("/{trip_id}", response_model=TripPublic)
def get_trip(
    trip_id: int,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> Trip:
    trip = db.get(Trip, trip_id)
    if trip is None or trip.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Trip not found")
    return trip


@router.put("/{trip_id}", response_model=TripPublic)
def update_trip(
    trip_id: int,
    payload: TripUpdate,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> Trip:
    trip = db.get(Trip, trip_id)
    if trip is None or trip.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Trip not found")

    updates = payload.model_dump(exclude_unset=True)
    for key, value in updates.items():
        setattr(trip, key, value)

    db.add(trip)
    db.commit()
    db.refresh(trip)
    return trip


@router.delete("/{trip_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_trip(
    trip_id: int,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> None:
    trip = db.get(Trip, trip_id)
    if trip is None or trip.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Trip not found")

    db.delete(trip)
    db.commit()
    return None
