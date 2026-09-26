"""SQLite persistence (stdlib sqlite3, WAL mode)."""
import json
import sqlite3
import threading
from datetime import datetime, timezone
from pathlib import Path

from config import DB_PATH
from security import hash_password

_lock = threading.Lock()
_conn: sqlite3.Connection | None = None

SCHEMA = """
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT UNIQUE NOT NULL,
    name TEXT NOT NULL,
    role TEXT NOT NULL,
    password_hash TEXT NOT NULL,
    created_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS reports (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    filename TEXT NOT NULL,
    company TEXT NOT NULL,
    period TEXT,
    uploaded_by TEXT NOT NULL,
    uploaded_at TEXT NOT NULL,
    pages INTEGER NOT NULL,
    metrics_json TEXT NOT NULL,
    analysis_json TEXT NOT NULL,
    pages_text_json TEXT NOT NULL,
    is_demo INTEGER NOT NULL DEFAULT 0
);
CREATE TABLE IF NOT EXISTS audit_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ts TEXT NOT NULL,
    actor TEXT NOT NULL,
    role TEXT NOT NULL,
    action TEXT NOT NULL,
    detail TEXT
);
"""


def get_conn() -> sqlite3.Connection:
    global _conn
    if _conn is None:
        Path(DB_PATH).parent.mkdir(parents=True, exist_ok=True)
        _conn = sqlite3.connect(DB_PATH, check_same_thread=False)
        _conn.row_factory = sqlite3.Row
        _conn.execute("PRAGMA journal_mode=WAL")
        _conn.executescript(SCHEMA)
        _conn.commit()
    return _conn


def seed_users() -> None:
    """Seed the three demo personas (prototype credentials, shown on login)."""
    users = [
        ("ceo@finsightx.demo", "Aria Mehta", "ceo", "demo1234"),
        ("analyst@finsightx.demo", "Rohan Iyer", "credit_analyst", "demo1234"),
        ("risk@finsightx.demo", "Kabir Shah", "risk_manager", "demo1234"),
    ]
    with _lock:
        c = get_conn()
        for email, name, role, pwd in users:
            row = c.execute("SELECT id FROM users WHERE email=?", (email,)).fetchone()
            if row is None:
                c.execute(
                    "INSERT INTO users (email, name, role, password_hash, created_at) VALUES (?,?,?,?,?)",
                    (email, name, role, hash_password(pwd), _now()),
                )
        c.commit()


def _now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


# ------------------------------------------------------------------ audit
def audit(actor: str, role: str, action: str, detail: str = "") -> None:
    with _lock:
        c = get_conn()
        c.execute(
            "INSERT INTO audit_log (ts, actor, role, action, detail) VALUES (?,?,?,?,?)",
            (_now(), actor, role, action, detail[:2000]),
        )
        c.commit()


def list_audit(limit: int = 200) -> list[dict]:
    rows = get_conn().execute(
        "SELECT ts, actor, role, action, detail FROM audit_log ORDER BY id DESC LIMIT ?", (limit,)
    ).fetchall()
    return [dict(r) for r in rows]


# ------------------------------------------------------------------ reports
def save_report(filename: str, company: str, period: str | None, uploaded_by: str,
                pages: int, metrics: dict, analysis: dict, pages_text: list[dict],
                is_demo: bool) -> int:
    with _lock:
        c = get_conn()
        cur = c.execute(
            """INSERT INTO reports
               (filename, company, period, uploaded_by, uploaded_at, pages,
                metrics_json, analysis_json, pages_text_json, is_demo)
               VALUES (?,?,?,?,?,?,?,?,?,?)""",
            (filename, company, period or "Unknown", uploaded_by, _now(), pages,
             json.dumps(metrics), json.dumps(analysis), json.dumps(pages_text),
             1 if is_demo else 0),
        )
        c.commit()
        return int(cur.lastrowid)


def list_reports() -> list[dict]:
    rows = get_conn().execute(
        """SELECT id, filename, company, period, uploaded_by, uploaded_at, pages, is_demo
           FROM reports ORDER BY id DESC"""
    ).fetchall()
    return [dict(r) for r in rows]


def get_report(report_id: int) -> dict | None:
    row = get_conn().execute("SELECT * FROM reports WHERE id=?", (report_id,)).fetchone()
    if row is None:
        return None
    d = dict(row)
    d["metrics"] = json.loads(d.pop("metrics_json"))
    d["analysis"] = json.loads(d.pop("analysis_json"))
    d["pages_text"] = json.loads(d.pop("pages_text_json"))
    return d
