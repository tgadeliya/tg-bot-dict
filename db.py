import sqlite3
from pathlib import Path

DB_PATH = Path("bot.db")


def init_db() -> None:
    """Create the definitions table if it doesn't exist."""
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS definitions (
            word TEXT PRIMARY KEY,
            definition TEXT NOT NULL
        )
        """
    )
    conn.commit()
    conn.close()


def get_definition(word: str) -> str | None:
    """Return a cached definition if available."""
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT definition FROM definitions WHERE word = ?", (word,))
    row = cur.fetchone()
    conn.close()
    return row[0] if row else None


def save_definition(word: str, definition: str) -> None:
    """Cache a definition for later use."""
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute(
        "INSERT OR REPLACE INTO definitions (word, definition) VALUES (?, ?)",
        (word, definition),
    )
    conn.commit()
    conn.close()


def count_definitions() -> int:
    """Return number of stored word definitions."""
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM definitions")
    (count,) = cur.fetchone()
    conn.close()
    return count


def get_all_definitions() -> list[tuple[str, str]]:
    """Return all stored word-definition pairs."""
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT word, definition FROM definitions")
    rows = cur.fetchall()
    conn.close()
    return rows
