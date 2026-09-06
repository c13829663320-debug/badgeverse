# -*- coding: utf-8 -*-
"""
BadgeVerse 启动器（适配本机受限嵌入式 Python）
作用：把 site-packages 加进 sys.path 后，以 __main__ 方式运行 app.py。
用法：python run_server.py
环境变量：STEPFUN_API_KEY、BADGE_MOCK=0/1、STEPFUN_IMAGE_MODEL 等见 config.py
"""
import os
import sys
import runpy

SITE_PACKAGES = r"D:\StepFun\resources\app.asar.unpacked\tools\win\python-3.11.9\Lib\site-packages"
if os.path.isdir(SITE_PACKAGES) and SITE_PACKAGES not in sys.path:
    sys.path.insert(0, SITE_PACKAGES)

BASE = os.path.dirname(os.path.abspath(__file__))
os.chdir(BASE)
if BASE not in sys.path:
    sys.path.insert(0, BASE)

runpy.run_path(os.path.join(BASE, "app.py"), run_name="__main__")
