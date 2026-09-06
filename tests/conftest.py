# -*- coding: utf-8 -*-
"""
conftest.py — BadgeVerse 测试公共配置
确保嵌入式 Python 的 site-packages 在 sys.path 中，使 pytest 能导入所有依赖。
"""
import sys
import os

SITE_PACKAGES = r"D:\StepFun\resources\app.asar.unpacked\tools\win\python-3.11.9\Lib\site-packages"
if os.path.isdir(SITE_PACKAGES) and SITE_PACKAGES not in sys.path:
    sys.path.insert(0, SITE_PACKAGES)

# 项目根目录
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

# 设置测试环境变量：MOCK 模式 + 空 key，避免测试时真实调用阶跃 API
os.environ.setdefault("BADGE_MOCK", "1")
os.environ.setdefault("STEPFUN_API_KEY", "")
