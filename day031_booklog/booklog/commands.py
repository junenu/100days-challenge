from __future__ import annotations

import datetime
from typing import Optional

import psycopg2

from .models import Book

_COL_WIDTHS = (4, 32, 20, 12, 6, 8, 5)
_HEADER = f"{'ID':<4}  {'タイトル':<32}  {'著者':<20}  {'ジャンル':<12}  {'ページ':>6}  {'状態':<8}  {'評価':<5}"
_SEP = "-" * (sum(_COL_WIDTHS) + len(_COL_WIDTHS) * 2)


def _fmt_row(b: Book) -> str:
    title = b.title[:30] + ".." if len(b.title) > 30 else b.title
    author = b.author[:18] + ".." if len(b.author) > 18 else b.author
    genre = (b.genre or "")[:10]
    pages = str(b.pages) if b.pages else "—"
    return (
        f"{b.id:<4}  {title:<32}  {author:<20}  {genre:<12}  "
        f"{pages:>6}  {b.status_label():<8}  {b.rating_stars():<5}"
    )


def cmd_add(
    conn: psycopg2.extensions.connection,
    title: str,
    author: str,
    genre: Optional[str],
    pages: Optional[int],
    status: str,
) -> None:
    sql = """
        INSERT INTO books (title, author, genre, pages, status)
        VALUES (%s, %s, %s, %s, %s)
        RETURNING id
    """
    with conn.cursor() as cur:
        cur.execute(sql, (title, author, genre, pages, status))
        row = cur.fetchone()
    conn.commit()
    print(f"追加しました (id={row['id']}): {title} / {author}")


def cmd_list(
    conn: psycopg2.extensions.connection,
    status: Optional[str],
    genre: Optional[str],
) -> None:
    conditions = []
    params: list = []
    if status:
        conditions.append("status = %s")
        params.append(status)
    if genre:
        conditions.append("genre ILIKE %s")
        params.append(f"%{genre}%")

    where = ("WHERE " + " AND ".join(conditions)) if conditions else ""
    sql = f"SELECT * FROM books {where} ORDER BY created_at DESC"

    with conn.cursor() as cur:
        cur.execute(sql, params)
        rows = cur.fetchall()

    if not rows:
        print("該当する本がありません。")
        return

    books = [Book.from_row(dict(r)) for r in rows]
    print(_HEADER)
    print(_SEP)
    for b in books:
        print(_fmt_row(b))
    print(f"\n合計: {len(books)} 冊")


def cmd_review(
    conn: psycopg2.extensions.connection,
    book_id: int,
    rating: Optional[int],
    notes: Optional[str],
    status: Optional[str],
) -> None:
    updates: list[str] = []
    params: list = []

    if rating is not None:
        updates.append("rating = %s")
        params.append(rating)
    if notes is not None:
        updates.append("notes = %s")
        params.append(notes)
    if status is not None:
        updates.append("status = %s")
        params.append(status)
        if status == "reading":
            updates.append("started_at = %s")
            params.append(datetime.date.today())
        elif status == "read":
            updates.append("finished_at = %s")
            params.append(datetime.date.today())

    if not updates:
        print("更新する項目がありません。--rating / --notes / --status を指定してください。")
        return

    params.append(book_id)
    sql = f"UPDATE books SET {', '.join(updates)} WHERE id = %s RETURNING title"

    with conn.cursor() as cur:
        cur.execute(sql, params)
        row = cur.fetchone()

    if row is None:
        print(f"id={book_id} の本が見つかりません。")
        conn.rollback()
        return

    conn.commit()
    print(f"更新しました: {row['title']}")


def cmd_show(conn: psycopg2.extensions.connection, book_id: int) -> None:
    with conn.cursor() as cur:
        cur.execute("SELECT * FROM books WHERE id = %s", (book_id,))
        row = cur.fetchone()

    if row is None:
        print(f"id={book_id} の本が見つかりません。")
        return

    b = Book.from_row(dict(row))
    print(f"ID      : {b.id}")
    print(f"タイトル: {b.title}")
    print(f"著者    : {b.author}")
    print(f"ジャンル: {b.genre or '—'}")
    print(f"ページ数: {b.pages or '—'}")
    print(f"状態    : {b.status_label()}")
    print(f"評価    : {b.rating_stars()}")
    print(f"開始日  : {b.started_at or '—'}")
    print(f"完了日  : {b.finished_at or '—'}")
    print(f"メモ    :\n{b.notes or '（なし）'}")


def cmd_delete(conn: psycopg2.extensions.connection, book_id: int) -> None:
    with conn.cursor() as cur:
        cur.execute("DELETE FROM books WHERE id = %s RETURNING title", (book_id,))
        row = cur.fetchone()

    if row is None:
        print(f"id={book_id} の本が見つかりません。")
        conn.rollback()
        return

    conn.commit()
    print(f"削除しました: {row['title']}")


def cmd_stats(conn: psycopg2.extensions.connection) -> None:
    sql_counts = """
        SELECT status, COUNT(*) AS cnt
        FROM books
        GROUP BY status
        ORDER BY status
    """
    sql_genres = """
        SELECT COALESCE(genre, '未分類') AS genre, COUNT(*) AS cnt
        FROM books
        GROUP BY genre
        ORDER BY cnt DESC
        LIMIT 5
    """
    sql_avg = "SELECT ROUND(AVG(rating), 2) AS avg_rating FROM books WHERE rating IS NOT NULL"

    with conn.cursor() as cur:
        cur.execute(sql_counts)
        counts = {r["status"]: r["cnt"] for r in cur.fetchall()}

        cur.execute(sql_genres)
        genres = cur.fetchall()

        cur.execute(sql_avg)
        avg_row = cur.fetchone()

    labels = {"want": "積読", "reading": "読書中", "read": "読了"}
    total = sum(counts.values())

    print("=== 読書統計 ===")
    print(f"合計冊数 : {total}")
    for key, label in labels.items():
        print(f"  {label:<6}: {counts.get(key, 0)}")

    avg = avg_row["avg_rating"] if avg_row["avg_rating"] else "—"
    print(f"平均評価 : {avg}")

    print("\nジャンル TOP5:")
    for row in genres:
        print(f"  {row['genre']:<16}: {row['cnt']} 冊")
