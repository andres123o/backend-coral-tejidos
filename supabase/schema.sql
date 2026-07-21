-- Esquema inicial para Coral Tejidos.
-- Alternativa a correr `alembic upgrade head`: pegar esto directo en el SQL Editor de Supabase.
-- Debe quedar en sync con backend/app/models/product.py: si cambias el modelo, corre Alembic
-- localmente para generar la migración equivalente en vez de editar este archivo a mano.

create extension if not exists "pgcrypto";

-- IDs se guardan como texto (varchar(36)), no el tipo uuid nativo de Postgres,
-- a propósito: coincide con lo que genera la app (Python uuid4) y con lo que
-- usa el mismo esquema en SQLite (dev local), ver app/models/product.py.
create table if not exists categories (
    id varchar(36) primary key default gen_random_uuid()::text,
    name varchar(120) not null,
    slug varchar(140) not null unique
);

create table if not exists products (
    id varchar(36) primary key default gen_random_uuid()::text,
    slug varchar(160) not null unique,
    name varchar(160) not null,
    subtitle varchar(160),
    description text not null default '',
    price numeric(10, 2) not null,
    promo_price numeric(10, 2),
    is_on_promo boolean not null default false,
    category_id varchar(36) references categories (id) on delete set null,
    images jsonb not null default '[]'::jsonb,
    colors jsonb not null default '[]'::jsonb,
    -- Texto libre de escasez/urgencia (ej. "Pieza única"), ver
    -- documentacion/estrategia-cta-conversion.md.
    scarcity_label varchar(80),
    is_available boolean not null default true,
    is_featured boolean not null default false,
    is_active boolean not null default true,
    created_at timestamptz not null default now(),
    updated_at timestamptz not null default now()
);

create index if not exists idx_products_category_id on products (category_id);
create index if not exists idx_products_is_active on products (is_active);

-- Fila única de configuración de tienda: banner de "Destacado" (desktop/mobile,
-- sin quitar fondo) y texto de envíos/cambios. Ver app/models/settings.py.
create table if not exists store_settings (
    id varchar(36) primary key default gen_random_uuid()::text,
    featured_image_desktop_url varchar(500),
    featured_image_mobile_url varchar(500),
    shipping_info text
);

-- RLS: lectura pública de productos activos/categorías/settings, escritura
-- solo desde el backend (que usa la service role key, la cual bypassa RLS).
-- Esto evita que cualquiera con la anon key pueda insertar/editar directo
-- desde el navegador.
alter table categories enable row level security;
alter table products enable row level security;
alter table store_settings enable row level security;

create policy "categories are publicly readable"
    on categories for select
    using (true);

create policy "active products are publicly readable"
    on products for select
    using (is_active = true);

create policy "store settings are publicly readable"
    on store_settings for select
    using (true);
