# -*- coding: utf-8 -*-
"""
test_failure_logging — 失败日志模块测试
红绿循环 Phase 1-6：订单表 error 字段 + 独立错误日志表
"""
import os
import tempfile
import sqlite3


def _get_test_db():
    """创建临时测试数据库"""
    path = os.path.join(tempfile.gettempdir(), f"test_badgeverse_{os.getpid()}.sqlite3")
    if os.path.exists(path):
        os.remove(path)
    return path


def test_log_error_creates_entry():
    """log_error 创建错误日志条目"""
    from modules.failure_logger import FailureLogger
    db_path = _get_test_db()
    fl = FailureLogger(db_path)
    fl.log_error(order_id="BV-TEST-001", error_type="generation_failed",
                 error_detail="阶跃 API 超时")
    errors = fl.get_errors()
    assert len(errors) == 1
    assert errors[0]["order_id"] == "BV-TEST-001"
    assert errors[0]["error_type"] == "generation_failed"


def test_get_errors_returns_list():
    """get_errors 返回错误列表"""
    from modules.failure_logger import FailureLogger
    db_path = _get_test_db()
    fl = FailureLogger(db_path)
    fl.log_error("ORDER-1", "gen_failed", "timeout")
    fl.log_error("ORDER-2", "print_failed", "paper jam")
    errors = fl.get_errors()
    assert len(errors) == 2


def test_get_errors_by_order():
    """按订单 ID 查询错误"""
    from modules.failure_logger import FailureLogger
    db_path = _get_test_db()
    fl = FailureLogger(db_path)
    fl.log_error("ORDER-A", "gen_failed", "timeout")
    fl.log_error("ORDER-B", "print_failed", "jam")
    errors = fl.get_errors_by_order("ORDER-A")
    assert len(errors) == 1
    assert errors[0]["order_id"] == "ORDER-A"


def test_error_entry_has_timestamp():
    """错误日志包含时间戳"""
    from modules.failure_logger import FailureLogger
    db_path = _get_test_db()
    fl = FailureLogger(db_path)
    fl.log_error("ORDER-X", "test", "detail")
    errors = fl.get_errors()
    assert "created_at" in errors[0]


def test_error_entry_has_required_fields():
    """错误日志包含所有必需字段"""
    from modules.failure_logger import FailureLogger
    db_path = _get_test_db()
    fl = FailureLogger(db_path)
    fl.log_error("ORDER-Y", "test_type", "test detail")
    errors = fl.get_errors()
    e = errors[0]
    for key in ("id", "order_id", "error_type", "error_detail", "created_at"):
        assert key in e, f"缺少字段: {key}"


def test_clear_errors():
    """清理错误日志"""
    from modules.failure_logger import FailureLogger
    db_path = _get_test_db()
    fl = FailureLogger(db_path)
    fl.log_error("O1", "t", "d")
    fl.log_error("O2", "t", "d")
    assert len(fl.get_errors()) == 2
    fl.clear()
    assert len(fl.get_errors()) == 0


def test_get_error_summary():
    """获取错误汇总"""
    from modules.failure_logger import FailureLogger
    db_path = _get_test_db()
    fl = FailureLogger(db_path)
    fl.log_error("O1", "generation_failed", "d1")
    fl.log_error("O2", "generation_failed", "d2")
    fl.log_error("O3", "print_failed", "d3")
    summary = fl.get_summary()
    assert "total" in summary
    assert "by_type" in summary
    assert summary["total"] == 3
