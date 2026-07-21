"""Seed de datos de ejemplo para desarrollo local.

Uso:
    python -m app.seed
"""

import asyncio

from slugify import slugify
from sqlalchemy import select

from app.db.session import async_session_maker
from app.models.product import Category, Product

CATEGORIES = [
    ("Amigurumis", "malva"),
    ("Hogar", "sage"),
    ("Bebé", "salmon"),
    ("Accesorios", "polvo"),
    ("Prendas", "arena"),
    ("Ediciones especiales", "aqua"),
]

# Fotos reales (fondo ya removido) en frontend/public/images/products/. Cada
# producto repite su única foto real varias veces para probar la galería de
# la card (puntos de navegación) mientras no haya varios ángulos por pieza.
SPIDERMAN = "/images/products/spiderman-amigurumi.png"
VIRGEN_CLASICA = "/images/products/virgen-maria-clasica.png"
VIRGEN_PIE = "/images/products/virgen-maria-pie.png"
LLAVERO_ROSA = "/images/products/llavero-rosa.png"


def _gallery(image: str) -> list[str]:
    return [image, image, image]


PRODUCTS = [
    {
        "name": "Spiderman Amigurumi",
        "subtitle": "Hilo suave, 100% algodón",
        "category": "Amigurumis",
        "description": "Amigurumi tejido a mano inspirado en Spiderman, ideal para regalo o colección.",
        "price": 55000,
        "promo_price": None,
        "is_on_promo": False,
        "images": _gallery(SPIDERMAN),
        "colors": ["Rojo/azul"],
        "is_featured": True,
    },
    {
        "name": "Virgen María Clásica",
        "subtitle": "Detalle en hilo dorado",
        "category": "Ediciones especiales",
        "description": "Figura de la Virgen María tejida a crochet, detalle en hilo dorado.",
        "price": 78000,
        "promo_price": 65000,
        "is_on_promo": True,
        "images": _gallery(VIRGEN_CLASICA),
        "colors": ["Celeste", "Blanco"],
        "is_featured": False,
    },
    {
        "name": "Virgen María de Pie",
        "subtitle": "Con base de madera",
        "category": "Ediciones especiales",
        "description": "Figura de la Virgen María sobre base de madera, acabado en dorado y turquesa.",
        "price": 82000,
        "promo_price": None,
        "is_on_promo": False,
        "images": _gallery(VIRGEN_PIE),
        "colors": ["Turquesa"],
        "is_featured": False,
    },
    {
        "name": "Llavero Rosa Tejida",
        "subtitle": "Incluye argolla metálica",
        "category": "Accesorios",
        "description": "Llavero con figura tejida y rosa de crochet, incluye argolla metálica.",
        "price": 32000,
        "promo_price": None,
        "is_on_promo": False,
        "images": _gallery(LLAVERO_ROSA),
        "colors": ["Rojo", "Rosado", "Blanco"],
        "is_featured": False,
    },
    {
        "name": "Spiderman Mini",
        "subtitle": "Tamaño llavero",
        "category": "Bebé",
        "description": "Versión mini del amigurumi de Spiderman, tamaño llavero/decoración.",
        "price": 38000,
        "promo_price": None,
        "is_on_promo": False,
        "images": _gallery(SPIDERMAN),
        "colors": ["Rojo/azul"],
        "is_featured": False,
    },
    {
        "name": "Virgen María Edición Dorada",
        "subtitle": "Edición limitada",
        "category": "Hogar",
        "description": "Edición especial con más detalle en hilo dorado, ideal para altar o sala.",
        "price": 95000,
        "promo_price": None,
        "is_on_promo": False,
        "images": _gallery(VIRGEN_CLASICA),
        "colors": ["Celeste"],
        "is_featured": False,
    },
    {
        "name": "Virgen Peregrina",
        "subtitle": "Base estable de madera",
        "category": "Hogar",
        "description": "Figura de la Virgen para llevar contigo o regalar, base estable de madera.",
        "price": 82000,
        "promo_price": 70000,
        "is_on_promo": True,
        "images": _gallery(VIRGEN_PIE),
        "colors": ["Turquesa", "Blanco"],
        "is_featured": False,
    },
    {
        "name": "Llavero Rosa Roja",
        "subtitle": "Detalle en hoja verde",
        "category": "Accesorios",
        "description": "Llavero tejido con rosa roja, detalle en verde para las hojas.",
        "price": 32000,
        "promo_price": None,
        "is_on_promo": False,
        "images": _gallery(LLAVERO_ROSA),
        "colors": ["Rojo"],
        "is_featured": False,
    },
    {
        "name": "Spiderman Colección",
        "subtitle": "Acabado en punto alto",
        "category": "Amigurumis",
        "description": "Pieza de colección tejida a mano, acabado en punto alto.",
        "price": 58000,
        "promo_price": None,
        "is_on_promo": False,
        "images": _gallery(SPIDERMAN),
        "colors": ["Rojo/azul"],
        "is_featured": False,
    },
    {
        "name": "Virgen María Azul",
        "subtitle": "Tonos azules suaves",
        "category": "Prendas",
        "description": "Variante en tonos azules, hecha a mano con hilo suave.",
        "price": 78000,
        "promo_price": None,
        "is_on_promo": False,
        "images": _gallery(VIRGEN_CLASICA),
        "colors": ["Celeste", "Turquesa"],
        "is_featured": False,
    },
    {
        "name": "Virgen del Camino",
        "subtitle": "Ideal para el carro",
        "category": "Hogar",
        "description": "Ideal para el carro o el escritorio, base de madera incluida.",
        "price": 82000,
        "promo_price": None,
        "is_on_promo": False,
        "images": _gallery(VIRGEN_PIE),
        "colors": ["Turquesa"],
        "is_featured": False,
    },
    {
        "name": "Llavero Rosa Premium",
        "subtitle": "Argolla dorada",
        "category": "Accesorios",
        "description": "Edición premium del llavero de rosa tejida, argolla dorada.",
        "price": 36000,
        "promo_price": None,
        "is_on_promo": False,
        "images": _gallery(LLAVERO_ROSA),
        "colors": ["Rosado", "Rojo"],
        "is_featured": False,
    },
]


async def seed() -> None:
    async with async_session_maker() as db:
        category_by_name: dict[str, Category] = {}

        for name, _color_key in CATEGORIES:
            slug = slugify(name)
            existing = await db.execute(select(Category).where(Category.slug == slug))
            category = existing.scalar_one_or_none()
            if category is None:
                category = Category(name=name, slug=slug)
                db.add(category)
                await db.flush()
            category_by_name[name] = category

        for item in PRODUCTS:
            slug = slugify(item["name"])
            existing = await db.execute(select(Product).where(Product.slug == slug))
            product = existing.scalar_one_or_none()
            if product is None:
                db.add(
                    Product(
                        slug=slug,
                        name=item["name"],
                        subtitle=item["subtitle"],
                        description=item["description"],
                        price=item["price"],
                        promo_price=item["promo_price"],
                        is_on_promo=item["is_on_promo"],
                        category_id=category_by_name[item["category"]].id,
                        images=item["images"],
                        colors=item["colors"],
                        is_featured=item["is_featured"],
                    )
                )
            else:
                # Actualiza productos ya sembrados (ej. de una corrida anterior sin imágenes)
                product.subtitle = item["subtitle"]
                product.images = item["images"]
                product.colors = item["colors"]
                product.is_featured = item["is_featured"]

        await db.commit()
    print(f"Seed listo: {len(CATEGORIES)} categorías, {len(PRODUCTS)} productos.")


if __name__ == "__main__":
    asyncio.run(seed())
