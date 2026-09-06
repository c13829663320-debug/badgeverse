# -*- coding: utf-8 -*-
"""
生成 6 种风格的 AI 参考图，存入 static/style_previews/
用阶跃 step-1x-medium 文生图接口
"""
import sys
import os
import base64
import time

SITE_PACKAGES = r"D:\StepFun\resources\app.asar.unpacked\tools\win\python-3.11.9\Lib\site-packages"
if os.path.isdir(SITE_PACKAGES) and SITE_PACKAGES not in sys.path:
    sys.path.insert(0, SITE_PACKAGES)

import requests

PROJECT = os.path.dirname(os.path.abspath(__file__))
if PROJECT not in sys.path:
    sys.path.insert(0, PROJECT)

import config

OUT_DIR = os.path.join(PROJECT, "static", "style_previews")
os.makedirs(OUT_DIR, exist_ok=True)

STYLES = {
    "anime_girl": (
        "japanese anime style, vibrant colors, clean line art, beautiful detailed eyes, "
        "soft shading, cute young woman portrait, pink hair, centered head-and-shoulders, high quality",
        "anime_girl.jpg",
    ),
    "anime_boy": (
        "japanese anime style, vibrant colors, sharp line art, cool confident expression, "
        "detailed eyes, handsome young man portrait, blue hair, centered head-and-shoulders, high quality",
        "anime_boy.jpg",
    ),
    "oil": (
        "classical oil painting, impressionist, rich brushstroke texture, renaissance portrait, "
        "warm lighting, elegant woman, centered head-and-shoulders, high quality",
        "oil.jpg",
    ),
    "ink": (
        "traditional chinese ink wash painting, elegant, minimalist, bamboo and mist, "
        "portrait of a scholar, centered head-and-shoulders, high quality",
        "ink.jpg",
    ),
    "cyber": (
        "cyberpunk style, neon glow, futuristic, cinematic lighting, holographic, "
        "portrait of a person in neon city, centered head-and-shoulders, high quality",
        "cyber.jpg",
    ),
    "watercolor": (
        "soft watercolor painting, dreamy, pastel colors, gentle blending, "
        "artistic portrait of a woman, centered head-and-shoulders, high quality",
        "watercolor.jpg",
    ),
}

API_KEY = os.environ.get("STEPFUN_API_KEY", config.STEPFUN_API_KEY)
BASE_URL = config.STEPFUN_BASE_URL

for key, (prompt, filename) in STYLES.items():
    out_path = os.path.join(OUT_DIR, filename)
    if os.path.exists(out_path):
        print(f"{filename} already exists, skip")
        continue
    print(f"Generating {filename}...", flush=True)
    payload = {
        "model": "step-image-edit-2",
        "prompt": prompt,
        "size": "1024x1024",
        "n": 1,
        "response_format": "b64_json",
    }
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json",
    }
    url = f"{BASE_URL}/images/generations"
    try:
        resp = requests.post(url, json=payload, headers=headers, timeout=90)
        if resp.status_code != 200:
            print(f"  FAIL HTTP {resp.status_code}: {resp.text[:200]}")
            continue
        data = resp.json()
        b64 = None
        if "data" in data and data["data"]:
            b64 = data["data"][0].get("b64_json")
            if not b64:
                url_out = data["data"][0].get("url")
                if url_out:
                    r2 = requests.get(url_out, timeout=60)
                    with open(out_path, "wb") as f:
                        f.write(r2.content)
                    print(f"  OK (url) -> {out_path}")
                    continue
        if b64:
            with open(out_path, "wb") as f:
                f.write(base64.b64decode(b64))
            print(f"  OK (b64) -> {out_path}")
        else:
            print(f"  FAIL: no image data")
    except Exception as e:
        print(f"  ERROR: {e}")
    time.sleep(1)

print("Done!")
