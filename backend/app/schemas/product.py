from pydantic import BaseModel, HttpUrl
from typing import Optional

class ProductBase(BaseModel):
    name: str
    price: float
    category_id: int
    stock_quantity: int = 0
    image: Optional[str] = None

class ProductIn(ProductBase):
    description: Optional[str] = None
    attributes: Optional[dict] = None

class ProductUpdate(BaseModel):
    name: Optional[str] = None
    price: Optional[float] = None
    category_id: Optional[int] = None
    stock_quantity: Optional[int] = None
    image: Optional[HttpUrl] = None
    description: Optional[str] = None
    attributes: Optional[dict] = None

class ProductOut(ProductBase):
    id: int

    class Config:
        orm_mode = True
