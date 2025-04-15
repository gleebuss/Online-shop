from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from passlib.hash import bcrypt
from uuid import uuid4
from datetime import datetime
import json

from app.db.postgres import get_db
from app.db.redis import get_redis
from app.models.postgres_models import Admin
from app.schemas.admin import AdminRegister, AdminLogin, AdminOut

router = APIRouter()

@router.post("/register", response_model=AdminOut)
async def register_admin(data: AdminRegister, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Admin).where(Admin.email == data.email))
    existing_admin = result.scalar_one_or_none()

    if existing_admin:
        raise HTTPException(status_code=400, detail="Email already registered")

    hashed_password = bcrypt.hash(data.password)
    new_admin = Admin(email=data.email, password=hashed_password)
    db.add(new_admin)
    await db.commit()
    await db.refresh(new_admin)
    return new_admin

@router.post("/login")
async def login_admin(data: AdminLogin, db: AsyncSession = Depends(get_db), redis=Depends(get_redis)):
    result = await db.execute(select(Admin).where(Admin.email == data.email))
    admin = result.scalar_one_or_none()

    if not admin or not bcrypt.verify(data.password, admin.password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    # Поиск существующей сессии по admin_id
    async for key in redis.scan_iter("session:*"):
        session_data = await redis.get(key)
        if session_data:
            parsed = json.loads(session_data)
            if parsed.get("admin_id") == admin.id:
                # Обновим last_activity и TTL
                parsed["last_activity"] = datetime.utcnow().isoformat()
                await redis.setex(key, 3600, json.dumps(parsed))
                session_id = key.split(":")[1]
                return {"session_id": session_id}

    # Если сессии нет — создаём новую
    session_id = str(uuid4())
    await redis.setex(
        f"session:{session_id}",
        3600,
        json.dumps({"admin_id": admin.id, "last_activity": datetime.utcnow().isoformat()})
    )

    return {"session_id": session_id}

