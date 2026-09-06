# -*- coding: utf-8 -*-
"""
test_offline_fallback — 断网兜底模块测试
红绿循环 Phase 1-4：活动主题图样走数字通道
"""
import os
import tempfile

def test_fallback_images_returns_list():
    """get_fallback_images 返回图样列表"""
    from modules.offline_fallback import get_fallback_images
    images = get_fallback_images()
    assert isinstance(images, list)


def test_offline_mode_default_false():
    """默认在线模式"""
    from modules.offline_fallback import OfflineFallback
    fb = OfflineFallback()
    assert fb.is_offline() is False


def test_set_offline_mode():
    """切换断网模式"""
    from modules.offline_fallback import OfflineFallback
    fb = OfflineFallback()
    fb.set_offline(True)
    assert fb.is_offline() is True
    fb.set_offline(False)
    assert fb.is_offline() is False


def test_create_fallback_order_returns_file_path():
    """create_fallback_order 返回一个有效的图片文件路径"""
    from modules.offline_fallback import OfflineFallback
    fb = OfflineFallback()
    fb.set_offline(True)
    # 创建临时主题图样目录
    fb.set_theme_dir(tempfile.gettempdir())
    result = fb.create_fallback_order()
    assert result is not None
    assert "file_path" in result
    assert os.path.exists(result["file_path"])


def test_online_mode_returns_none():
    """在线模式下 create_fallback_order 返回 None"""
    from modules.offline_fallback import OfflineFallback
    fb = OfflineFallback()
    fb.set_offline(False)
    assert fb.create_fallback_order() is None


def test_fallback_images_have_metadata():
    """兜底图样包含名称信息"""
    from modules.offline_fallback import get_fallback_images
    images = get_fallback_images()
    for img in images:
        assert "name" in img
