from fastapi import WebSocket, HTTPException, status
from pydantic import BaseModel
import jwt
from datetime import datetime, timedelta

class TokenData(BaseModel):
    """Token payload data"""
    user_id: str
    exp: datetime

SECRET_KEY = "your-secret-key-change-in-production"
ALGORITHM = "HS256"

async def verify_websocket_token(websocket: WebSocket, token: str) -> TokenData:
    """Verify JWT token for websocket connection"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        token_data = TokenData(**payload)
        if token_data.exp < datetime.utcnow():
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
            raise HTTPException(status_code=401, detail="Token expired")
        return token_data
    except jwt.InvalidTokenError:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        raise HTTPException(status_code=401, detail="Invalid token")
