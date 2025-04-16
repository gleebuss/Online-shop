from fastapi import APIRouter, Depends, HTTPException
from app.db.mongo import db, get_cart, add_to_cart, remove_from_cart, clear_cart
from app.dependencies.auth import get_current_user
from app.schemas.cart import CartItem, CartOut

router = APIRouter()


@router.get("/", response_model=CartOut)
def read_cart(user=Depends(get_current_user)):
    cart = get_cart(db, str(user["id"]))
    if not cart:
        raise HTTPException(status_code=404, detail="Cart is empty")
    return cart


@router.post("/add", status_code=201)
async def add_to_cart(item: CartItem, user=Depends(get_current_user)):
    cart = await get_cart(user["id"]) or {"items": []}
    
    for existing in cart["items"]:
        if existing["product_id"] == item.product_id:
            existing["quantity"] += item.quantity
            break
    else:
        cart["items"].append(item.dict())

    await set_cart(user["id"], cart)
    return cart


@router.post("/remove", status_code=204)
async def remove_item(item: CartItem, user=Depends(get_current_user)):
    remove_from_cart(db, str(user["id"]), item.product_id)


@router.post("/clear", status_code=204)
async def clear(user=Depends(get_current_user)):
    clear_cart(db, str(user["id"]))
    await clear_cart(user["id"])
    return {"message": "Cart cleared"}
