"""SQLite access layer. An application-scoped connection, injectable in tests."""
import sqlite3
from contextlib import contextmanager
from pathlib import Path

SCHEMA = """
CREATE TABLE IF NOT EXISTS salespeople (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  name TEXT NOT NULL CHECK (length(trim(name)) > 0),
  monthly_target_cents INTEGER NOT NULL CHECK (monthly_target_cents >= 0)
);
CREATE TABLE IF NOT EXISTS orders (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  salesperson_id INTEGER NOT NULL REFERENCES salespeople(id),
  customer_name TEXT NOT NULL CHECK (length(trim(customer_name)) > 0),
  amount_cents INTEGER NOT NULL CHECK (amount_cents > 0),
  created_at TEXT NOT NULL DEFAULT (datetime('now'))
);
"""

def connect(path: str | Path = ':memory:') -> sqlite3.Connection:
    db = sqlite3.connect(str(path), check_same_thread=False)
    db.row_factory = sqlite3.Row
    db.execute('PRAGMA foreign_keys = ON')
    db.executescript(SCHEMA)
    return db

@contextmanager
def transaction(db: sqlite3.Connection):
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
