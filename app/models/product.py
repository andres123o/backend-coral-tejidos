import uuid
from datetime import datetime

from sqlalchemy import JSON, Boolean, DateTime, ForeignKey, Numeric, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base

# IDs se guardan como texto (no el tipo UUID nativo de Postgres) en ambas
# bases de datos, a propósito: así el esquema es idéntico en SQLite (dev
# local) y Postgres (Supabase), sin ramas condicionales por motor. Esto evita
# que las migraciones generadas contra un motor queden con un tipo de columna
# que no coincide con lo que el modelo espera al correr contra el otro.
_ID_TYPE = String(36)


def _new_uuid() -> str:
    return str(uuid.uuid4())


class Category(Base):
    __tablename__ = "categories"

    id: Mapped[str] = mapped_column(_ID_TYPE, primary_key=True, default=_new_uuid)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    slug: Mapped[str] = mapped_column(String(140), unique=True, nullable=False, index=True)

    products: Mapped[list["Product"]] = relationship(back_populates="category")


class Product(Base):
    __tablename__ = "products"

    id: Mapped[str] = mapped_column(_ID_TYPE, primary_key=True, default=_new_uuid)
    slug: Mapped[str] = mapped_column(String(160), unique=True, nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(160), nullable=False)
    subtitle: Mapped[str | None] = mapped_column(String(160), nullable=True)
    description: Mapped[str] = mapped_column(Text, default="")

    price: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    promo_price: Mapped[float | None] = mapped_column(Numeric(10, 2), nullable=True)
    is_on_promo: Mapped[bool] = mapped_column(Boolean, default=False)

    category_id: Mapped[str | None] = mapped_column(
        _ID_TYPE, ForeignKey("categories.id", ondelete="SET NULL"), nullable=True
    )
    category: Mapped[Category | None] = relationship(back_populates="products")

    images: Mapped[list[str]] = mapped_column(JSON, default=list)
    # Uno o varios colores disponibles para la pieza (lo define quien administra
    # la tienda). Si tiene más de uno, la persona elige color antes de comprar.
    colors: Mapped[list[str]] = mapped_column(JSON, default=list)
    # Texto libre de escasez/urgencia (ej. "Pieza única", "Últimas 2"), ver
    # documentacion/estrategia-cta-conversion.md. Opcional, la dueña lo escribe
    # por producto desde el admin; no se calcula automáticamente.
    scarcity_label: Mapped[str | None] = mapped_column(String(80), nullable=True)

    is_available: Mapped[bool] = mapped_column(Boolean, default=True)
    is_featured: Mapped[bool] = mapped_column(Boolean, default=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
