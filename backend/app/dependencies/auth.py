from fastapi import Depends, HTTPException
from app.db.redis import get_redis
import json

async def get_current_admin(redis=Depends(get_redis), session_id: str = ""):
    print(session_id)
    if not session_id:
        raise HTTPException(status_code=401, detail="Missing session_id")
    
    session_data = await redis.get(f"session:{session_id}")
    if not session_data:
        raise HTTPException(status_code=401, detail="Invalid or expired session")
    
    session = json.loads(session_data)
    if "admin_id" not in session:
        raise HTTPException(status_code=403, detail="Not an admin session")

    return session

async def get_current_user(redis=Depends(get_redis), session_id: str = ""):
    # Получаем данные сессии из Redis
    session_data = await redis.get(f"session:{session_id}")
    
    if session_data is None:
        raise HTTPException(status_code=401, detail="Invalid session ID")

    # Декодируем данные сессии из JSON в Python-объект
    session_info = json.loads(session_data)
    
    # Возвращаем ID пользователя (или можно вернуть весь объект с дополнительной информацией)
    return {"id": session_info["customer_id"], "last_activity": session_info["last_activity"]}

