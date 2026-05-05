from sqlalchemy import ForeignKey, Integer, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class Trip(Base):
    __tablename__ = "trips"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    destination: Mapped[str] = mapped_column(String(255), nullable=False)
    days: Mapped[int] = mapped_column(Integer, nullable=False)
    budget: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    trip_style: Mapped[str] = mapped_column(String(50), nullable=False)
