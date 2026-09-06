# -*- coding: utf-8 -*-
"""
BadgeVerse · 订单管理模块
线程安全的订单创建、查询、统计。含 error 字段和取件号。
"""
import os
import sqlite3
import time
import uuid
import threading
import datetime


class OrderManager:
    """线程安全的订单管理器"""

    def __init__(self, db_path):
        self._db_path = db_path
        self._lock = threading.Lock()
        self._init_db()

    def _init_db(self):
        conn = sqlite3.connect(self._db_path)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS orders (
                id TEXT PRIMARY KEY,
                pickup_code TEXT,
                style TEXT,
                source_file TEXT,
                result_file TEXT,
                print_file TEXT,
                gen_ms INTEGER,
                error TEXT,
                status TEXT DEFAULT 'completed',
                created_at REAL
            )
        """)
        conn.execute("CREATE INDEX IF NOT EXISTS idx_orders_code ON orders(pickup_code)")
        conn.commit()
        conn.close()

    def create_order(self, style, source_file, result_file, gen_ms, error=None,
                     print_file=None):
        """创建订单，返回 pickup_code（线程安全）"""
        with self._lock:
            today = datetime.date.today().strftime("%Y%m%d")
            seq = uuid.uuid4().hex[:4].upper()
            pickup_code = f"BV-{today}-{seq}"
            order_id = uuid.uuid4().hex[:12]

            conn = sqlite3.connect(self._db_path)
            conn.execute(
                "INSERT INTO orders (id, pickup_code, style, source_file, result_file, "
                "print_file, gen_ms, error, status, created_at) "
                "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (order_id, pickup_code, style, source_file, result_file,
                 print_file, int(gen_ms), error, "completed", time.time())
            )
            conn.commit()
            conn.close()
            return pickup_code

    def get_order(self, pickup_code):
        """按取件号查询订单"""
        conn = sqlite3.connect(self._db_path)
        conn.row_factory = sqlite3.Row
        row = conn.execute(
            "SELECT * FROM orders WHERE pickup_code = ?", (pickup_code,)
        ).fetchone()
        conn.close()
        return dict(row) if row else None

    def get_all_orders(self, limit=100):
        """获取所有订单"""
        conn = sqlite3.connect(self._db_path)
        conn.row_factory = sqlite3.Row
        rows = conn.execute(
            "SELECT * FROM orders ORDER BY created_at DESC LIMIT ?", (limit,)
        ).fetchall()
        conn.close()
        return [dict(r) for r in rows]

    def get_stats(self):
        """获取统计"""
        conn = sqlite3.connect(self._db_path)
        total = conn.execute("SELECT COUNT(*) FROM orders").fetchone()[0]
        success = conn.execute(
            "SELECT COUNT(*) FROM orders WHERE error IS NULL OR error = ''"
        ).fetchone()[0]
        avg_gen = conn.execute(
            "SELECT AVG(gen_ms) FROM orders WHERE gen_ms > 0"
        ).fetchone()[0] or 0
        conn.close()
        return {
            "total": total,
            "success": success,
            "failed": total - success,
            "avg_gen_ms": int(avg_gen),
        }
