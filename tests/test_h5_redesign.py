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
    soup = BeautifulSoup(html, "lxml")
    section = soup.find(attrs={"id": "step-bg"}) or soup.find(attrs={"data-step": "background"})
    assert section is not None


def test_step1_has_style_carousel():
    """Step 1 有风格轮播（横向滚动容器）"""
    html = _get_index_html()
    soup = BeautifulSoup(html, "lxml")
    carousel = soup.find(attrs={"id": "style-carousel"}) or soup.find(attrs={"class": "style-carousel"})
    assert carousel is not None


def test_step1_has_style_thumbnails():
    """Step 1 至少4个风格缩略图"""
    html = _get_index_html()
    soup = BeautifulSoup(html, "lxml")
    thumbs = soup.find_all(attrs={"class": "style-thumb"})
    assert len(thumbs) >= 4


def test_step1_has_large_preview():
    """Step 1 有大图预览区"""
    html = _get_index_html()
    soup = BeautifulSoup(html, "lxml")
    preview = soup.find(attrs={"id": "bg-preview"}) or soup.find(attrs={"class": "bg-preview"})
    assert preview is not None


def test_step2_upload_exists():
    """Step 2 确定人物（上传）区域存在"""
    html = _get_index_html()
    soup = BeautifulSoup(html, "lxml")
    section = soup.find(attrs={"id": "step-person"}) or soup.find(attrs={"data-step": "person"})
    assert section is not None


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
    soup = BeautifulSoup(html, "lxml")
    preview = soup.find(attrs={"id": "person-preview"}) or soup.find(attrs={"class": "person-preview"})
    assert preview is not None


def test_step3_text_exists():
    """Step 3 加文字区域存在"""
    html = _get_index_html()
    soup = BeautifulSoup(html, "lxml")
    section = soup.find(attrs={"id": "step-text"}) or soup.find(attrs={"data-step": "text"})
    assert section is not None


def test_step3_has_text_input():
    """Step 3 有文字输入框"""
    html = _get_index_html()
    soup = BeautifulSoup(html, "lxml")
    inp = soup.find("input", attrs={"id": "text-input"}) or soup.find("input", attrs={"name": "badge-text"})
    assert inp is not None


def test_step3_has_font_color_position_selectors():
    """Step 3 有字体/颜色/位置选择器"""
    html = _get_index_html()
    soup = BeautifulSoup(html, "lxml")
    font = soup.find("select", attrs={"id": "font-select"}) or soup.find(attrs={"id": "font-select"})
    color = soup.find("select", attrs={"id": "color-select"}) or soup.find(attrs={"id": "color-select"})
    pos = soup.find("select", attrs={"id": "position-select"}) or soup.find(attrs={"id": "position-select"})
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
    soup = BeautifulSoup(html, "lxml")
    section = soup.find(attrs={"id": "step-generate"}) or soup.find(attrs={"data-step": "generate"})
    assert section is not None


def test_step4_has_generate_button():
    """Step 4 有生成按钮"""
    html = _get_index_html()
    soup = BeautifulSoup(html, "lxml")
    btn = soup.find(attrs={"id": "btn-generate"}) or soup.find(attrs={"class": "btn-generate"})
    assert btn is not None


def test_step4_has_result_and_pickup():
    """Step 4 有结果区和取件号"""
    html = _get_index_html()
    soup = BeautifulSoup(html, "lxml")
    result = soup.find(attrs={"id": "result-preview"}) or soup.find(attrs={"class": "result-preview"})
    pickup = soup.find(attrs={"id": "pickup-code"}) or soup.find(attrs={"class": "pickup-display"})
    assert result is not None
    assert pickup is not None


def test_has_step_navigation():
    """有步骤导航指示器"""
    html = _get_index_html()
    soup = BeautifulSoup(html, "lxml")
    indicators = soup.find_all(attrs={"class": "step-indicator"})
    assert len(indicators) >= 4


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
