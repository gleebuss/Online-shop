from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from passlib.hash import bcrypt
from uuid import uuid4
from datetime import datetime
import json

from app.db.postgres import get_db
from app.db.redis import get_redis
from app.models.postgres_models import Customer
from app.schemas.user import UserRegister, UserLogin, UserOut

router = APIRouter()

@router.post("/register", response_model=UserOut)
async def register_user(data: UserRegister, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Customer).where(Customer.email == data.email))
    existing_user = result.scalar_one_or_none()

    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    hashed_password = bcrypt.hash(data.password)
    new_user = Customer(
        name=data.name,
        email=data.email,
        password=hashed_password,
        phone=data.phone,
        address=data.address
    )
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    return new_user

@router.post("/login")
async def login_user(data: UserLogin, db: AsyncSession = Depends(get_db), redis=Depends(get_redis)):
    result = await db.execute(select(Customer).where(Customer.email == data.email))
    user = result.scalar_one_or_none()

    if not user or not bcrypt.verify(data.password, user.password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    # Ищем существующую сессию по customer_id
    async for key in redis.scan_iter("session:*"):
        session_data = await redis.get(key)
        if session_data:
            parsed = json.loads(session_data)
            if parsed.get("customer_id") == user.id:
                parsed["last_activity"] = datetime.utcnow().isoformat()
                await redis.setex(key, 3600, json.dumps(parsed))
                session_id = key.split(":")[1]
                return {"session_id": session_id}

    # Если нет — создаём новую
    session_id = str(uuid4())
    await redis.setex(
        f"session:{session_id}",
        3600,
        json.dumps({"customer_id": user.id, "last_activity": datetime.utcnow().isoformat()})
    )

    return {"session_id": session_id}
