import os
import jwt
from datetime import datetime, timedelta
from ninja.security import HttpBearer

JWT_SECRET = os.environ.get("JWT_SECRET", "dev-secret")
JWT_ALGORITHM = "HS256"
JWT_EXPIRATION_DAYS = 7


def create_token(user_id: int, openid: str) -> str:
    payload = {
        "user_id": user_id,
        "openid": openid,
        "exp": datetime.utcnow() + timedelta(days=JWT_EXPIRATION_DAYS),
        "iat": datetime.utcnow(),
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)


def verify_token(token: str) -> dict | None:
    try:
        return jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
    except jwt.PyJWTError:
        return None


class BearerAuth(HttpBearer):
    def authenticate(self, request, token: str):
        payload = verify_token(token)
        if payload is None:
            return None
        return payload
