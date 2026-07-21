from fastapi import APIRouter, Depends, HTTPException
from slugify import slugify
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.auth import get_current_admin_user
from app.db.session import get_db
from app.models.product import Product
from app.schemas.product import ProductAdminOut, ProductCreate, ProductUpdate

router = APIRouter(
    prefix="/api/admin/products",
    tags=["admin-products"],
    dependencies=[Depends(get_current_admin_user)],
)


async def _unique_slug(db: AsyncSession, name: str) -> str:
    base = slugify(name)
    slug = base
    suffix = 2
    while (await db.execute(select(Product.id).where(Product.slug == slug))).scalar_one_or_none():
        slug = f"{base}-{suffix}"
        suffix += 1
    return slug


async def _get_product_or_404(db: AsyncSession, product_id: str) -> Product:
    stmt = select(Product).options(selectinload(Product.category)).where(Product.id == product_id)
    result = await db.execute(stmt)
    product = result.scalar_one_or_none()
    if product is None:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    return product


@router.get("", response_model=list[ProductAdminOut])
async def list_all_products(db: AsyncSession = Depends(get_db)):
    stmt = (
        select(Product)
        .options(selectinload(Product.category))
        .order_by(Product.created_at.desc())
    )
    result = await db.execute(stmt)
    return result.scalars().all()


@router.get("/{product_id}", response_model=ProductAdminOut)
async def get_product(product_id: str, db: AsyncSession = Depends(get_db)):
    return await _get_product_or_404(db, product_id)


@router.post("", response_model=ProductAdminOut, status_code=201)
async def create_product(payload: ProductCreate, db: AsyncSession = Depends(get_db)):
    slug = await _unique_slug(db, payload.name)

    if payload.is_featured:
        await db.execute(update(Product).values(is_featured=False))

    product = Product(slug=slug, **payload.model_dump())
    db.add(product)
    await db.commit()
    return await _get_product_or_404(db, product.id)


@router.patch("/{product_id}", response_model=ProductAdminOut)
async def update_product(product_id: str, payload: ProductUpdate, db: AsyncSession = Depends(get_db)):
    product = await _get_product_or_404(db, product_id)
    changes = payload.model_dump(exclude_unset=True)

    if changes.get("is_featured") is True:
        await db.execute(update(Product).where(Product.id != product_id).values(is_featured=False))

    for field, value in changes.items():
        setattr(product, field, value)

    await db.commit()
    return await _get_product_or_404(db, product_id)


@router.delete("/{product_id}", response_model=ProductAdminOut)
async def archive_product(product_id: str, db: AsyncSession = Depends(get_db)):
    """Archiva el producto (is_active=false), nunca se borra permanentemente.
    Para reactivarlo, usar PATCH con is_active=true."""
    product = await _get_product_or_404(db, product_id)
    product.is_active = False
    await db.commit()
    return await _get_product_or_404(db, product_id)
