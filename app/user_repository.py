import os
import psycopg2
import psycopg2.extras
from app.models import User


class PostgresUserRepository:
    """Same connection/cursor pattern as PostgresItemRepository."""

    def __init__(self):
        self.dsn = os.environ.get("DATABASE_URL")

    def _get_conn(self):
        return psycopg2.connect(self.dsn)

    def create(self, email, password_hash):
        conn = self._get_conn()
        try:
            with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cur:
                cur.execute(
                    "INSERT INTO users (email, password_hash) VALUES (%s, %s) RETURNING id, email, password_hash",
                    (email, password_hash)
                )
                row = cur.fetchone()
                conn.commit()
                return User(row["id"], row["email"], row["password_hash"])
        finally:
            conn.close()

    def get_by_email(self, email):
        conn = self._get_conn()
        try:
            with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cur:
                cur.execute(
                    "SELECT id, email, password_hash FROM users WHERE email = %s",
                    (email,)
                )
                row = cur.fetchone()
                if row:
                    return User(row["id"], row["email"], row["password_hash"])
                return None
        finally:
            conn.close()
