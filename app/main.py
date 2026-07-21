from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import get_settings
from app.routers import (
    admin_categories,
    admin_products,
    admin_uploads,
    categories,
    products,
    settings as settings_router,
)

settings = get_settings()

app = FastAPI(title="Coral Tejidos API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(products.router)
app.include_router(categories.router)
app.include_router(settings_router.public_router)
app.include_router(admin_products.router)
app.include_router(admin_categories.router)
app.include_router(admin_uploads.router)
app.include_router(settings_router.admin_router)


@app.get("/health")
async def health():
    return {"status": "ok"}
