import os
import sys
from typing import List
from sqlalchemy import create_engine, MetaData, Table, text, select
from sqlalchemy.sql.sqltypes import Integer, Boolean, Float, Numeric, DateTime
from sqlalchemy.engine import Engine


def get_env(key: str, default: str = "") -> str:
    value = os.getenv(key, default)
    if value is None:
        return default
    return value


def create_db_engine(url: str) -> Engine:
    return create_engine(url, pool_pre_ping=True)


def reflect_tables(engine: Engine, schema: str | None = None) -> MetaData:
    metadata = MetaData(schema=schema)
    metadata.reflect(bind=engine)
    return metadata


def disable_triggers(engine: Engine, tables: List[Table], schema: str | None = None) -> None:
    try:
        with engine.begin() as conn:
            for table in tables:
                full_name = f"{schema}.{table.name}" if schema else table.name
                conn.execute(text(f'ALTER TABLE {full_name} DISABLE TRIGGER ALL'))
    except Exception:
        # Not all roles/schemas allow this; proceed without fatal error
        pass


def enable_triggers(engine: Engine, tables: List[Table], schema: str | None = None) -> None:
    try:
        with engine.begin() as conn:
            for table in tables:
                full_name = f"{schema}.{table.name}" if schema else table.name
                conn.execute(text(f'ALTER TABLE {full_name} ENABLE TRIGGER ALL'))
    except Exception:
        pass


def _pg_type_for(sqlite_col) -> str:
    t = sqlite_col.type
    # Map common SQLite types to Postgres
    if isinstance(t, Integer):
        return 'INTEGER'
    if isinstance(t, (Float, Numeric)):
        return 'NUMERIC'
    if isinstance(t, Boolean):
        return 'BOOLEAN'
    if isinstance(t, DateTime):
        return 'TIMESTAMP'
    # Default to TEXT for anything else (incl. VARCHAR, TEXT, BLOB)
    return 'TEXT'

def ensure_table_exists_in_postgres(dest_engine: Engine, src_table: Table) -> None:
    col_defs = []
    pk_cols = [c.name for c in src_table.primary_key.columns] if src_table.primary_key else []
    for c in src_table.columns:
        pg_type = _pg_type_for(c)
        col_sql = f'"{c.name}" {pg_type}'
        # Simple NOT NULL if reflected as nullable=False
        if not c.nullable:
            col_sql += ' NOT NULL'
        col_defs.append(col_sql)
    pk_sql = f', PRIMARY KEY ({", ".join(f"\"{n}\"" for n in pk_cols)})' if pk_cols else ''
    ddl = f'CREATE TABLE IF NOT EXISTS "{src_table.name}" ({", ".join(col_defs)}{pk_sql})'
    with dest_engine.begin() as conn:
        conn.execute(text(ddl))

def copy_table(source_engine: Engine, dest_engine: Engine, src_table: Table, dest_table: Table) -> None:
    # Pull rows from source using SQLAlchemy Core to avoid manual quoting
    with source_engine.connect() as s_conn:
        rows = s_conn.execute(select(src_table)).mappings().all()
        if not rows:
            return

    # Bulk insert into destination using table.insert() which handles quoting
    chunk_size = 1000
    with dest_engine.begin() as d_conn:
        for i in range(0, len(rows), chunk_size):
            chunk = rows[i : i + chunk_size]
            try:
                d_conn.execute(dest_table.insert(), chunk)
            except Exception:
                # Best-effort: insert row-by-row and skip duplicates or FK failures
                for r in chunk:
                    try:
                        d_conn.execute(dest_table.insert(), r)
                    except Exception:
                        pass


def main() -> int:
    # Paths and URLs
    sqlite_url = get_env('SQLITE_URL', 'sqlite:///instance/app.db')
    pg_url = get_env('PG_URL') or get_env('DATABASE_URL')
    if not pg_url:
        print('ERROR: Set PG_URL or DATABASE_URL to your Supabase Postgres URL (with sslmode=require).')
        return 1

    source = create_db_engine(sqlite_url)
    dest = create_db_engine(pg_url)

    # Reflect tables from SQLite
    src_md = reflect_tables(source)
    if not src_md.tables:
        print('No tables found in source database.')
        return 0

    # Create tables on destination if they don't exist
    # Note: Reflection from SQLite may not carry FKs perfectly; run your own migrations beforehand if available
    # Prefer that destination schema is already created via your app models.
    # If not, best-effort create based on reflected SQLite metadata.
    try:
        src_md.create_all(dest, checkfirst=True)
    except Exception as e:
        print(f'WARN: Could not auto-create tables on destination: {e}')

    # Disable triggers (best-effort)
    tables = list(src_md.sorted_tables)
    disable_triggers(dest, tables)

    # Reflect destination tables to ensure proper quoting and types
    dest_md = MetaData()
    dest_md.reflect(bind=dest)

    # Copy in dependency-safe order where possible
    preferred_order = [
        'user',
        'product',
        'parent_order',
        'order',
        'order_item',
        'sub_order',
        'sub_order_item',
        'vendor_application',
        'vendor_wallet',
        'wallet_ledger',
        'withdrawal_request',
        'refund',
        'email_verification_token',
        'password_reset_token',
        'payment_audit',
        'admin_settings',
        'carousel_slide',
    ]

    # Build ordered list of tables present
    ordered_tables = [t for name in preferred_order for t in tables if t.name == name]
    # Append any remaining tables not listed explicitly
    ordered_tables += [t for t in tables if t not in ordered_tables]

    try:
        for src_table in ordered_tables:
            print(f'Copying table: {src_table.name}')
            try:
                dest_table = dest_md.tables.get(src_table.name)
                if dest_table is None:
                    # Create a compatible table in Postgres, then reflect it
                    try:
                        ensure_table_exists_in_postgres(dest, src_table)
                        dest_table = Table(src_table.name, dest_md, autoload_with=dest)
                    except Exception as e:
                        print(f'ERROR creating destination table {src_table.name}: {e}')
                        continue
                copy_table(source, dest, src_table, dest_table)
            except Exception as e:
                print(f'ERROR copying {src_table.name}: {e}')
    finally:
        enable_triggers(dest, tables)

    print('Migration complete.')
    return 0


if __name__ == '__main__':
    sys.exit(main())


