from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
import structlog, time
from app.database import get_db
from app.schemas.user import UserCreate, UserLogin, Token
from app.models.user import User
from app.auth.jwt_handler import create_access_token, hash_password, verify_password

router = APIRouter(prefix="/auth", tags=["auth"])
log = structlog.get_logger()

@router.post("/register", status_code=201)
def register(payload: UserCreate, db: Session = Depends(get_db)):
    start = time.time()
    existing = db.query(User).filter(User.email == payload.email).first()
    if existing:
        log.warning("register_failed", operation="register", status="failure", reason="email_exists")
        raise HTTPException(status_code=400, detail="Email already registered")

    user = User(
        name=payload.name,
        email=payload.email,
        phone=payload.phone,
        monthly_income=payload.monthly_income,
        hashed_password=hash_password(payload.password),
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    log.info("register_success", operation="register", status="success",
              duration_ms=int((time.time() - start) * 1000), user_id=user.id)
    return {"id": user.id, "email": user.email}

@router.post("/login", response_model=Token)
def login(payload: UserLogin, db: Session = Depends(get_db)):
    start = time.time()
    user = db.query(User).filter(User.email == payload.email).first()
    if not user or not verify_password(payload.password, user.hashed_password):
        log.warning("login_failed", operation="login", status="failure")
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = create_access_token({"sub": str(user.id)})
    log.info("login_success", operation="login", status="success",
              duration_ms=int((time.time() - start) * 1000), user_id=user.id)
    return {"access_token": token, "token_type": "bearer"}