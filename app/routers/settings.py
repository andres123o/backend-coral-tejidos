from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth import get_current_admin_user
from app.db.session import get_db
from app.models.settings import StoreSettings
from app.schemas.settings import StoreSettingsOut, StoreSettingsUpdate

public_router = APIRouter(prefix="/api/settings", tags=["settings"])
admin_router = APIRouter(
    prefix="/api/admin/settings",
    tags=["admin-settings"],
    dependencies=[Depends(get_current_admin_user)],
)


async def _get_or_create_settings(db: AsyncSession) -> StoreSettings:
    result = await db.execute(select(StoreSettings).limit(1))
    settings_row = result.scalar_one_or_none()
    if settings_row is None:
        settings_row = StoreSettings()
        db.add(settings_row)
        await db.commit()
        await db.refresh(settings_row)
    return settings_row


@public_router.get("", response_model=StoreSettingsOut)
async def get_settings(db: AsyncSession = Depends(get_db)):
    return await _get_or_create_settings(db)


@admin_router.patch("", response_model=StoreSettingsOut)
async def update_settings(payload: StoreSettingsUpdate, db: AsyncSession = Depends(get_db)):
    settings_row = await _get_or_create_settings(db)
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(settings_row, field, value)
    await db.commit()
    await db.refresh(settings_row)
    return settings_row
