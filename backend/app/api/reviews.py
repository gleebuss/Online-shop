from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import update, delete
from app.models.postgres_models import Review
from app.db.postgres import get_db
from app.schemas.review import ReviewIn, ReviewUpdate, ReviewOut
from app.dependencies.auth import get_current_user, get_current_admin

router = APIRouter()

@router.post("/", response_model=ReviewOut, status_code=201)
async def create_review(
    review_data: ReviewIn,
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user)
):
    new_review = Review(
        product_id=review_data.product_id,
        customer_id=user["id"],
        rating=review_data.rating,
        comment=review_data.comment,
    )
    db.add(new_review)
    await db.commit()
    await db.refresh(new_review)
    return new_review

@router.put("/{review_id}", response_model=ReviewOut)
async def update_review(
    review_id: int,
    review_data: ReviewUpdate,
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user)
):
    review = await db.get(Review, review_id)
    if not review:
        raise HTTPException(status_code=404, detail="Review not found")
    if review.customer_id != user["id"]:
        raise HTTPException(status_code=403, detail="Not authorized")

    update_data = review_data.model_dump(exclude_unset=True)
    await db.execute(update(Review).where(Review.id == review_id).values(**update_data))
    await db.commit()
    return await db.get(Review, review_id)

@router.delete("/{review_id}", status_code=204)
async def delete_review(
    review_id: int,
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user)
):
    review = await db.get(Review, review_id)
    if not review:
        raise HTTPException(status_code=404, detail="Review not found")
    if review.customer_id != user["id"]:
        raise HTTPException(status_code=403, detail="Not authorized")
    await db.execute(delete(Review).where(Review.id == review_id))
    await db.commit()
    return None

# Админ может удалять любые отзывы
@router.delete("/admin/{review_id}", status_code=204)
async def delete_review_admin(
    review_id: int,
    db: AsyncSession = Depends(get_db),
    admin=Depends(get_current_admin)
):
    review = await db.get(Review, review_id)
    if not review:
        raise HTTPException(status_code=404, detail="Review not found")
    await db.execute(delete(Review).where(Review.id == review_id))
    await db.commit()
    return None
