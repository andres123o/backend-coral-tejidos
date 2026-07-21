from pydantic import BaseModel, ConfigDict, field_validator


class CategoryOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    name: str
    slug: str

    @field_validator("id", mode="before")
    @classmethod
    def _stringify_id(cls, value: object) -> str:
        return str(value)


class ProductOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    slug: str
    name: str
    subtitle: str | None
    description: str
    price: float
    promo_price: float | None
    is_on_promo: bool
    images: list[str]
    colors: list[str]
    scarcity_label: str | None
    is_available: bool
    is_featured: bool
    category: CategoryOut | None

    @field_validator("id", mode="before")
    @classmethod
    def _stringify_id(cls, value: object) -> str:
        return str(value)


class ProductAdminOut(ProductOut):
    """Igual que ProductOut, más is_active, porque el admin necesita ver también
    los productos archivados, cosa que el endpoint público nunca expone."""

    is_active: bool


class ProductCreate(BaseModel):
    name: str
    subtitle: str | None = None
    description: str = ""
    price: float
    promo_price: float | None = None
    is_on_promo: bool = False
    category_id: str | None = None
    images: list[str] = []
    colors: list[str] = []
    scarcity_label: str | None = None
    is_available: bool = True
    is_featured: bool = False


class ProductUpdate(BaseModel):
    """Todos los campos opcionales, para un PATCH parcial. Se aplica con
    `model_dump(exclude_unset=True)` para distinguir "no enviado" de
    "enviado como null/false"."""

    name: str | None = None
    subtitle: str | None = None
    description: str | None = None
    price: float | None = None
    promo_price: float | None = None
    is_on_promo: bool | None = None
    category_id: str | None = None
    images: list[str] | None = None
    colors: list[str] | None = None
    scarcity_label: str | None = None
    is_available: bool | None = None
    is_featured: bool | None = None
    is_active: bool | None = None


class CategoryCreate(BaseModel):
    name: str
    slug: str | None = None


class CategoryUpdate(BaseModel):
    name: str | None = None
    slug: str | None = None
