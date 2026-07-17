from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from opentelemetry import trace
from app.database import get_db
from app.auth.jwt_handler import decode_access_token
from app.models.user import User

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")
tracer = trace.get_tracer("poc-02-finance-api")

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    with tracer.start_as_current_span("auth.validate") as span:
        payload = decode_access_token(token)
        if payload is None:
            span.set_attribute("auth.token_valid", False)
            raise credentials_exception

        user_id = payload.get("sub")
        if user_id is None:
            span.set_attribute("auth.token_valid", False)
            raise credentials_exception

        span.set_attribute("auth.token_valid", True)
        span.set_attribute("auth.user_id", user_id)

    user = db.query(User).filter(User.id == int(user_id)).first()
    if user is None:
        raise credentials_exception
    return user