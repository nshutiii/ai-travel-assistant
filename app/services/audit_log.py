import logging

logger = logging.getLogger("app.audit")


def record_trip_created(*, trip_id: int, user_id: int, destination: str) -> None:
    logger.info(
        "audit.trip_created trip_id=%s user_id=%s destination=%s",
        trip_id,
        user_id,
        destination,
    )


def record_itinerary_saved(*, trip_id: int, user_id: int, day_count: int) -> None:
    logger.info(
        "audit.itinerary_saved trip_id=%s user_id=%s day_count=%s",
        trip_id,
        user_id,
        day_count,
    )
