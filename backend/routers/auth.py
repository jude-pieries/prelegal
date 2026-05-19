import os
from datetime import datetime, timedelta, timezone

import bcrypt
from fastapi import APIRouter, HTTPException
from jose import jwt
from pydantic import BaseModel

from database import get_db

router = APIRouter()

SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key-change-in-production")
ALGORITHM = "HS256"
TOKEN_EXPIRE_HOURS = 24


class AuthRequest(BaseModel):
    email: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


def _hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


def _verify_password(password: str, hashed: str) -> bool:
    return bcrypt.checkpw(password.encode(), hashed.encode())


def _make_token(user_id: int) -> str:
    expires = datetime.now(timezone.utc) + timedelta(hours=TOKEN_EXPIRE_HOURS)
    return jwt.encode({"sub": str(user_id), "exp": expires}, SECRET_KEY, algorithm=ALGORITHM)


@router.post("/signup", response_model=TokenResponse)
def signup(req: AuthRequest):
    with get_db() as db:
        if db.execute("SELECT id FROM users WHERE email = ?", (req.email,)).fetchone():
            raise HTTPException(status_code=400, detail="Email already registered")
        db.execute(
            "INSERT INTO users (email, password_hash) VALUES (?, ?)",
            (req.email, _hash_password(req.password)),
        )
        db.commit()
        user_id = db.execute("SELECT last_insert_rowid()").fetchone()[0]
    return TokenResponse(access_token=_make_token(user_id))


@router.post("/signin", response_model=TokenResponse)
def signin(req: AuthRequest):
    with get_db() as db:
        user = db.execute(
            "SELECT id, password_hash FROM users WHERE email = ?", (req.email,)
        ).fetchone()
    if not user or not _verify_password(req.password, user["password_hash"]):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    return TokenResponse(access_token=_make_token(user["id"]))
