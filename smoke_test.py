# -*- coding: utf-8 -*-
"""
BadgeVerse 全链路冒烟测试：health -> upload -> generate -> order -> stats
用法：python smoke_test.py [风格名，默认 动漫]
"""
import os
import sys
import time

SITE_PACKAGES = r"D:\StepFun\resources\app.asar.unpacked\tools\win\python-3.11.9\Lib\site-packages"
if os.path.isdir(SITE_PACKAGES) and SITE_PACKAGES not in sys.path:
    sys.path.insert(0, SITE_PACKAGES)

import requests  # noqa: E402

BASE = "http://127.0.0.1:5000"
IMG = os.path.join(os.path.dirname(os.path.abspath(__file__)), "uploads", "test_face.jpg")
STYLE = sys.argv[1] if len(sys.argv) > 1 else "动漫"


def main():
    print("health:", requests.get(BASE + "/health", timeout=10).text)

    with open(IMG, "rb") as f:
        r = requests.post(BASE + "/api/upload",
                          files={"file": ("test_face.jpg", f, "image/jpeg")}, timeout=30)
    print("upload:", r.text)
    fid = r.json()["file_id"]

    t0 = time.time()
    r = requests.post(BASE + "/api/generate",
                      json={"file_id": fid, "style": STYLE}, timeout=180)
    print(f"generate ({time.time() - t0:.1f}s):", r.text)
    gen = r.json()
    if not gen.get("ok"):
        sys.exit(1)

    r = requests.post(BASE + "/api/order", json={
        "style": STYLE,
        "result_file": gen.get("result_url", ""),
        "source_file": fid,
        "gen_ms": gen.get("gen_ms", 0),
    }, timeout=30)
    print("order:", r.text)

    print("stats:", requests.get(BASE + "/api/stats", timeout=10).text)


if __name__ == "__main__":
    main()
