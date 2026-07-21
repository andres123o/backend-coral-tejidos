from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit


def prepare_asyncpg_url(url: str) -> tuple[str, dict]:
    """Normalizes a Postgres URL for use with SQLAlchemy + asyncpg.

   - Forces the `postgresql+asyncpg://` scheme (works whether the input was
      `postgres://`, `postgresql://`, or already `postgresql+asyncpg://`).
   - Strips `pgbouncer=true` from the query string, since asyncpg doesn't accept
      it as a connect kwarg, and instead disables asyncpg's server-side prepared
      statement cache via connect_args. This is required when connecting
      through Supabase's transaction-mode pooler (port 6543), which doesn't
      support prepared statements shared across pooled connections; without
      this, queries intermittently fail under load with "prepared statement
      already exists" errors. The session-mode pooler (port 5432, used for
      migrations) doesn't set `pgbouncer=true` and needs no special handling.
    """
    parts = urlsplit(url)
    query = dict(parse_qsl(parts.query))
    uses_pgbouncer = query.pop("pgbouncer", "false").lower() == "true"
    normalized = urlunsplit(("postgresql+asyncpg", parts.netloc, parts.path, urlencode(query), parts.fragment))

    connect_args = {}
    if uses_pgbouncer:
        # statement_cache_size=0 is the only real asyncpg.connect() kwarg that
        # disables its server-side prepared-statement cache (verified against
        # asyncpg's actual connect() signature). An earlier version of this
        # also passed a "prepared_statement_cache_size" kwarg, which doesn't
        # exist on asyncpg.connect() at all, so it's not the fix.
        connect_args = {"statement_cache_size": 0}
    return normalized, connect_args
