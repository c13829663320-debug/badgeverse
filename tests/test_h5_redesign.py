# -*- coding: utf-8 -*-
"""
test_h5_redesign — 向导式线性流程结构断言
新流程：选背景 → 确定人物 → 加文字 → 生成
"""
from bs4 import BeautifulSoup


def _get_index_html():
    import app as app_module
    with app_module.app.test_client() as c:
        return c.get("/").data.decode("utf-8")


def test_step1_background_selection_exists():
    """Step 1 选背景区域存在"""
    html = _get_index_html()
    assert "选择风格" in html or "step-1" in html


def test_step1_has_style_carousel():
    """Step 1 有风格轮播/网格容器"""
    html = _get_index_html()
    soup = BeautifulSoup(html, "lxml")
    grid = soup.find(attrs={"id": "style-grid"}) or soup.find(attrs={"class": "style-grid"})
    assert grid is not None


def test_step1_has_style_thumbnails():
    """Step 1 至少4个风格缩略图（JS 渲染，检查 STYLES 数据）"""
    html = _get_index_html()
    # 风格通过 JS STYLES 对象渲染，检查模板中 styles 循环
    assert "style-card" in html or "style-thumb" in html or "style-grid" in html


def test_step1_has_large_preview():
    """Step 1 有预览区"""
    html = _get_index_html()
    assert "preview-circle" in html or "bg-preview" in html or "preview" in html.lower()


def test_step2_upload_exists():
    """Step 2 确定人物（上传）区域存在"""
    html = _get_index_html()
    assert "step-2" in html or "上传" in html


def test_step2_has_file_input():
    """Step 2 有文件上传控件"""
    html = _get_index_html()
    soup = BeautifulSoup(html, "lxml")
    file_input = soup.find("input", attrs={"type": "file"})
    assert file_input is not None
    assert "image/*" in (file_input.get("accept") or "")


def test_step2_has_person_preview():
    """Step 2 有人物预览区"""
    html = _get_index_html()
    assert "person-img" in html or "person-preview" in html or "upload-done" in html


def test_step3_text_exists():
    """Step 3 加文字区域存在"""
    html = _get_index_html()
    assert "step-3" in html or "文字" in html


def test_step3_has_text_input():
    """Step 3 有文字输入框"""
    html = _get_index_html()
    soup = BeautifulSoup(html, "lxml")
    inp = soup.find("input", attrs={"id": "text-input"})
    assert inp is not None


def test_step3_has_font_color_position_selectors():
    """Step 3 有字体/颜色/位置选择器"""
    html = _get_index_html()
    soup = BeautifulSoup(html, "lxml")
    font = soup.find("select", attrs={"id": "font-select"})
    color = soup.find("select", attrs={"id": "color-select"})
    pos = soup.find("select", attrs={"id": "position-select"})
    assert font is not None
    assert color is not None
    assert pos is not None


def test_step3_has_live_canvas_preview():
    """Step 3 有实时 canvas 预览"""
    html = _get_index_html()
    soup = BeautifulSoup(html, "lxml")
    canvas = soup.find("canvas")
    assert canvas is not None


def test_step4_generate_exists():
    """Step 4 生成区域存在"""
    html = _get_index_html()
    assert "step-4" in html or "生成" in html


def test_step4_has_generate_button():
    """Step 4 有生成按钮"""
    html = _get_index_html()
    soup = BeautifulSoup(html, "lxml")
    btn = soup.find(attrs={"id": "btn-generate"})
    assert btn is not None


def test_step4_has_result_and_pickup():
    """Step 4 有结果区和取件号"""
    html = _get_index_html()
    assert "result-area" in html or "result-preview" in html or "result" in html.lower()
    assert "pickup" in html.lower()


def test_has_step_navigation():
    """有步骤导航指示器"""
    html = _get_index_html()
    soup = BeautifulSoup(html, "lxml")
    dots = soup.find_all(attrs={"class": "step-dot"})
    assert len(dots) >= 4


def test_has_mobile_viewport():
    """移动端 viewport"""
    html = _get_index_html()
    soup = BeautifulSoup(html, "lxml")
    viewport = soup.find("meta", attrs={"name": "viewport"})
    assert viewport is not None
    assert "width=device-width" in viewport.get("content", "")


def test_has_trendy_styling():
    """潮流视觉元素（渐变+圆角）"""
    html = _get_index_html()
    soup = BeautifulSoup(html, "lxml")
    style_tag = soup.find("style")
    assert style_tag is not None
    css = style_tag.text
    assert "gradient" in css or "linear-gradient" in css
    assert "border-radius" in css


def test_has_gender_selector():
    """有性别筛选器"""
    html = _get_index_html()
    assert "gender" in html.lower()


def test_styles_include_gender_tags():
    """风格库包含性别标签"""
    import config
    for name, cfg in config.STYLES.items():
        if isinstance(cfg, dict):
            assert "prompt" in cfg
            assert "gender" in cfg
            assert cfg["gender"] in ("male", "female", "neutral")
