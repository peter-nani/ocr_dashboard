import os
import sqlite3
from datetime import datetime, timedelta, timezone
import jwt
from fastapi import Request, HTTPException, status

SECRET_KEY = os.getenv("JWT_SECRET", "super-secret-control-room-key-9912")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 1440
DB_PATH = "/app/data/dashboard.db"

# Removed admin/admin. Added new custom fallback mapping for main.py imports.
USER_REGISTRY = {"operator": "matrix99"}

def verify_password(username: str, plain_password: str) -> bool:
    # 1. First check the local SQLite relational storage
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT password FROM users WHERE username = ?", (username,))
        row = cursor.fetchone()
        conn.close()
        if row and row[0] == plain_password:
            return True
    except Exception:
        # Fallback gracefully if database initialization hasn't finished yet
        pass

    # 2. Second check against the hardware registry fallback mapping
    if USER_REGISTRY.get(username) == plain_password:
        return True
        
    return False

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def get_current_user_from_cookie(request: Request):
    token = request.cookies.get("access_token")
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
        return username
    except jwt.PyJWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token expired or corrupt")