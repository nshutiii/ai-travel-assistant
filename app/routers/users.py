from typing import Annotated

from fastapi import APIRouter, Depends

from app.deps import get_current_user
from app.models.user import User
from app.schemas.user import UserPublic

router = APIRouter(tags=["Users"])


@router.get("/me", response_model=UserPublic)
def read_me(current_user: Annotated[User, Depends(get_current_user)]) -> User:
    return current_user
