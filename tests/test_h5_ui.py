# -*- coding: utf-8 -*-
"""
test_h5_ui — H5 前端结构断言
红绿循环 Phase 2-1：年轻潮流视觉语言，移动端自适应
"""
from bs4 import BeautifulSoup

# conftest.py 已注入依赖


def _get_index_html():
    import app as app_module
    with app_module.app.test_client() as c:
        resp = c.get("/")
        return resp.data.decode("utf-8")


def test_index_returns_200():
    """首页可正常访问"""
    import app as app_module
    with app_module.app.test_client() as c:
        resp = c.get("/")
        assert resp.status_code == 200


def test_has_mobile_viewport():
    """移动端 viewport meta 配置正确"""
    html = _get_index_html()
    soup = BeautifulSoup(html, "lxml")
    viewport = soup.find("meta", attrs={"name": "viewport"})
    assert viewport is not None
    assert "width=device-width" in viewport.get("content", "")


def test_has_upload_area():
    """上传区域存在"""
    html = _get_index_html()
    soup = BeautifulSoup(html, "lxml")
    file_input = soup.find("input", attrs={"type": "file"})
    assert file_input is not None


def test_has_style_selection():
    """风格选择存在"""
    html = _get_index_html()
    soup = BeautifulSoup(html, "lxml")
    # 至少有4个风格按钮/选项
    style_buttons = soup.find_all(attrs={"class": "style-btn"})
    style_options = soup.find_all("option")
    assert len(style_buttons) + len(style_options) >= 4


def test_has_generate_button():
    """生成按钮存在"""
    html = _get_index_html()
    soup = BeautifulSoup(html, "lxml")
    btn = soup.find(attrs={"id": "btn-generate"}) or soup.find(attrs={"class": "btn-generate"})
    assert btn is not None


def test_has_pickup_display():
    """取件号显示区域存在"""
    html = _get_index_html()
    assert "pickup" in html.lower()


def test_has_trendy_styling():
    """潮流视觉元素存在（渐变/动画/圆角等 CSS）"""
    html = _get_index_html()
    soup = BeautifulSoup(html, "lxml")
    style_tag = soup.find("style")
    assert style_tag is not None
    css = style_tag.text
    assert "gradient" in css or "linear-gradient" in css
    assert "border-radius" in css or "rounded" in css.lower()


def test_has_result_preview():
    """结果预览区域存在"""
    html = _get_index_html()
    assert "result" in html.lower()
