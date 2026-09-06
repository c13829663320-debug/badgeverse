# -*- coding: utf-8 -*-
"""
test_text_overlay_ui — 文字叠加 H5 交互测试
红绿循环 Phase 2-2：输入框+字体选择器+颜色选择器+位置选择器
"""
from bs4 import BeautifulSoup


def _get_index_html():
    import app as app_module
    with app_module.app.test_client() as c:
        return c.get("/").data.decode("utf-8")


def test_has_text_input():
    """文字输入框存在"""
    html = _get_index_html()
    soup = BeautifulSoup(html, "lxml")
    inp = soup.find("input", attrs={"id": "text-input"}) or \
          soup.find("input", attrs={"name": "badge-text"})
    assert inp is not None


def test_has_font_selector():
    """字体选择器存在"""
    html = _get_index_html()
    soup = BeautifulSoup(html, "lxml")
    sel = soup.find("select", attrs={"id": "font-select"}) or \
          soup.find(attrs={"id": "font-select"})
    assert sel is not None


def test_has_color_selector():
    """颜色选择器存在"""
    html = _get_index_html()
    soup = BeautifulSoup(html, "lxml")
    sel = soup.find("select", attrs={"id": "color-select"}) or \
          soup.find(attrs={"id": "color-select"})
    assert sel is not None


def test_has_position_selector():
    """位置选择器存在"""
    html = _get_index_html()
    soup = BeautifulSoup(html, "lxml")
    sel = soup.find("select", attrs={"id": "position-select"}) or \
          soup.find(attrs={"id": "position-select"})
    assert sel is not None


def test_font_selector_has_options():
    """字体选择器有多个选项"""
    html = _get_index_html()
    soup = BeautifulSoup(html, "lxml")
    sel = soup.find("select", attrs={"id": "font-select"}) or \
          soup.find(attrs={"id": "font-select"})
    if sel and sel.name == "select":
        options = sel.find_all("option")
        assert len(options) >= 3
    else:
        # 可能是按钮组
        btns = soup.find_all(attrs={"class": "font-option"})
        assert len(btns) >= 3


def test_color_selector_has_options():
    """颜色选择器有多个选项"""
    html = _get_index_html()
    soup = BeautifulSoup(html, "lxml")
    sel = soup.find("select", attrs={"id": "color-select"}) or \
          soup.find(attrs={"id": "color-select"})
    if sel and sel.name == "select":
        options = sel.find_all("option")
        assert len(options) >= 5
    else:
        btns = soup.find_all(attrs={"class": "color-option"})
        assert len(btns) >= 5


def test_position_selector_has_options():
    """位置选择器有多个选项"""
    html = _get_index_html()
    soup = BeautifulSoup(html, "lxml")
    sel = soup.find("select", attrs={"id": "position-select"}) or \
          soup.find(attrs={"id": "position-select"})
    if sel and sel.name == "select":
        options = sel.find_all("option")
        assert len(options) >= 3
    else:
        btns = soup.find_all(attrs={"class": "position-option"})
        assert len(btns) >= 3


def test_has_live_preview_area():
    """实时预览区域存在"""
    html = _get_index_html()
    soup = BeautifulSoup(html, "lxml")
    preview = soup.find(attrs={"id": "canvas-preview"}) or \
              soup.find(attrs={"id": "preview-canvas"}) or \
              soup.find(attrs={"class": "live-preview"})
    assert preview is not None
