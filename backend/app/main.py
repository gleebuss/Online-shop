from fastapi import FastAPI
from app.db.postgres import init_db
from app.api.products import router

app = FastAPI()
app.include_router(router)
@app.on_event("startup")
async def startup_event():
    await init_db()

@app.get("/")
async def hello():
    return "Online shop"