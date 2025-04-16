from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import update, delete
from app.db.postgres import get_db
from app.models.postgres_models import Order
from app.schemas.order import OrderIn, OrderOut, OrderUpdate
from typing import List

router = APIRouter()

@router.get("/", response_model=List[OrderOut])
async def get_orders(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Order))
    return result.scalars().all()

@router.get("/{order_id}", response_model=OrderOut)
async def get_order(order_id: int, db: AsyncSession = Depends(get_db)):
    cached = await get_cached_order(order_id)
    if cached:
        return cached
    order = await db.get(Order, order_id)
    await cache_order(order_id, order.__dict__)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return order

@router.post("/", response_model=OrderOut, status_code=201)
async def create_order(order: OrderIn, db: AsyncSession = Depends(get_db)):
    new_order = Order(**order.model_dump())
    db.add(new_order)
    await db.commit()
    await db.refresh(new_order)
    return new_order

@router.put("/{order_id}", response_model=OrderOut)
async def update_order(order_id: int, data: OrderUpdate, db: AsyncSession = Depends(get_db)):
    order = await db.get(Order, order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    update_data = data.model_dump(exclude_unset=True)
    await db.execute(update(Order).where(Order.id == order_id).values(**update_data))
    await db.commit()
    return await db.get(Order, order_id)

@router.delete("/{order_id}", status_code=204)
async def delete_order(order_id: int, db: AsyncSession = Depends(get_db)):
    order = await db.get(Order, order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    await db.execute(delete(Order).where(Order.id == order_id))
    await db.commit()
    return None
