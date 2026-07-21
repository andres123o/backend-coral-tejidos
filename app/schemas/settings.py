from pydantic import BaseModel, ConfigDict


class StoreSettingsOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    featured_image_desktop_url: str | None
    featured_image_mobile_url: str | None
    shipping_info: str | None


class StoreSettingsUpdate(BaseModel):
    featured_image_desktop_url: str | None = None
    featured_image_mobile_url: str | None = None
    shipping_info: str | None = None
