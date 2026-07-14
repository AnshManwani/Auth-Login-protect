import os
import psycopg2
import psycopg2.extras
from app.models import Item


class PostgresItemRepository:
    """Same interface as InMemoryItemRepository, backed by real Postgres."""

    def __init__(self):
        self.dsn = os.environ.get("DATABASE_URL")

    def _get_conn(self):
        return psycopg2.connect(self.dsn)

    def create(self, name, description, user_id=None):
        conn = self._get_conn()
        try:
            with conn.cursor() as cur:
                cur.execute(
                    "INSERT INTO items (name, description, user_id) VALUES (%s, %s, %s) RETURNING id",
                    (name, description, user_id)
                )
                new_id = cur.fetchone()[0]
                conn.commit()
                return Item(new_id, name, description, user_id)
        finally:
            conn.close()

    def get_all(self):
        conn = self._get_conn()
        try:
            with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cur:
                cur.execute("SELECT id, name, description, user_id FROM items ORDER BY id")
                rows = cur.fetchall()
                return [Item(r["id"], r["name"], r["description"], r["user_id"]) for r in rows]
        finally:
            conn.close()

    def get_by_id(self, item_id):
        conn = self._get_conn()
        try:
            with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cur:
                cur.execute("SELECT id, name, description, user_id FROM items WHERE id = %s", (item_id,))
                row = cur.fetchone()
                if row:
                    return Item(row["id"], row["name"], row["description"], row["user_id"])
                return None
        finally:
            conn.close()

    def delete(self, item_id):
        conn = self._get_conn()
        try:
            with conn.cursor() as cur:
                cur.execute("DELETE FROM items WHERE id = %s", (item_id,))
                deleted = cur.rowcount > 0
                conn.commit()
                return deleted
        finally:
            conn.close()