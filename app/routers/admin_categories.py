from fastapi import APIRouter, Depends, HTTPException
from slugify import slugify
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth import get_current_admin_user
from app.db.session import get_db
from app.models.product import Category
from app.schemas.product import CategoryCreate, CategoryOut, CategoryUpdate

router = APIRouter(
    prefix="/api/admin/categories",
    tags=["admin-categories"],
    dependencies=[Depends(get_current_admin_user)],
)


async def _unique_slug(db: AsyncSession, base_text: str, exclude_id: str | None = None) -> str:
    base = slugify(base_text)
    slug = base
    suffix = 2
    while True:
        stmt = select(Category.id).where(Category.slug == slug)
        if exclude_id:
            stmt = stmt.where(Category.id != exclude_id)
        if not (await db.execute(stmt)).scalar_one_or_none():
            return slug
        slug = f"{base}-{suffix}"
        suffix += 1


async def _get_category_or_404(db: AsyncSession, category_id: str) -> Category:
    category = await db.get(Category, category_id)
    if category is None:
        raise HTTPException(status_code=404, detail="Categoría no encontrada")
    return category


@router.get("", response_model=list[CategoryOut])
async def list_all_categories(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Category).order_by(Category.name))
    return result.scalars().all()


@router.post("", response_model=CategoryOut, status_code=201)
async def create_category(payload: CategoryCreate, db: AsyncSession = Depends(get_db)):
    slug = payload.slug and slugify(payload.slug) or await _unique_slug(db, payload.name)
    category = Category(name=payload.name, slug=slug)
    db.add(category)
    await db.commit()
    await db.refresh(category)
    return category


@router.patch("/{category_id}", response_model=CategoryOut)
async def update_category(category_id: str, payload: CategoryUpdate, db: AsyncSession = Depends(get_db)):
    category = await _get_category_or_404(db, category_id)
    changes = payload.model_dump(exclude_unset=True)

    if "slug" in changes and changes["slug"]:
        changes["slug"] = await _unique_slug(db, changes["slug"], exclude_id=category_id)
    elif "name" in changes and "slug" not in changes:
        pass  # el slug no cambia solo porque el nombre cambió (evita romper links ya compartidos)

    for field, value in changes.items():
        setattr(category, field, value)

    await db.commit()
    await db.refresh(category)
    return category


@router.delete("/{category_id}", status_code=204)
async def delete_category(category_id: str, db: AsyncSession = Depends(get_db)):
    """Borra la categoría. Los productos que la usaban quedan con
    category_id = NULL (ON DELETE SET NULL a nivel de base de datos), así que
    no se pierden, solo quedan sin categoría específica."""
    category = await _get_category_or_404(db, category_id)
    await db.delete(category)
    await db.commit()
