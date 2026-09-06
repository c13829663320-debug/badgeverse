# -*- coding: utf-8 -*-
"""
test_text_overlay — 文字叠加模块测试
红绿循环 Phase 1-2：中英文混排渲染到圆面纸，可选字体/颜色/位置
"""
import os
import sys
import io

# conftest.py 已注入依赖


def test_get_available_fonts():
    """get_available_fonts 返回非空字体列表"""
    from modules.text_overlay import get_available_fonts
    fonts = get_available_fonts()
    assert isinstance(fonts, list)
    assert len(fonts) >= 3
    for f in fonts:
        assert "name" in f
        assert "path" in f


def test_get_font_returns_valid():
    """get_font 返回可用的 ImageFont 对象"""
    from modules.text_overlay import get_font
    from PIL import ImageFont
    font = get_font(0, size=40)
    assert font is not None
    assert isinstance(font, ImageFont.FreeTypeFont)


def test_get_font_by_name():
    """通过名称获取字体"""
    from modules.text_overlay import get_font_by_name, get_available_fonts
    fonts = get_available_fonts()
    name = fonts[0]["name"]
    font = get_font_by_name(name, size=30)
    assert font is not None


def test_available_colors():
    """get_available_colors 返回颜色列表"""
    from modules.text_overlay import get_available_colors
    colors = get_available_colors()
    assert isinstance(colors, list)
    assert len(colors) >= 5
    assert "白色" in [c["name"] for c in colors]
    assert "黑色" in [c["name"] for c in colors]


def test_available_positions():
    """get_available_positions 返回位置列表"""
    from modules.text_overlay import get_available_positions
    positions = get_available_positions()
    assert isinstance(positions, list)
    assert len(positions) >= 3
    pos_names = [p["name"] for p in positions]
    assert "底部" in pos_names
    assert "居中" in pos_names
    assert "顶部" in pos_names


def test_add_text_returns_image():
    """add_text_to_image 返回 PIL Image"""
    from modules.text_overlay import add_text_to_image
    from PIL import Image
    img = Image.new("RGB", (826, 826), (255, 255, 255))
    result = add_text_to_image(img, "测试", font_index=0, color_name="黑色", position_name="底部")
    assert isinstance(result, Image.Image)


def test_add_text_changes_image():
    """add_text_to_image 后图片发生了变化（文字被实际绘制）"""
    from modules.text_overlay import add_text_to_image
    from PIL import Image
    img = Image.new("RGB", (826, 826), (255, 255, 255))
    original_bytes = img.tobytes()
    result = add_text_to_image(img, "吧唧星球", font_index=0, color_name="黑色", position_name="底部")
    assert result.tobytes() != original_bytes


def test_chinese_text():
    """中文字符渲染"""
    from modules.text_overlay import add_text_to_image
    from PIL import Image
    img = Image.new("RGB", (826, 826), (255, 255, 255))
    result = add_text_to_image(img, "吧唧星球", font_index=0, color_name="红色", position_name="居中")
    assert result is not None


def test_english_text():
    """英文字符渲染"""
    from modules.text_overlay import add_text_to_image
    from PIL import Image
    img = Image.new("RGB", (826, 826), (255, 255, 255))
    result = add_text_to_image(img, "BadgeVerse", font_index=0, color_name="黑色", position_name="顶部")
    assert result is not None


def test_mixed_text():
    """中英文混排"""
    from modules.text_overlay import add_text_to_image
    from PIL import Image
    img = Image.new("RGB", (826, 826), (255, 255, 255))
    result = add_text_to_image(img, "BadgeVerse 吧唧", font_index=0, color_name="黑色", position_name="底部")
    assert result is not None


def test_long_text_truncated():
    """过长文字不超出边界（自动缩小字号）"""
    from modules.text_overlay import add_text_to_image
    from PIL import Image
    img = Image.new("RGB", (400, 400), (255, 255, 255))
    long_text = "这是一段非常非常非常长的文字用来测试是否会超出圆形边界区域"
    result = add_text_to_image(img, long_text, font_index=0, color_name="黑色", position_name="底部")
    assert result is not None


def test_all_positions():
    """所有位置都能正常渲染"""
    from modules.text_overlay import add_text_to_image, get_available_positions
    from PIL import Image
    img = Image.new("RGB", (826, 826), (255, 255, 255))
    for pos in get_available_positions():
        result = add_text_to_image(img, "测试", font_index=0, color_name="黑色", position_name=pos["name"])
        assert result is not None


def test_all_colors():
    """所有颜色都能正常渲染"""
    from modules.text_overlay import add_text_to_image, get_available_colors
    from PIL import Image
    img = Image.new("RGB", (826, 826), (255, 255, 255))
    for color in get_available_colors():
        result = add_text_to_image(img, "测试", font_index=0, color_name=color["name"], position_name="底部")
        assert result is not None
