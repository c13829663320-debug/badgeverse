"""
badgeverse.image_utils
图片处理：阶跃风格化生成(含重试/MOCK) + 70mm 圆形裁切 + 89×89 四宫格拼版
"""
import os
import io
import time
import base64
import requests
from PIL import Image, ImageDraw, ImageFilter, ImageEnhance

import config

# 生成图片最大边长（避免过大）
MAX_SIDE = 1080


# ----------------------------- 阶跃生成 -----------------------------
# 风格化 = 图像编辑（图生图）：保留人物面部特征，只换风格。
# 官方接口：POST /v1/images/edits（multipart/form-data），模型 step-image-edit-2，
# 输入图上限 4096x4096，返回图与输入图同尺寸，单次约 1-2 秒。
EDIT_PROMPT_PREFIX = (
    "Keep the person's face, facial features and identity unchanged. "
    "Convert this portrait photo into the following style: "
)
EDIT_PROMPT_SUFFIX = ", centered head-and-shoulders composition, high quality"


def _guess_mime(path):
    ext = os.path.splitext(path)[1].lower()
    return {".png": "image/png", ".webp": "image/webp"}.get(ext, "image/jpeg")


def _preprocess_image(src_path):
    """预处理：确保图片不超过阶跃 API 限制（4096x4096），返回临时文件路径。"""
    img = Image.open(src_path).convert("RGB")
    w, h = img.size
    if max(w, h) > 4000:
        ratio = 4000 / max(w, h)
        img = img.resize((int(w * ratio), int(h * ratio)), Image.LANCZOS)
        tmp = src_path.rsplit(".", 1)[0] + "_pre.jpg"
        img.save(tmp, "JPEG", quality=92)
        return tmp
    return src_path


def _call_stepfun(src_path, style_prompt):
    """调用阶跃 StepFun 图像编辑 API（图生图风格化），返回 PIL Image。"""
    headers = {
        "Authorization": f"Bearer {config.STEPFUN_API_KEY}",
    }
    url = f"{config.STEPFUN_BASE_URL}/images/edits"
    prompt = EDIT_PROMPT_PREFIX + style_prompt + EDIT_PROMPT_SUFFIX
    # 预处理：确保图片不超 4096px
    actual_src = _preprocess_image(src_path)
    with open(actual_src, "rb") as f:
        files = {"image": (os.path.basename(src_path), f, _guess_mime(src_path))}
        form = {
            "model": config.STEPFUN_IMAGE_MODEL,
            "prompt": prompt,
            "response_format": "b64_json",
        }
        resp = requests.post(url, headers=headers, files=files, data=form,
                             timeout=config.GENERATE_TIMEOUT)
    if resp.status_code != 200:
        raise RuntimeError(f"阶跃接口 HTTP {resp.status_code}: {resp.text[:300]}")
    data = resp.json()
    # 兼容不同返回结构
    b64 = None
    if isinstance(data, dict):
        for key in ("b64_json", "data"):
            if key in data:
                if key == "b64_json":
                    b64 = data[key]
                elif isinstance(data[key], list) and data[key]:
                    first = data[key][0]
                    b64 = first.get("b64_json") if isinstance(first, dict) else None
                    if not b64 and isinstance(first, dict):
                        b64 = first.get("url")
                break
    url_out = None
    if isinstance(data, dict):
        for item in (data.get("data") or []):
            if isinstance(item, dict) and item.get("url"):
                url_out = item["url"]
                break
    if b64:
        return Image.open(io.BytesIO(base64.b64decode(b64))).convert("RGB")
    if url_out:
        r = requests.get(url_out, timeout=config.GENERATE_TIMEOUT)
        r.raise_for_status()
        return Image.open(io.BytesIO(r.content)).convert("RGB")
    raise RuntimeError("阶跃接口未返回图片数据")


def _b64(path):
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode()


# ----------------------------- MOCK 生成 -----------------------------
def _mock_stylize(src_path, style_prompt):
    """离线模拟风格化：基于原图做色调/滤镜处理，保证无 key 也可全流程联调、演示。"""
    img = Image.open(src_path).convert("RGB")
    img.thumbnail((MAX_SIDE, MAX_SIDE))
    # 按风格粗略调色，制造"风格化"观感
    sp = style_prompt.lower()
    if "anime" in sp or "动漫" in sp:
        img = ImageEnhance.Color(img).enhance(1.5)
        img = ImageEnhance.Contrast(img).enhance(1.2)
    elif "oil" in sp or "油画" in sp:
        img = img.filter(ImageFilter.GaussianBlur(1.5))
        img = ImageEnhance.Color(img).enhance(1.4)
    elif "cyber" in sp or "赛博" in sp:
        img = ImageEnhance.Color(img).enhance(1.7)
        img = ImageEnhance.Contrast(img).enhance(1.3)
    elif "ink" in sp or "东方" in sp:
        img = img.filter(ImageFilter.SMOOTH)
        img = ImageEnhance.Color(img).enhance(0.9)
    else:
        img = ImageEnhance.Color(img).enhance(1.2)
    return img


# ----------------------------- 对外入口 -----------------------------
def stylize_image(src_path, style, file_id):
    """返回 (输出路径, 耗时秒, mock_used)。内部处理阶跃重试2次或 MOCK 生图。"""
    style_prompt = config.STYLES.get(style, style)
    t0 = time.time()
    out_path = os.path.join(config.GENERATED_DIR, f"{file_id}_styled.jpg")

    if config.MOCK_MODE or not config.STEPFUN_API_KEY:
        img = _mock_stylize(src_path, style_prompt)
        img.save(out_path, "JPEG", quality=92)
        return out_path, (time.time() - t0), True

    last_err = None
    for attempt in range(config.GENERATE_RETRIES + 1):
        try:
            img = _call_stepfun(src_path, style_prompt)
            img.save(out_path, "JPEG", quality=92)
            return out_path, (time.time() - t0), False
        except Exception as e:  # noqa
            last_err = e
            print(f"[BadgeVerse] 阶跃调用失败(第{attempt + 1}次): {e}", flush=True)
            if attempt < config.GENERATE_RETRIES:
                time.sleep(1.5 * (attempt + 1))  # 递增退避
    # 重试耗尽 -> 降级到 MOCK，保证现场不中断
    print(f"[BadgeVerse] 重试耗尽，降级 MOCK。最后错误: {last_err}", flush=True)
    img = _mock_stylize(src_path, style_prompt)
    img.save(out_path, "JPEG", quality=92)
    return out_path, (time.time() - t0), True


# ----------------------------- 70mm 圆形裁切 -----------------------------
def crop_to_circle(src_path, dst_path):
    """把生成图无损居中裁切为 70mm 圆形面纸（PNG 透明背景）。"""
    img = Image.open(src_path).convert("RGB")
    side = config.BLEED_PX
    # 居中方形裁剪
    w, h = img.size
    s = min(w, h)
    left = (w - s) // 2
    top = (h - s) // 2
    img = img.crop((left, top, left + s, top + s)).resize((side, side), Image.LANCZOS)

    # 圆形遮罩（透明背景）
    mask = Image.new("L", (side, side), 0)
    d = ImageDraw.Draw(mask)
    d.ellipse((0, 0, side, side), fill=255)
    out = Image.new("RGBA", (side, side), (0, 0, 0, 0))
    out.paste(img, (0, 0), mask)
    out.save(dst_path, "PNG")
    return dst_path


# ----------------------------- 89×89 四宫格拼版 -----------------------------
def build_print_grid(circle_png_path, output_dir, pickup_code):
    """把一枚圆面纸排进 89×89mm 四宫格（白底），供 TS5380 打印。返回输出路径。"""
    grid_px = int(config.PRINT_GRID_MM / 25.4 * config.DPI)
    cell = grid_px // 2
    sheet = Image.new("RGBA", (grid_px, grid_px), (255, 255, 255, 255))

    badge = Image.open(circle_png_path).convert("RGBA")
    badge.thumbnail((cell, cell), Image.LANCZOS)

    positions = [(0, 0), (cell, 0), (0, cell), (cell, cell)]
    for (px, py) in positions:
        sheet.paste(badge, (px + (cell - badge.width) // 2, py + (cell - badge.height) // 2), badge)

    os.makedirs(output_dir, exist_ok=True)
    out_path = os.path.join(output_dir, f"print_{pickup_code}.png")
    sheet.convert("RGB").save(out_path, "PNG")
    return out_path
