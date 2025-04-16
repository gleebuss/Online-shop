from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class OrderIn(BaseModel):
    customer_id: int
    order_date: datetime
    total_amount: float
    status: Optional[str] = "в обработке"

class OrderUpdate(BaseModel):
    total_amount: Optional[float] = None
    status: Optional[str] = None

class OrderOut(OrderIn):
    id: int
    order_date: datetime

    class Config:
        orm_mode = True
