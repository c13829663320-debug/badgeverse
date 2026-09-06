# -*- coding: utf-8 -*-
"""
test_admin_api — 后台管理 API 测试
红绿循环 Phase 1-7：打印队列状态、断网开关、重打印、限流调节、错误日志查询
"""
import os
import tempfile
import json

# conftest.py 已注入依赖


def _setup_app():
    """创建测试用 app 实例"""
    import app as app_module
    app_module.app.config["TESTING"] = True
    app_module.app.config["MAX_CONTENT_LENGTH"] = 12 * 1024 * 1024
    return app_module.app.test_client()


def test_admin_queue_status():
    """GET /api/admin/queue 返回打印队列状态"""
    c = _setup_app()
    resp = c.get("/api/admin/queue")
    assert resp.status_code == 200
    data = resp.get_json()
    assert "queued" in data
    assert "done" in data
    assert "error" in data
    assert "total" in data


def test_admin_offline_toggle():
    """POST /api/admin/offline 切换断网模式"""
    c = _setup_app()
    resp = c.post("/api/admin/offline", json={"offline": True})
    assert resp.status_code == 200
    data = resp.get_json()
    assert data.get("offline") is True

    resp = c.post("/api/admin/offline", json={"offline": False})
    data = resp.get_json()
    assert data.get("offline") is False


def test_admin_interval_set():
    """POST /api/admin/interval 调节限流间歇"""
    c = _setup_app()
    resp = c.post("/api/admin/interval", json={"seconds": 10})
    assert resp.status_code == 200
    data = resp.get_json()
    assert data.get("interval_seconds") == 10


def test_admin_errors():
    """GET /api/admin/errors 返回错误日志列表"""
    c = _setup_app()
    resp = c.get("/api/admin/errors")
    assert resp.status_code == 200
    data = resp.get_json()
    assert isinstance(data, list)


def test_admin_reprint():
    """POST /api/admin/reprint 重打印"""
    c = _setup_app()
    resp = c.post("/api/admin/reprint", json={"item_id": "nonexistent"})
    assert resp.status_code == 200
    data = resp.get_json()
    assert data.get("ok") is False  # 不存在的条目应返回 ok=False


def test_admin_stats():
    """GET /api/admin/stats 返回统计数据"""
    c = _setup_app()
    resp = c.get("/api/admin/stats")
    assert resp.status_code == 200
    data = resp.get_json()
    assert "total" in data
    assert "success" in data
    assert "avg_gen_ms" in data
