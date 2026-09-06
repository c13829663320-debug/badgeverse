# -*- coding: utf-8 -*-
"""
BadgeVerse · 文字叠加模块
在圆面纸上渲染中英文混排文字，支持可选字体/颜色/位置。
自动适配字号防止文字超出圆形边界。
"""
import os
import math

from PIL import Image, ImageDraw, ImageFont

# Windows 系统字体目录
_FONT_DIR = os.path.join(os.environ.get("WINDIR", r"C:\Windows"), "Fonts")

# 可选字体（中英文兼容）
_FONTS = [
    {"name": "微软雅黑", "path": os.path.join(_FONT_DIR, "msyh.ttc")},
    {"name": "黑体", "path": os.path.join(_FONT_DIR, "simhei.ttf")},
    {"name": "宋体", "path": os.path.join(_FONT_DIR, "simsun.ttc")},
    {"name": "楷体", "path": os.path.join(_FONT_DIR, "simkai.ttf")},
    {"name": "等线", "path": os.path.join(_FONT_DIR, "Deng.ttf")},
]

# 可选颜色
_COLORS = [
    {"name": "白色", "value": (255, 255, 255)},
    {"name": "黑色", "value": (0, 0, 0)},
    {"name": "红色", "value": (255, 70, 70)},
    {"name": "蓝色", "value": (60, 130, 246)},
    {"name": "绿色", "value": (34, 197, 94)},
    {"name": "黄色", "value": (255, 215, 0)},
    {"name": "粉色", "value": (255, 105, 180)},
    {"name": "紫色", "value": (147, 112, 219)},
]

# 可选位置
_POSITIONS = [
    {"name": "底部", "value": "bottom"},
    {"name": "居中", "value": "center"},
    {"name": "顶部", "value": "top"},
]

# 圆形安全边界（相对于图片边长的百分比）
_SAFE_RADIUS_RATIO = 0.44  # 圆形半径的 44% 以内放文字


def get_available_fonts():
    """返回可用的字体列表（过滤掉系统不存在的字体）"""
    result = []
    for i, f in enumerate(_FONTS):
        if os.path.exists(f["path"]):
            result.append({"name": f["name"], "path": f["path"], "index": i})
    if not result:
        # 兜底：用 PIL 默认字体
        result.append({"name": "默认", "path": None, "index": 0})
    return result


def get_font(font_index, size=40):
    """通过索引获取字体对象"""
    fonts = get_available_fonts()
    if not fonts:
        return ImageFont.load_default()
    idx = min(font_index, len(fonts) - 1)
    path = fonts[idx]["path"]
    if path and os.path.exists(path):
        return ImageFont.truetype(path, size)
    return ImageFont.load_default()


def get_font_by_name(name, size=40):
    """通过名称获取字体对象"""
    fonts = get_available_fonts()
    for f in fonts:
        if f["name"] == name:
            if f["path"] and os.path.exists(f["path"]):
                return ImageFont.truetype(f["path"], size)
            return ImageFont.load_default()
    # 没找到就用第一个
    return get_font(0, size)


def get_available_colors():
    """返回可选颜色列表"""
    return _COLORS


def get_available_positions():
    """返回可选位置列表"""
    return _POSITIONS


def _get_color(name):
    for c in _COLORS:
        if c["name"] == name:
            return c["value"]
    return (0, 0, 0)


def _get_position_value(name):
    for p in _POSITIONS:
        if p["name"] == name:
            return p["value"]
    return "bottom"


def _fit_font_size(text, font_path, max_width, max_height, start_size=48):
    """自动缩小字号直到文字不超出边界"""
    size = start_size
    while size >= 12:
        if font_path and os.path.exists(font_path):
            font = ImageFont.truetype(font_path, size)
        else:
            font = ImageFont.load_default()
        bbox = font.getbbox(text)
        w = bbox[2] - bbox[0]
        h = bbox[3] - bbox[1]
        if w <= max_width and h <= max_height:
            return font, w, h
        size -= 2
    return font, w, h


def add_text_to_image(image, text, font_index=0, color_name="白色", position_name="底部"):
    """
    在图片上渲染文字。
    image: PIL.Image — 目标图片
    text: str — 要渲染的文字
    font_index: int — 字体索引
    color_name: str — 颜色名
    position_name: str — 位置名
    返回: PIL.Image（在原图上绘制）
    """
    if not text:
        return image

    draw = ImageDraw.Draw(image)
    w, h = image.size
    cx, cy = w // 2, h // 2
    radius = min(w, h) // 2
    max_text_width = int(radius * _SAFE_RADIUS_RATIO * 2)
    max_text_height = int(radius * _SAFE_RADIUS_RATIO * 0.6)

    fonts = get_available_fonts()
    font_path = fonts[min(font_index, len(fonts) - 1)]["path"] if fonts else None
    font, tw, th = _fit_font_size(text, font_path, max_text_width, max_text_height, start_size=48)

    color = _get_color(color_name)
    pos_val = _get_position_value(position_name)

    # 计算文字位置
    text_x = cx - tw // 2
    if pos_val == "top":
        text_y = int(cy - radius * 0.65) - th // 2
    elif pos_val == "center":
        text_y = cy - th // 2
    else:  # bottom
        text_y = int(cy + radius * 0.65) - th // 2

    # 绘制描边（增强可读性）
    stroke_w = max(1, tw // 100)
    draw.text((text_x, text_y), text, fill=color, font=font,
              stroke_width=stroke_w, stroke_fill=(0, 0, 0))

    return image
