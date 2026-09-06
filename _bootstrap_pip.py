# -*- coding: utf-8 -*-
"""
一次性辅助脚本：在受限嵌入式 Python（python311._pth 不含 site-packages）下引导 pip。
用法：python _bootstrap_pip.py <pip参数...>，例如：
    python _bootstrap_pip.py install -r requirements.txt
"""
import sys

SITE_PACKAGES = r"D:\StepFun\resources\app.asar.unpacked\tools\win\python-3.11.9\Lib\site-packages"
if SITE_PACKAGES not in sys.path:
    sys.path.insert(0, SITE_PACKAGES)

from pip._internal.cli.main import main  # noqa: E402

if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
