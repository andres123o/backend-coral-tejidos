import uuid

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from storage3.exceptions import StorageApiError

from app.core.auth import get_current_admin_user, get_supabase_admin_client

router = APIRouter(
    prefix="/api/admin/uploads",
    tags=["admin-uploads"],
    dependencies=[Depends(get_current_admin_user)],
)

BUCKET = "product-images"

_EXT_BY_CONTENT_TYPE = {
    "image/png": "png",
    "image/jpeg": "jpg",
    "image/jpg": "jpg",
    "image/webp": "webp",
}


async def _ensure_bucket_exists() -> None:
    client = await get_supabase_admin_client()
    try:
        await client.storage.get_bucket(BUCKET)
    except StorageApiError:
        await client.storage.create_bucket(BUCKET, options={"public": True})


def _extension_for(file: UploadFile) -> str:
    if file.filename and "." in file.filename:
        return file.filename.rsplit(".", 1)[-1].lower()
    return _EXT_BY_CONTENT_TYPE.get(file.content_type or "", "png")


@router.post("")
async def upload_image(file: UploadFile = File(...)):
    """Sube una imagen ya lista (el quitado de fondo, si aplica, ya se hizo en
    el navegador antes de llegar aquí) a Supabase Storage y devuelve su URL
    pública. Un solo endpoint sirve tanto para fotos de producto como para
    las imágenes de campaña del bloque Destacado."""
    await _ensure_bucket_exists()

    contents = await file.read()
    if not contents:
        raise HTTPException(status_code=400, detail="Archivo vacío")

    object_path = f"{uuid.uuid4()}.{_extension_for(file)}"

    client = await get_supabase_admin_client()
    try:
        await client.storage.from_(BUCKET).upload(
            object_path, contents, {"content-type": file.content_type or "application/octet-stream"}
        )
    except StorageApiError as exc:
        raise HTTPException(status_code=502, detail=f"Error subiendo a Supabase Storage: {exc}") from exc

    url = await client.storage.from_(BUCKET).get_public_url(object_path)
    return {"url": url}
