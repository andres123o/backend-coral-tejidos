from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.db.session import get_db
from app.models.product import Product
from app.schemas.product import ProductOut

router = APIRouter(prefix="/api/products", tags=["products"])


@router.get("", response_model=list[ProductOut])
async def list_products(
    db: AsyncSession = Depends(get_db),
    category: str | None = Query(default=None, description="Slug de categoría"),
    q: str | None = Query(default=None, description="Búsqueda por nombre/descripción"),
    featured: bool | None = Query(default=None),
):
    stmt = (
        select(Product)
        .options(selectinload(Product.category))
        .where(Product.is_active.is_(True))
        .order_by(Product.created_at.desc())
    )

    if category:
        stmt = stmt.where(Product.category.has(slug=category))
    if featured is not None:
        stmt = stmt.where(Product.is_featured.is_(featured))
    if q:
        like = f"%{q.lower()}%"
        stmt = stmt.where(
            (Product.name.ilike(like)) | (Product.description.ilike(like))
        )

    result = await db.execute(stmt)
    return result.scalars().all()


@router.get("/{slug}", response_model=ProductOut)
async def get_product(slug: str, db: AsyncSession = Depends(get_db)):
    stmt = (
        select(Product)
        .options(selectinload(Product.category))
        .where(Product.slug == slug, Product.is_active.is_(True))
    )
    result = await db.execute(stmt)
    product = result.scalar_one_or_none()
    if product is None:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    return product
