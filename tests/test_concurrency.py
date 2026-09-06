# -*- coding: utf-8 -*-
"""
test_concurrency — 并发下单模块测试
红绿循环 Phase 1-5：多用户同时下单，阶跃 API 真正并发，线程安全
"""
import os
import tempfile
import threading
import sqlite3


def _get_test_db():
    path = os.path.join(tempfile.gettempdir(), f"test_concurrency_{os.getpid()}.sqlite3")
    if os.path.exists(path):
        os.remove(path)
    return path


def test_concurrent_orders_get_unique_ids():
    """3个并发下单各获得唯一订单号"""
    from modules.order_manager import OrderManager
    db_path = _get_test_db()
    om = OrderManager(db_path)
    results = []
    lock = threading.Lock()

    def place_order(i):
        oid = om.create_order(
            style="动漫",
            source_file=f"src_{i}.jpg",
            result_file=f"res_{i}.jpg",
            gen_ms=1000 * i
        )
        with lock:
            results.append(oid)

    threads = [threading.Thread(target=place_order, args=(i,)) for i in range(3)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    assert len(results) == 3
    assert len(set(results)) == 3  # 全部唯一


def test_concurrent_orders_all_persisted():
    """3个并发下单全部成功写入数据库"""
    from modules.order_manager import OrderManager
    db_path = _get_test_db()
    om = OrderManager(db_path)
    results = []

    def place_order(i):
        oid = om.create_order(
            style="赛博",
            source_file=f"src_{i}.jpg",
            result_file=f"res_{i}.jpg",
            gen_ms=2000
        )
        results.append(oid)

    threads = [threading.Thread(target=place_order, args=(i,)) for i in range(3)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    orders = om.get_all_orders()
    assert len(orders) == 3


def test_order_has_pickup_code():
    """订单有取件号"""
    from modules.order_manager import OrderManager
    db_path = _get_test_db()
    om = OrderManager(db_path)
    oid = om.create_order("动漫", "src.jpg", "res.jpg", 1500)
    order = om.get_order(oid)
    assert order is not None
    assert "pickup_code" in order
    assert order["pickup_code"].startswith("BV-")


def test_order_has_error_field():
    """订单表有 error 字段"""
    from modules.order_manager import OrderManager
    db_path = _get_test_db()
    om = OrderManager(db_path)
    oid = om.create_order("动漫", "src.jpg", "res.jpg", 1500, error="测试错误")
    order = om.get_order(oid)
    assert "error" in order


def test_order_stats_concurrent():
    """并发下单后 stats 正确"""
    from modules.order_manager import OrderManager
    db_path = _get_test_db()
    om = OrderManager(db_path)

    def place_order(i):
        om.create_order("动漫", f"src_{i}.jpg", f"res_{i}.jpg", 1500 + i * 100)

    threads = [threading.Thread(target=place_order, args=(i,)) for i in range(5)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    stats = om.get_stats()
    assert stats["total"] == 5
    assert stats["success"] == 5
