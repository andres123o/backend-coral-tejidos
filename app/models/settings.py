from sqlalchemy import String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.session import Base
from app.models.product import _ID_TYPE, _new_uuid


class StoreSettings(Base):
    """Fila única de configuración de tienda (banner de Destacado + envíos).

    Se lee/escribe siempre la primera fila; si no existe ninguna, los routers
    la crean con valores nulos/por defecto la primera vez que se necesite.
    """

    __tablename__ = "store_settings"

    id: Mapped[str] = mapped_column(_ID_TYPE, primary_key=True, default=_new_uuid)

    # Imágenes de campaña del bloque "Destacado" (sin quitar fondo). Nulas
    # hasta que la dueña suba algo desde el admin, momento en que el frontend público cae a
    # los archivos estáticos en public/images/ mientras tanto.
    featured_image_desktop_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    featured_image_mobile_url: Mapped[str | None] = mapped_column(String(500), nullable=True)

    shipping_info: Mapped[str | None] = mapped_column(Text, nullable=True)
