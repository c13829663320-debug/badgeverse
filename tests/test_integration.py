# -*- coding: utf-8 -*-
"""
test_integration — 全链路集成测试
Phase 3-1：上传→审核→生成→文字叠加→下单→打印队列→取件
"""
import os
import tempfile
from PIL import Image
from bs4 import BeautifulSoup

# conftest.py 已注入依赖


def _make_test_image(path):
    """生成一张有效测试图片"""
    img = Image.new("RGB", (400, 400), (100, 150, 200))
    img.save(path, "JPEG", quality=90)


def _setup_app():
    import app as app_module
    app_module.app.config["TESTING"] = True
    return app_module.app.test_client()


def test_full_pipeline_mock():
    """完整链路：上传→生成→下单→取件号（MOCK 模式，异步轮询）"""
    c = _setup_app()
    # 1. 上传
    tmp = os.path.join(tempfile.gettempdir(), "test_integration.jpg")
    _make_test_image(tmp)
    with open(tmp, "rb") as f:
        resp = c.post("/api/upload", data={"file": (f, "test.jpg")}, content_type="multipart/form-data")
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["ok"] is True
    file_id = data["file_id"]

    # 2. 提交生成任务（异步模式：返回 task_id）
    resp = c.post("/api/generate", json={
        "file_id": file_id, "style": "动漫",
        "text": "测试", "font_index": 0, "color_name": "白色", "position_name": "底部"
    })
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["ok"] is True
    task_id = data["task_id"]

    # 3. 轮询任务状态（MOCK 模式应该很快完成）
    import time
    result_url = None
    for _ in range(30):
        resp = c.get(f"/api/task/{task_id}")
        data = resp.get_json()
        if data["status"] == "done":
            result_url = data["result_url"]
            break
        time.sleep(0.5)

    assert result_url is not None

    # 3. 下单
    resp = c.post("/api/order", json={
        "style": "动漫", "result_file": result_url, "source_file": file_id, "gen_ms": 1000
    })
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["ok"] is True
    assert data["pickup_code"].startswith("BV-")

    # 4. 结果文件存在
    result_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        "generated", os.path.basename(result_url)
    )
    assert os.path.exists(result_path)
    result_img = Image.open(result_path)
    assert result_img.size[0] > 0 and result_img.size[1] > 0


def test_upload_rejected_no_file():
    """无文件上传被拒绝"""
    c = _setup_app()
    resp = c.post("/api/upload", data={})
    assert resp.status_code == 400


def test_generate_rejected_bad_style():
    """不存在的风格被拒绝"""
    c = _setup_app()
    resp = c.post("/api/generate", json={"file_id": "nonexistent", "style": "不存在的风格"})
    assert resp.status_code == 400


def test_health_returns_ok():
    """health 接口正常"""
    c = _setup_app()
    resp = c.get("/health")
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["ok"] is True


def test_admin_stats_accessible():
    """管理统计接口可访问"""
    c = _setup_app()
    resp = c.get("/api/admin/stats")
    assert resp.status_code == 200
    data = resp.get_json()
    assert "total" in data
    assert "queue" in data


def test_admin_queue_accessible():
    """管理队列接口可访问"""
    c = _setup_app()
    resp = c.get("/api/admin/queue")
    assert resp.status_code == 200


def test_offline_toggle_workflow():
    """断网开关切换工作流"""
    c = _setup_app()
    # 开启
    resp = c.post("/api/admin/offline", json={"offline": True})
    assert resp.status_code == 200
    assert resp.get_json()["offline"] is True
    # 关闭
    resp = c.post("/api/admin/offline", json={"offline": False})
    assert resp.get_json()["offline"] is False


def test_interval_adjustment():
    """限流间歇调节"""
    c = _setup_app()
    resp = c.post("/api/admin/interval", json={"seconds": 15})
    assert resp.status_code == 200
    assert resp.get_json()["interval_seconds"] == 15


def test_index_page_has_all_steps():
    """H5 页面包含所有步骤"""
    c = _setup_app()
    html = c.get("/").data.decode("utf-8")
    soup = BeautifulSoup(html, "lxml")
    # 检查步骤标题
    assert "选择风格" in html or "选风格" in html
    assert "上传" in html
    assert "文字" in html
    assert "生成" in html


def test_admin_page_has_all_sections():
    """管理页包含所有区域"""
    c = _setup_app()
    html = c.get("/admin").data.decode("utf-8")
    assert "管理后台" in html
    assert "打印队列" in html
    assert "控制面板" in html
    assert "订单列表" in html
    assert "错误日志" in html
