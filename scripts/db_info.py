"""Step 03.1 demo: connect to the local Supabase Postgres and show the version and the extensions this project uses."""

import os

import psycopg

URL = os.environ.get("DATABASE_URL", "postgresql://postgres:postgres@127.0.0.1:54322/postgres")
WANTED = {"pgmq": "job queue", "pg_cron": "scheduled jobs", "pg_net": "HTTP calls from SQL", "vector": "embeddings (pgvector)"}

with psycopg.connect(URL) as conn:
    print(conn.execute("select version()").fetchone()[0])
    rows = conn.execute(
        """select name, default_version, installed_version from pg_available_extensions
           where name = any(%s) order by name""",
        (list(WANTED),),
    ).fetchall()
    print(f"\n{'extension':<10} {'available':<10} {'installed':<10} used for")
    for name, available, installed in rows:
        print(f"{name:<10} {available:<10} {installed or '-':<10} {WANTED[name]}")
    tables = conn.execute("select count(*) from pg_tables where schemaname = 'public'").fetchone()[0]
    print(f"\ntables in schema public: {tables}")
