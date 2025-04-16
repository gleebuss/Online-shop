from fastapi import APIRouter, Depends, HTTPException
from app.db.mongo import (
    db,
    get_user_profile,
    create_user_profile,
    update_user_profile,
    push_to_list,
    remove_from_list
)
from app.dependencies.auth import get_current_user
from app.schemas.user_profile import UserProfileOut, UserProfileUpdate
from app.schemas.product import ProductOut
from app.db.postgres import get_db
from app.models.postgres_models import Product
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

router = APIRouter()


@router.get("/profile", response_model=UserProfileOut)
async def read_profile(user=Depends(get_current_user)):
    profile = get_user_profile(mongo_db, str(user["id"]))
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    return profile


@router.put("/profile", response_model=UserProfileOut)
async def update_profile(data: UserProfileUpdate, user=Depends(get_current_user)):
    return update_user_profile(mongo_db, str(user["id"]), data.dict(exclude_unset=True))


@router.post("/wishlist/{product_id}", status_code=204)
async def add_to_wishlist(product_id: int, user=Depends(get_current_user)):
    push_to_list(mongo_db, str(user["id"]), "wishlist", product_id)


@router.delete("/wishlist/{product_id}", status_code=204)
async def remove_from_wishlist(product_id: int, user=Depends(get_current_user)):
    remove_from_list(mongo_db, str(user["id"]), "wishlist", product_id)


@router.post("/recent/{product_id}", status_code=204)
async def add_to_recent(product_id: int, user=Depends(get_current_user)):
    push_to_list(mongo_db, str(user["id"]), "recent_views", product_id)


@router.get("/wishlist/products", response_model=list[ProductOut])
async def get_wishlist_products(
    user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    profile = get_user_profile(mongo_db, str(user["id"]))
    if not profile or not profile.wishlist:
        return []
    result = await db.execute(select(Product).where(Product.id.in_(profile.wishlist)))
    return result.scalars().all()
