from fastapi import FastAPI
from app.db.postgres import init_db
from app.api import products, auth_user, auth_admin, categories, orders, reviews, order_items, user_profile, cart, promotions

app = FastAPI()
app.include_router(products.router, prefix="/products", tags=["Products"])
app.include_router(auth_user.router, prefix="/user/auth", tags=["UserAuth"])
app.include_router(auth_admin.router, prefix="/admin/auth", tags=["AdminAuth"])
app.include_router(categories.router, prefix="/categories", tags=["Categories"])
app.include_router(orders.router, prefix="/orders", tags=["Orders"])
app.include_router(reviews.router, prefix="/reviews", tags=["Reviews"])
app.include_router(order_items.router, prefix="/order-items", tags=["OrderItems"])
app.include_router(user_profile.router, prefix="/user/me", tags=["User Profile"])
app.include_router(cart.router, prefix="/cart", tags=["Cart"])
app.include_router(promotions.router, prefix="/promotions", tags=["Promotions"])


@app.on_event("startup")
async def startup_event():
    await init_db()

@app.get("/")
async def hello():
    return "Online shop"