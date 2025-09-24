import os
import sys
from typing import List
from sqlalchemy import create_engine, MetaData, Table, text
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


def copy_table(source_engine: Engine, dest_engine: Engine, table: Table) -> None:
    columns = [c.name for c in table.columns]
    select_sql = text(f"SELECT {', '.join(columns)} FROM {table.name}")
    insert_sql = text(
        f"INSERT INTO {table.name} ({', '.join(columns)}) VALUES ({', '.join(':'+c for c in columns)})"
    )

    with source_engine.connect() as s_conn:
        rows = s_conn.execute(select_sql).mappings().all()
        if not rows:
            return

    # bulk insert in chunks
    chunk_size = 1000
    with dest_engine.begin() as d_conn:
        for i in range(0, len(rows), chunk_size):
            chunk = rows[i : i + chunk_size]
            d_conn.execute(insert_sql, chunk)


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
    try:
        src_md.create_all(dest, checkfirst=True)
    except Exception as e:
        print(f'WARN: Could not auto-create tables on destination: {e}')

    # Disable triggers (best-effort)
    tables = list(src_md.sorted_tables)
    disable_triggers(dest, tables)

    try:
        for table in tables:
            print(f'Copying table: {table.name}')
            try:
                copy_table(source, dest, table)
            except Exception as e:
                print(f'ERROR copying {table.name}: {e}')
    finally:
        enable_triggers(dest, tables)

    print('Migration complete.')
    return 0


if __name__ == '__main__':
    sys.exit(main())


