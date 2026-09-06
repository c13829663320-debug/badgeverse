# -*- coding: utf-8 -*-
"""
test_smoke — 项目测试框架冒烟测试
验证 pytest 能正确导入项目模块、配置环境变量生效。
这是 red-green-mode 循环的基础：如果这个测试都跑不过，后续所有 TDD 无从谈起。
"""
import os
import sys

# conftest.py 已确保 site-packages 在 path 中


def test_pytest_runs():
    """pytest 自身能正常执行"""
    assert True


def test_config_importable():
    """config 模块可导入，且环境变量生效"""
    import config
    assert config.MOCK_MODE is True  # conftest 设置了 BADGE_MOCK=1
    assert config.STEPFUN_IMAGE_MODEL == "step-image-edit-2"


def test_image_utils_importable():
    """image_utils 模块可导入"""
    import image_utils
    assert hasattr(image_utils, 'stylize_image')
    assert hasattr(image_utils, 'crop_to_circle')
    assert hasattr(image_utils, 'build_print_grid')


def test_app_importable():
    """app 模块可导入（Flask app 实例存在）"""
    import app
    assert app.app is not None


def test_bs4_importable():
    """BeautifulSoup 可导入（前端结构断言依赖）"""
    from bs4 import BeautifulSoup
    soup = BeautifulSoup('<div class="test">hello</div>', 'lxml')
    assert soup.find(class_='test').text == 'hello'
