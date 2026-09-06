# -*- coding: utf-8 -*-
"""
BadgeVerse · 失败日志模块
订单错误独立日志表，支持按订单查询、类型汇总。
"""
import os
import sqlite3
import time
import uuid


class FailureLogger:
    """失败日志管理器"""

    def __init__(self, db_path):
        self._db_path = db_path
        self._init_db()

    def _init_db(self):
        conn = sqlite3.connect(self._db_path)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS error_logs (
                id TEXT PRIMARY KEY,
                order_id TEXT,
                error_type TEXT,
                error_detail TEXT,
                created_at REAL
            )
        """)
        conn.execute("CREATE INDEX IF NOT EXISTS idx_error_order ON error_logs(order_id)")
        conn.commit()
        conn.close()

    def log_error(self, order_id, error_type, error_detail):
        """记录一条错误日志"""
        conn = sqlite3.connect(self._db_path)
        log_id = uuid.uuid4().hex[:12]
        conn.execute(
            "INSERT INTO error_logs (id, order_id, error_type, error_detail, created_at) VALUES (?, ?, ?, ?, ?)",
            (log_id, str(order_id), str(error_type), str(error_detail), time.time())
        )
        conn.commit()
        conn.close()

    def get_errors(self, limit=100):
        """获取错误日志列表"""
        conn = sqlite3.connect(self._db_path)
        conn.row_factory = sqlite3.Row
        rows = conn.execute(
            "SELECT * FROM error_logs ORDER BY created_at DESC LIMIT ?", (limit,)
        ).fetchall()
        conn.close()
        return [dict(r) for r in rows]

    def get_errors_by_order(self, order_id):
        """按订单 ID 查询错误日志"""
        conn = sqlite3.connect(self._db_path)
        conn.row_factory = sqlite3.Row
        rows = conn.execute(
            "SELECT * FROM error_logs WHERE order_id = ? ORDER BY created_at DESC",
            (str(order_id),)
        ).fetchall()
        conn.close()
        return [dict(r) for r in rows]

    def get_summary(self):
        """获取错误汇总"""
        conn = sqlite3.connect(self._db_path)
        total = conn.execute("SELECT COUNT(*) FROM error_logs").fetchone()[0]
        rows = conn.execute(
            "SELECT error_type, COUNT(*) as cnt FROM error_logs GROUP BY error_type"
        ).fetchall()
        conn.close()
        by_type = {r[0]: r[1] for r in rows}
        return {"total": total, "by_type": by_type}

    def clear(self):
        """清空错误日志"""
        conn = sqlite3.connect(self._db_path)
        conn.execute("DELETE FROM error_logs")
        conn.commit()
        conn.close()
