import os
import sqlite3
import random
import string
import time

class ProductDB:
    def __init__(self, db_path=None):
        self.db_path = db_path or os.path.join(os.getcwd(), "MyProduct.db")
        self._ensure_db()

    def _connect(self):
        return sqlite3.connect(self.db_path)

    def _ensure_db(self):
        with self._connect() as conn:
            cur = conn.cursor()
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS Products (
                    productID INTEGER PRIMARY KEY,
                    productName TEXT NOT NULL,
                    productPrice INTEGER NOT NULL
                )
                """
            )
            conn.commit()

    def insert(self, productID, productName, productPrice):
        with self._connect() as conn:
            cur = conn.cursor()
            try:
                cur.execute(
                    "INSERT INTO Products (productID, productName, productPrice) VALUES (?, ?, ?)",
                    (productID, productName, productPrice),
                )
                conn.commit()
                return True
            except sqlite3.IntegrityError:
                return False

    def bulk_insert(self, total=100_000, start_id=1, batch_size=1000, name_prefix="Product"):
        """
        빠른 대량 삽입: total 개수 생성. batch_size 단위로 커밋.
        각 항목: (productID, productName, productPrice)
        """
        start_time = time.time()
        inserted = 0
        with self._connect() as conn:
            cur = conn.cursor()
            for batch_start in range(start_id, start_id + total, batch_size):
                batch = []
                for i in range(batch_start, min(batch_start + batch_size, start_id + total)):
                    pid = i
                    pname = f"{name_prefix}_{pid}"
                    pprice = random.randint(100, 10000)
                    batch.append((pid, pname, pprice))
                cur.executemany(
                    "INSERT OR IGNORE INTO Products (productID, productName, productPrice) VALUES (?, ?, ?)",
                    batch,
                )
                conn.commit()
                inserted += len(batch)
        elapsed = time.time() - start_time
        return {"inserted": inserted, "elapsed_seconds": elapsed}

    def update(self, productID, productName=None, productPrice=None):
        if productName is None and productPrice is None:
            return False
        parts = []
        params = []
        if productName is not None:
            parts.append("productName = ?")
            params.append(productName)
        if productPrice is not None:
            parts.append("productPrice = ?")
            params.append(productPrice)
        params.append(productID)
        sql = f"UPDATE Products SET {', '.join(parts)} WHERE productID = ?"
        with self._connect() as conn:
            cur = conn.cursor()
            cur.execute(sql, params)
            conn.commit()
            return cur.rowcount > 0

    def delete(self, productID):
        with self._connect() as conn:
            cur = conn.cursor()
            cur.execute("DELETE FROM Products WHERE productID = ?", (productID,))
            conn.commit()
            return cur.rowcount > 0

    def select(self, productID=None, limit=None, offset=None):
        with self._connect() as conn:
            cur = conn.cursor()
            if productID is not None:
                cur.execute("SELECT productID, productName, productPrice FROM Products WHERE productID = ?", (productID,))
                return cur.fetchone()
            sql = "SELECT productID, productName, productPrice FROM Products"
            params = []
            if limit is not None:
                sql += " LIMIT ?"
                params.append(limit)
                if offset is not None:
                    sql += " OFFSET ?"
                    params.append(offset)
            cur.execute(sql, params)
            return cur.fetchall()

    def count(self):
        with self._connect() as conn:
            cur = conn.cursor()
            cur.execute("SELECT COUNT(*) FROM Products")
            return cur.fetchone()[0]

if __name__ == "__main__":
    # 간단 사용 예: 데이터베이스 생성 및 100,000건 샘플 데이터 삽입
    db = ProductDB()  # MyProduct.db 생성
    print("DB 파일:", db.db_path)
    existing = db.count()
    print("기존 레코드 수:", existing)
    if existing < 100_000:
        to_add = 100_000 - existing
        print(f"{to_add}개 레코드 삽입 시작...")
        result = db.bulk_insert(total=to_add, start_id=existing + 1, batch_size=5000)
        print("삽입 완료:", result)
    print("총 레코드 수:", db.count())