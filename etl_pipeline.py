

import sqlite3
import time
import logging
import requests
import schedule
from datetime import datetime, timezone
from typing import Optional


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
log = logging.getLogger(__name__)


API_URL    = "https://jsonplaceholder.typicode.com/posts"
DB_PATH    = "posts.db"
MAX_RETRY  = 3          
BACKOFF    = 2          



def fetch_posts(url: str = API_URL) -> list[dict]:
    """
    Загружает посты из API.
    При сетевых / серверных ошибках делает до MAX_RETRY попыток
    с экспоненциальной задержкой: 2s → 4s → 8s.
    """
    for attempt in range(1, MAX_RETRY + 1):
        try:
            log.info(f"[Extract] Попытка {attempt}/{MAX_RETRY} → {url}")
            response = requests.get(url, timeout=10)
            response.raise_for_status()        # 4xx / 5xx → HTTPError
            data = response.json()
            log.info(f"[Extract] Получено записей: {len(data)}")
            return data

        except requests.exceptions.HTTPError as exc:
            log.warning(f"[Extract] HTTP ошибка: {exc}")
        except requests.exceptions.ConnectionError as exc:
            log.warning(f"[Extract] Нет соединения: {exc}")
        except requests.exceptions.Timeout:
            log.warning("[Extract] Превышен таймаут запроса")
        except Exception as exc:
            log.error(f"[Extract] Неожиданная ошибка: {exc}")

        if attempt < MAX_RETRY:
            wait = BACKOFF ** attempt          # 2, 4, 8 секунд
            log.info(f"[Extract] Ждём {wait}s перед следующей попыткой…")
            time.sleep(wait)

    raise RuntimeError(f"Не удалось получить данные после {MAX_RETRY} попыток")



def transform(
    raw: list[dict],
    last_id: int = 0,
    timestamp: Optional[str] = None,
) -> list[dict]:
    
    if timestamp is None:
        timestamp = datetime.now(timezone.utc).isoformat()

    result = []
    for post in raw:
        if post["id"] <= last_id:
            continue                          
        result.append({
            "userId":    post["userId"],
            "id":        post["id"],
            "title":     post["title"].upper(),
            "body":      post["body"],
            "timestamp": timestamp,
        })

    log.info(
        f"[Transform] Новых записей после фильтра (last_id={last_id}): {len(result)}"
    )
    return result



def get_last_loaded_id(conn: sqlite3.Connection) -> int:
    
    row = conn.execute("SELECT MAX(id) FROM posts").fetchone()
    return row[0] if row[0] is not None else 0


def init_db(conn: sqlite3.Connection) -> None:
    
    conn.execute("""
        CREATE TABLE IF NOT EXISTS posts (
            id        INTEGER PRIMARY KEY,
            userId    INTEGER NOT NULL,
            title     TEXT    NOT NULL,
            body      TEXT    NOT NULL,
            timestamp TEXT    NOT NULL
        )
    """)
    conn.commit()


def load(records: list[dict], db_path: str = DB_PATH) -> int:
    """
    Загружает список записей в SQLite.
    Использует INSERT OR IGNORE чтобы избежать дублирования.
    Возвращает количество реально вставленных строк.
    """
    if not records:
        log.info("[Load] Нет новых записей для вставки")
        return 0

    with sqlite3.connect(db_path) as conn:
        init_db(conn)
        cursor = conn.executemany(
            """
            INSERT OR IGNORE INTO posts (id, userId, title, body, timestamp)
            VALUES (:id, :userId, :title, :body, :timestamp)
            """,
            records,
        )
        conn.commit()
        inserted = cursor.rowcount
        log.info(f"[Load] Вставлено {inserted} новых записей в {db_path}")
        return inserted




def run_pipeline(db_path: str = DB_PATH) -> None:
    """Полный ETL-цикл: Extract → Transform → Load."""
    log.info("=" * 60)
    log.info("Запуск ETL pipeline")

    # Узнаём последний загруженный id (инкрементальность)
    with sqlite3.connect(db_path) as conn:
        init_db(conn)
        last_id = get_last_loaded_id(conn)
    log.info(f"[Pipeline] Последний загруженный id: {last_id}")

    # Extract
    raw = fetch_posts()

    # Transform
    records = transform(raw, last_id=last_id)

    # Load
    load(records, db_path=db_path)

    log.info("ETL pipeline завершён")
    log.info("=" * 60)



def start_scheduler() -> None:
    """Запускает pipeline сразу и затем каждые 5 минут."""
    log.info("Планировщик запущен. Интервал: каждые 5 минут.")
    run_pipeline()                              # первый запуск немедленно
    schedule.every(5).minutes.do(run_pipeline)

    while True:
        schedule.run_pending()
        time.sleep(10)                          # проверяем расписание каждые 10с



if __name__ == "__main__":
    start_scheduler()
    
    
import sqlite3
conn = sqlite3.connect(r"C:\Users\Владелец\Downloads\data storage\posts.db")
rows = conn.execute("SELECT * FROM posts").fetchall()
for r in rows: print(r)