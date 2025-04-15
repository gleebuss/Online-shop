from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import update, delete
from typing import List

from bson import ObjectId
from app.models.postgres_models import Product, Category
from app.db.postgres import get_db
from app.db.mongo import get_mongo_collection
from app.schemas.product import ProductIn, ProductUpdate, ProductOut
from app.dependencies.auth import get_current_admin

router = APIRouter()

@router.get("/", response_model=List[ProductOut])
async def get_products(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Product))
    return result.scalars().all()

@router.get("/{product_id}", response_model=ProductOut)
async def get_product(product_id: int, db: AsyncSession = Depends(get_db)):
    product = await db.get(Product, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product

@router.post("/", response_model=ProductOut, status_code=201)
async def create_product(
    product_data: ProductIn,
    db: AsyncSession = Depends(get_db),
    mongo=Depends(get_mongo_collection),
    admin=Depends(get_current_admin)
):
    category = await db.get(Category, product_data.category_id)
    if not category:
        raise HTTPException(status_code=400, detail="Category not found")

    product = Product(
        name=product_data.name,
        price=product_data.price,
        category_id=product_data.category_id,
        stock_quantity=product_data.stock_quantity,
        image=product_data.image
    )
    db.add(product)
    await db.commit()
    await db.refresh(product)

    mongo["products"].insert_one({
        "product_id": product.id,
        "description": product_data.description,
        "attributes": product_data.attributes
    })

    return product

@router.put("/{product_id}", response_model=ProductOut)
async def update_product(
    product_id: int,
    product_data: ProductUpdate,
    db: AsyncSession = Depends(get_db),
    admin=Depends(get_current_admin),
    mongo_collection=Depends(get_mongo_collection),
):
    product = await db.get(Product, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    update_data = product_data.model_dump(exclude_unset=True)
    await db.execute(
        update(Product).where(Product.id == product_id).values(**update_data)
    )
    await db.commit()
    updated_product = await db.get(Product, product_id)

    # Mongo: Обновим документ, если он существует
    mongo_collection.update_one(
        {"_id": str(product_id)},
        {"$set": {
            "description": update_data.get("description", ""),
            "attributes": update_data.get("attributes", {})
        }},
        upsert=True  # на случай, если в Mongo ещё нет этого товара
    )

    return updated_product

@router.patch("/{product_id}", response_model=ProductOut)
async def partial_update_product(
    product_id: int,
    product_data: ProductUpdate,
    db: AsyncSession = Depends(get_db),
    admin=Depends(get_current_admin),
    mongo_collection=Depends(get_mongo_collection),
):
    return await update_product(product_id, product_data, db, admin, mongo_collection)

@router.delete("/{product_id}", status_code=204)
async def delete_product(
    product_id: int,
    db: AsyncSession = Depends(get_db),
    admin=Depends(get_current_admin),
    mongo_collection=Depends(get_mongo_collection),
):
    product = await db.get(Product, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    await db.execute(delete(Product).where(Product.id == product_id))
    await db.commit()

    mongo_collection.delete_one({"_id": str(product_id)})

    return None