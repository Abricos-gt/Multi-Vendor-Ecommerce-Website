import os
from sqlalchemy import create_engine, text

pg_url = os.getenv('PG_URL') or os.getenv('DATABASE_URL')
if not pg_url:
    raise SystemExit('Set PG_URL or DATABASE_URL to your Supabase Postgres URL')

engine = create_engine(pg_url, pool_pre_ping=True)

stmts = [
    'ALTER TABLE "user" ALTER COLUMN password_hash TYPE TEXT',
    'ALTER TABLE product ALTER COLUMN image_url TYPE TEXT',
    'ALTER TABLE vendor_application ALTER COLUMN license_url TYPE TEXT',
    'ALTER TABLE vendor_application ALTER COLUMN id_card_url TYPE TEXT',
]

with engine.begin() as conn:
    for s in stmts:
        try:
            conn.execute(text(s))
            print(f"OK: {s}")
        except Exception as e:
            print(f"WARN: {s} -> {e}")

print('Done.')

