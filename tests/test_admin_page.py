# -*- coding: utf-8 -*-
"""
test_admin_page — 后台管理页结构断言
红绿循环 Phase 2-3：订单列表、看板、队列状态、日志、开关、按钮、滑块
"""
from bs4 import BeautifulSoup


def _get_admin_html():
    import app as app_module
    with app_module.app.test_client() as c:
        resp = c.get("/admin")
        assert resp.status_code == 200
        return resp.data.decode("utf-8")


def test_admin_returns_200():
    """管理页可正常访问"""
    import app as app_module
    with app_module.app.test_client() as c:
        assert c.get("/admin").status_code == 200


def test_has_dashboard_cards():
    """看板卡片存在"""
    html = _get_admin_html()
    soup = BeautifulSoup(html, "lxml")
    cards = soup.find_all(attrs={"class": "stat-card"})
    assert len(cards) >= 3


def test_has_order_table():
    """订单列表表格存在"""
    html = _get_admin_html()
    soup = BeautifulSoup(html, "lxml")
    table = soup.find("table", attrs={"id": "order-table"}) or \
            soup.find(attrs={"id": "order-list"})
    assert table is not None


def test_has_queue_status():
    """打印队列状态区存在"""
    html = _get_admin_html()
    soup = BeautifulSoup(html, "lxml")
    q = soup.find(attrs={"id": "queue-status"}) or \
        soup.find(attrs={"class": "queue-status"})
    assert q is not None


def test_has_error_log_area():
    """错误日志区存在"""
    html = _get_admin_html()
    soup = BeautifulSoup(html, "lxml")
    log = soup.find(attrs={"id": "error-log"}) or \
          soup.find(attrs={"class": "error-log"})
    assert log is not None


def test_has_offline_toggle():
    """断网开关存在"""
    html = _get_admin_html()
    soup = BeautifulSoup(html, "lxml")
    toggle = soup.find(attrs={"id": "offline-toggle"}) or \
             soup.find("input", attrs={"type": "checkbox"})
    assert toggle is not None


def test_has_reprint_button():
    """重打印按钮存在"""
    html = _get_admin_html()
    soup = BeautifulSoup(html, "lxml")
    btn = soup.find(attrs={"id": "btn-reprint"}) or \
          soup.find("button", attrs={"class": "reprint-btn"})
    assert btn is not None


def test_has_interval_slider():
    """限流间歇调节滑块存在"""
    html = _get_admin_html()
    soup = BeautifulSoup(html, "lxml")
    slider = soup.find("input", attrs={"type": "range"}) or \
             soup.find(attrs={"id": "interval-slider"})
    assert slider is not None
