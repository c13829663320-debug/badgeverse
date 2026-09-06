# -*- coding: utf-8 -*-
"""
BadgeVerse · 断网兜底模块
活动主题图样走数字通道（圆裁→排队→静默打印），后台开关切换。
"""
import os
import glob
import uuid

from PIL import Image, ImageDraw

import config

# 主题图样目录（可配置）
_THEME_DIR = os.environ.get("BADGE_THEME_DIR", "")


def get_fallback_images():
    """返回可用的活动主题图样列表"""
    theme_dir = _THEME_DIR or os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "themes")
    images = []
    if os.path.isdir(theme_dir):
        for f in sorted(glob.glob(os.path.join(theme_dir, "*.png"))) + \
                    sorted(glob.glob(os.path.join(theme_dir, "*.jpg"))):
            images.append({"name": os.path.splitext(os.path.basename(f))[0], "path": f})
    if not images:
        # 兜底：生成一张纯色活动主题图
        images.append({"name": "BadgeVerse 活动", "path": None})
    return images


def _generate_placeholder_image(name="BadgeVerse"):
    """生成一张临时活动主题图样"""
    img = Image.new("RGB", (826, 826), (255, 105, 180))  # 粉色
    draw = ImageDraw.Draw(img)
    draw.text((200, 380), name, fill=(255, 255, 255))
    path = os.path.join(config.UPLOAD_DIR, f"fallback_{uuid.uuid4().hex[:8]}.jpg")
    img.save(path, "JPEG", quality=95)
    return path


class OfflineFallback:
    """断网兜底管理"""

    def __init__(self):
        self._offline = False
        self._theme_dir = _THEME_DIR

    def set_theme_dir(self, path):
        self._theme_dir = path

    def is_offline(self):
        return self._offline

    def set_offline(self, value):
        self._offline = bool(value)

    def create_fallback_order(self):
        """在断网模式下创建一个兜底订单，返回 {file_path, name}"""
        if not self._offline:
            return None

        images = get_fallback_images()
        if images and images[0]["path"] and os.path.exists(images[0]["path"]):
            return {"file_path": images[0]["path"], "name": images[0]["name"]}
        else:
            # 生成临时图样
            path = _generate_placeholder_image()
            return {"file_path": path, "name": "BadgeVerse 活动"}
