# -*- coding: utf-8 -*-
"""
run_tests.py — 在受限嵌入式 Python 下运行 pytest 的启动器
用法：python run_tests.py [pytest参数...]
"""
import os
import sys

SITE_PACKAGES = r"D:\StepFun\resources\app.asar.unpacked\tools\win\python-3.11.9\Lib\site-packages"
if os.path.isdir(SITE_PACKAGES) and SITE_PACKAGES not in sys.path:
    sys.path.insert(0, SITE_PACKAGES)

BASE = os.path.dirname(os.path.abspath(__file__))
if BASE not in sys.path:
    sys.path.insert(0, BASE)

from pytest import main  # noqa: E402

raise SystemExit(main(sys.argv[1:]))
