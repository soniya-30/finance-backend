# dependencies.py
from typing import List
from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app import utils

# -------------------------
# Extract user from JWT
# -------------------------

security = HTTPBearer()

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials  # auto extracts token

    payload = utils.verify_token(token)
    if payload is None:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    return payload

# -------------------------
# Role-based access control
# -------------------------
def require_roles(allowed_roles: List[str]):
    def role_checker(user = Depends(get_current_user)):
        if user.get("role") not in allowed_roles:
            raise HTTPException(status_code=403, detail="Operation not permitted")
        return user
    return role_checker