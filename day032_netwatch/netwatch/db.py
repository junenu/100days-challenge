import os
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv

load_dotenv()

_DDL = """
CREATE TABLE IF NOT EXISTS hosts (
    id SERIAL PRIMARY KEY,
    address VARCHAR(255) NOT NULL UNIQUE,
    name VARCHAR(255),
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS ping_results (
    id SERIAL PRIMARY KEY,
    host_id INTEGER REFERENCES hosts(id) ON DELETE CASCADE,
    success BOOLEAN NOT NULL,
    rtt_ms FLOAT,
    checked_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS traceroute_hops (
    id SERIAL PRIMARY KEY,
    host_id INTEGER REFERENCES hosts(id) ON DELETE CASCADE,
    trace_id VARCHAR(36) NOT NULL,
    hop_num INTEGER NOT NULL,
    hop_address VARCHAR(255),
    rtt_ms FLOAT,
    traced_at TIMESTAMP DEFAULT NOW()
);
"""


def connect() -> psycopg2.extensions.connection:
    return psycopg2.connect(
        host=os.getenv("POSTGRES_HOST", "localhost"),
        port=int(os.getenv("POSTGRES_PORT", "5432")),
        dbname=os.getenv("POSTGRES_DB", "netwatch"),
        user=os.getenv("POSTGRES_USER", "netwatch"),
        password=os.getenv("POSTGRES_PASSWORD", "netwatch"),
        cursor_factory=RealDictCursor,
    )


def init_db() -> None:
    with connect() as conn:
        with conn.cursor() as cur:
            cur.execute(_DDL)
        conn.commit()
