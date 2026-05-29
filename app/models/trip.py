from sqlalchemy import ForeignKey, Integer, Numeric, String, Boolean
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class Trip(Base):
    __tablename__ = "trips"
    __allow_unmapped__ = True

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    destination: Mapped[str] = mapped_column(String(255), nullable=False)
    days: Mapped[int] = mapped_column(Integer, nullable=False)
    budget: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    trip_style: Mapped[str] = mapped_column(String(50), nullable=False)

    # New fields for flight support
    need_flight: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    origin: Mapped[str] | None = mapped_column(String(255), nullable=True)
    airfare_estimate: Mapped[float] | None = mapped_column(Numeric(10, 2), nullable=True, default=0)
