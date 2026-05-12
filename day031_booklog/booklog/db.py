import os
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv

load_dotenv()

_DSN = (
    f"host={os.getenv('POSTGRES_HOST', 'localhost')} "
    f"port={os.getenv('POSTGRES_PORT', '5432')} "
    f"dbname={os.getenv('POSTGRES_DB', 'booklog')} "
    f"user={os.getenv('POSTGRES_USER', 'booklog')} "
    f"password={os.getenv('POSTGRES_PASSWORD', 'booklog')}"
)

_DDL = """
CREATE TABLE IF NOT EXISTS books (
    id          SERIAL PRIMARY KEY,
    title       TEXT NOT NULL,
    author      TEXT NOT NULL,
    genre       TEXT,
    pages       INTEGER,
    status      TEXT NOT NULL DEFAULT 'want'
                    CHECK (status IN ('want', 'reading', 'read')),
    rating      INTEGER CHECK (rating BETWEEN 1 AND 5),
    notes       TEXT,
    started_at  DATE,
    finished_at DATE,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
"""


def connect() -> psycopg2.extensions.connection:
    try:
        conn = psycopg2.connect(_DSN, cursor_factory=RealDictCursor)
        return conn
    except psycopg2.OperationalError as e:
        raise SystemExit(f"DB 接続失敗: {e}\ndocker compose up -d を実行してください。") from e


def migrate(conn: psycopg2.extensions.connection) -> None:
    with conn.cursor() as cur:
        cur.execute(_DDL)
    conn.commit()
