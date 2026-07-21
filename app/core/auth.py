from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from supabase import AsyncClient, create_async_client
from supabase_auth.types import User

from app.core.config import get_settings

_security = HTTPBearer(auto_error=False)

# Clientes de Supabase son async y su creación también lo es (`await
# create_async_client(...)`), así que no se pueden armar como una constante de
# módulo, así que se crean una sola vez de forma perezosa y se reutilizan.
_anon_client: AsyncClient | None = None
_admin_client: AsyncClient | None = None


async def get_supabase_anon_client() -> AsyncClient:
    """Cliente con la anon key, usado solo para verificar el token de quien inicia sesión."""
    global _anon_client
    if _anon_client is None:
        settings = get_settings()
        _anon_client = await create_async_client(settings.supabase_url, settings.supabase_anon_key)
    return _anon_client


async def get_supabase_admin_client() -> AsyncClient:
    """Cliente con la service role key, que bypassa RLS, usado para subir archivos a Storage.

    SENSIBLE: nunca exponer este cliente ni la key al frontend.
    """
    global _admin_client
    if _admin_client is None:
        settings = get_settings()
        _admin_client = await create_async_client(settings.supabase_url, settings.supabase_service_role_key)
    return _admin_client


async def get_current_admin_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(_security),
) -> User:
    """Dependency de FastAPI: exige `Authorization: Bearer <token>` con una
    sesión válida de Supabase Auth. Se usa en todos los routers de admin.
    """
    if credentials is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="No autenticado")

    client = await get_supabase_anon_client()
    try:
        response = await client.auth.get_user(credentials.credentials)
    except Exception as exc:  # token inválido/expirado -> gotrue levanta su propia excepción
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Sesión inválida") from exc

    if response is None or response.user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Sesión inválida")

    return response.user
