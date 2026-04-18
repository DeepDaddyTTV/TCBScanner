from __future__ import annotations

import sqlite3
import threading
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


DEFAULT_NAMING_FORMAT = "{ChapterTitle}"


class Store:
    def __init__(self, db_path: Path) -> None:
        self.db_path = db_path
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._lock = threading.RLock()
        self._conn = sqlite3.connect(self.db_path, check_same_thread=False)
        self._conn.row_factory = sqlite3.Row
        self._conn.execute("PRAGMA foreign_keys = ON")
        self.init_db()

    def init_db(self) -> None:
        with self._lock, self._conn:
            self._conn.executescript(
                """
                PRAGMA journal_mode = WAL;

                CREATE TABLE IF NOT EXISTS series (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    source_url TEXT NOT NULL,
                    folder TEXT NOT NULL,
                    check_interval_minutes INTEGER NOT NULL DEFAULT 60,
                    enabled INTEGER NOT NULL DEFAULT 1,
                    backfill_existing INTEGER NOT NULL DEFAULT 0,
                    initialized INTEGER NOT NULL DEFAULT 0,
                    created_at TEXT NOT NULL,
                    last_checked_at TEXT,
                    last_error TEXT
                );

                CREATE TABLE IF NOT EXISTS chapters (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    series_id INTEGER NOT NULL REFERENCES series(id) ON DELETE CASCADE,
                    source_url TEXT NOT NULL,
                    chapter_key TEXT NOT NULL,
                    sort_key REAL NOT NULL DEFAULT 0,
                    display_title TEXT NOT NULL,
                    status TEXT NOT NULL DEFAULT 'pending',
                    cbz_path TEXT,
                    page_count INTEGER NOT NULL DEFAULT 0,
                    discovered_at TEXT NOT NULL,
                    downloaded_at TEXT,
                    error TEXT,
                    UNIQUE(series_id, source_url)
                );

                CREATE TABLE IF NOT EXISTS events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    series_id INTEGER REFERENCES series(id) ON DELETE CASCADE,
                    chapter_id INTEGER REFERENCES chapters(id) ON DELETE SET NULL,
                    level TEXT NOT NULL,
                    message TEXT NOT NULL,
                    created_at TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS settings (
                    key TEXT PRIMARY KEY,
                    value TEXT NOT NULL
                );
                """
            )
            self._ensure_column("series", "naming_format", "TEXT")
            self._conn.execute(
                """
                INSERT OR IGNORE INTO settings (key, value)
                VALUES ('default_naming_format', ?)
                """,
                (DEFAULT_NAMING_FORMAT,),
            )

    def _ensure_column(self, table: str, column: str, column_type: str) -> None:
        rows = self._conn.execute(f"PRAGMA table_info({table})").fetchall()
        if column not in {str(row["name"]) for row in rows}:
            self._conn.execute(f"ALTER TABLE {table} ADD COLUMN {column} {column_type}")

    def create_series(self, payload: dict[str, Any]) -> dict[str, Any]:
        now = utc_now()
        with self._lock, self._conn:
            cur = self._conn.execute(
                """
                INSERT INTO series (
                    title, source_url, folder, check_interval_minutes,
                    enabled, backfill_existing, initialized, created_at, naming_format
                )
                VALUES (?, ?, ?, ?, ?, ?, 0, ?, ?)
                """,
                (
                    payload["title"],
                    payload["source_url"],
                    payload["folder"],
                    int(payload["check_interval_minutes"]),
                    1 if payload.get("enabled", True) else 0,
                    1 if payload.get("backfill_existing", False) else 0,
                    now,
                    payload.get("naming_format") or None,
                ),
            )
            series_id = int(cur.lastrowid)
        self.add_event(series_id, None, "info", "Series added.")
        return self.get_series(series_id) or {}

    def list_series(self) -> list[dict[str, Any]]:
        with self._lock:
            rows = self._conn.execute(
                """
                SELECT
                    s.*,
                    COUNT(c.id) AS chapter_count,
                    SUM(CASE WHEN c.status = 'downloaded' THEN 1 ELSE 0 END) AS downloaded_count,
                    SUM(CASE WHEN c.status = 'pending' THEN 1 ELSE 0 END) AS pending_count,
                    SUM(CASE WHEN c.status = 'failed' THEN 1 ELSE 0 END) AS failed_count,
                    SUM(CASE WHEN c.status = 'skipped' THEN 1 ELSE 0 END) AS skipped_count
                FROM series s
                LEFT JOIN chapters c ON c.series_id = s.id
                GROUP BY s.id
                ORDER BY s.created_at DESC
                """
            ).fetchall()
        return [self._row_to_dict(row) for row in rows]

    def get_series(self, series_id: int) -> dict[str, Any] | None:
        with self._lock:
            row = self._conn.execute(
                """
                SELECT
                    s.*,
                    COUNT(c.id) AS chapter_count,
                    SUM(CASE WHEN c.status = 'downloaded' THEN 1 ELSE 0 END) AS downloaded_count,
                    SUM(CASE WHEN c.status = 'pending' THEN 1 ELSE 0 END) AS pending_count,
                    SUM(CASE WHEN c.status = 'failed' THEN 1 ELSE 0 END) AS failed_count,
                    SUM(CASE WHEN c.status = 'skipped' THEN 1 ELSE 0 END) AS skipped_count
                FROM series s
                LEFT JOIN chapters c ON c.series_id = s.id
                WHERE s.id = ?
                GROUP BY s.id
                """,
                (series_id,),
            ).fetchone()
        return self._row_to_dict(row) if row else None

    def update_series_source(self, series_id: int, source_url: str) -> None:
        with self._lock, self._conn:
            self._conn.execute(
                "UPDATE series SET source_url = ? WHERE id = ?",
                (source_url, series_id),
            )

    def set_series_enabled(self, series_id: int, enabled: bool) -> dict[str, Any] | None:
        with self._lock, self._conn:
            self._conn.execute(
                "UPDATE series SET enabled = ? WHERE id = ?",
                (1 if enabled else 0, series_id),
            )
        self.add_event(
            series_id,
            None,
            "info",
            "Monitoring enabled." if enabled else "Monitoring paused.",
        )
        return self.get_series(series_id)

    def set_series_naming_format(
        self,
        series_id: int,
        naming_format: str | None,
    ) -> dict[str, Any] | None:
        cleaned = " ".join((naming_format or "").strip().split())
        with self._lock, self._conn:
            self._conn.execute(
                "UPDATE series SET naming_format = ? WHERE id = ?",
                (cleaned or None, series_id),
            )
        self.add_event(series_id, None, "info", "Series naming format updated.")
        return self.get_series(series_id)

    def delete_series(self, series_id: int) -> None:
        with self._lock, self._conn:
            self._conn.execute("DELETE FROM series WHERE id = ?", (series_id,))

    def record_check_start(self, series_id: int) -> None:
        with self._lock, self._conn:
            self._conn.execute(
                "UPDATE series SET last_error = NULL WHERE id = ?",
                (series_id,),
            )

    def record_check_finish(self, series_id: int, error: str | None = None) -> None:
        with self._lock, self._conn:
            self._conn.execute(
                """
                UPDATE series
                SET last_checked_at = ?, last_error = ?
                WHERE id = ?
                """,
                (utc_now(), error, series_id),
            )

    def set_initialized(self, series_id: int) -> None:
        with self._lock, self._conn:
            self._conn.execute(
                "UPDATE series SET initialized = 1 WHERE id = ?",
                (series_id,),
            )

    def upsert_chapters(
        self,
        series_id: int,
        chapters: list[dict[str, Any]],
        status_for_new: str,
    ) -> list[dict[str, Any]]:
        created: list[dict[str, Any]] = []
        now = utc_now()
        with self._lock, self._conn:
            for chapter in chapters:
                cur = self._conn.execute(
                    """
                    INSERT OR IGNORE INTO chapters (
                        series_id, source_url, chapter_key, sort_key, display_title,
                        status, discovered_at
                    )
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        series_id,
                        chapter["url"],
                        chapter["chapter_key"],
                        float(chapter.get("sort_key") or 0),
                        chapter["title"],
                        status_for_new,
                        now,
                    ),
                )
                if cur.rowcount:
                    row = self._conn.execute(
                        "SELECT * FROM chapters WHERE id = ?",
                        (int(cur.lastrowid),),
                    ).fetchone()
                    created.append(self._row_to_dict(row))
        return created

    def list_chapters(self, series_id: int) -> list[dict[str, Any]]:
        with self._lock:
            rows = self._conn.execute(
                """
                SELECT *
                FROM chapters
                WHERE series_id = ?
                ORDER BY sort_key DESC, discovered_at DESC
                """,
                (series_id,),
            ).fetchall()
        return [self._row_to_dict(row) for row in rows]

    def pending_chapters(self, series_id: int | None = None) -> list[dict[str, Any]]:
        query = "SELECT * FROM chapters WHERE status = 'pending'"
        params: tuple[Any, ...] = ()
        if series_id is not None:
            query += " AND series_id = ?"
            params = (series_id,)
        query += " ORDER BY sort_key ASC, discovered_at ASC"
        with self._lock:
            rows = self._conn.execute(query, params).fetchall()
        return [self._row_to_dict(row) for row in rows]

    def get_chapter(self, chapter_id: int) -> dict[str, Any] | None:
        with self._lock:
            row = self._conn.execute(
                "SELECT * FROM chapters WHERE id = ?",
                (chapter_id,),
            ).fetchone()
        return self._row_to_dict(row) if row else None

    def set_chapter_status(
        self,
        chapter_id: int,
        status: str,
        *,
        cbz_path: str | None = None,
        page_count: int | None = None,
        error: str | None = None,
    ) -> None:
        downloaded_at = utc_now() if status == "downloaded" else None
        with self._lock, self._conn:
            self._conn.execute(
                """
                UPDATE chapters
                SET status = ?,
                    cbz_path = COALESCE(?, cbz_path),
                    page_count = COALESCE(?, page_count),
                    downloaded_at = COALESCE(?, downloaded_at),
                    error = ?
                WHERE id = ?
                """,
                (status, cbz_path, page_count, downloaded_at, error, chapter_id),
            )

    def mark_chapter_pending(self, chapter_id: int) -> dict[str, Any] | None:
        with self._lock, self._conn:
            self._conn.execute(
                """
                UPDATE chapters
                SET status = 'pending', error = NULL
                WHERE id = ? AND status IN ('failed', 'skipped')
                """,
                (chapter_id,),
            )
        return self.get_chapter(chapter_id)

    def mark_missing_pending(self, series_id: int) -> int:
        with self._lock, self._conn:
            cur = self._conn.execute(
                """
                UPDATE chapters
                SET status = 'pending', error = NULL
                WHERE series_id = ? AND status IN ('failed', 'skipped')
                """,
                (series_id,),
            )
            return int(cur.rowcount)

    def mark_selected_pending(self, series_id: int, chapter_ids: list[int]) -> int:
        clean_ids = sorted({int(chapter_id) for chapter_id in chapter_ids if int(chapter_id) > 0})
        if not clean_ids:
            return 0
        placeholders = ",".join("?" for _ in clean_ids)
        with self._lock, self._conn:
            cur = self._conn.execute(
                f"""
                UPDATE chapters
                SET status = 'pending', error = NULL
                WHERE series_id = ?
                  AND id IN ({placeholders})
                  AND status IN ('failed', 'skipped')
                """,
                (series_id, *clean_ids),
            )
            return int(cur.rowcount)

    def get_default_naming_format(self) -> str:
        return self.get_setting("default_naming_format") or DEFAULT_NAMING_FORMAT

    def get_setting(self, key: str) -> str | None:
        with self._lock:
            row = self._conn.execute(
                "SELECT value FROM settings WHERE key = ?",
                (key,),
            ).fetchone()
        return str(row["value"]) if row else None

    def set_setting(self, key: str, value: str) -> None:
        with self._lock, self._conn:
            self._conn.execute(
                """
                INSERT INTO settings (key, value)
                VALUES (?, ?)
                ON CONFLICT(key) DO UPDATE SET value = excluded.value
                """,
                (key, value),
            )

    def add_event(
        self,
        series_id: int | None,
        chapter_id: int | None,
        level: str,
        message: str,
    ) -> None:
        with self._lock, self._conn:
            self._conn.execute(
                """
                INSERT INTO events (series_id, chapter_id, level, message, created_at)
                VALUES (?, ?, ?, ?, ?)
                """,
                (series_id, chapter_id, level, message, utc_now()),
            )

    def list_events(self, limit: int = 100) -> list[dict[str, Any]]:
        with self._lock:
            rows = self._conn.execute(
                """
                SELECT e.*, s.title AS series_title, c.display_title AS chapter_title
                FROM events e
                LEFT JOIN series s ON s.id = e.series_id
                LEFT JOIN chapters c ON c.id = e.chapter_id
                ORDER BY e.id DESC
                LIMIT ?
                """,
                (limit,),
            ).fetchall()
        return [self._row_to_dict(row) for row in rows]

    def _row_to_dict(self, row: sqlite3.Row) -> dict[str, Any]:
        data = dict(row)
        for key in (
            "enabled",
            "backfill_existing",
            "initialized",
        ):
            if key in data:
                data[key] = bool(data[key])
        for key in (
            "chapter_count",
            "downloaded_count",
            "pending_count",
            "failed_count",
            "skipped_count",
        ):
            if key in data and data[key] is None:
                data[key] = 0
        return data
