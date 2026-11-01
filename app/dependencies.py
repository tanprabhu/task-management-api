from typing import Annotated

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import (
    HTTPAuthorizationCredentials,
    HTTPBearer,
)
from jwt.exceptions import InvalidTokenError
from sqlalchemy.orm import Session

from app.config import get_settings
from app.database import get_db
from app.models import User


settings = get_settings()

bearer_scheme = HTTPBearer(auto_error=False)

DatabaseSession = Annotated[Session, Depends(get_db)]

BearerCredentials = Annotated[
    HTTPAuthorizationCredentials | None,
    Depends(bearer_scheme),
]


def authentication_error() -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials.",
        headers={"WWW-Authenticate": "Bearer"},
    )


def get_current_user(
    credentials: BearerCredentials,
    database: DatabaseSession,
) -> User:
    if credentials is None:
        raise authentication_error()

    try:
        payload = jwt.decode(
            credentials.credentials,
            settings.jwt_secret_key.get_secret_value(),
            algorithms=[settings.jwt_algorithm],
        )

        subject = payload.get("sub")

        if subject is None:
            raise authentication_error()

        user_id = int(subject)

    except (InvalidTokenError, TypeError, ValueError):
        raise authentication_error() from None

    user = database.get(User, user_id)

    if user is None:
        raise authentication_error()

    return user