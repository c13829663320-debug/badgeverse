"""
badgeverse.config
吧唧星球 BadgeVerse 全局配置（环境变量可覆盖，便于现场切换）
"""
import os

# ---------- 阶跃 StepFun 图像 API ----------
# Flash Pro 会员额度；可替换为其它兼容接口
STEPFUN_API_KEY = os.environ.get("STEPFUN_API_KEY", "")
STEPFUN_BASE_URL = os.environ.get("STEPFUN_BASE_URL", "https://api.stepfun.com/v1")
# 图生图/风格化走 /images/edits 接口，默认用 step-image-edit-2（官方轻量级编辑模型，单次 1-2 秒）
# 注意：官方公告 step-image-edit-2 将于 2026-10-10 下线，届时需切换到替代模型
STEPFUN_IMAGE_MODEL = os.environ.get("STEPFUN_IMAGE_MODEL", "step-image-edit-2")

# ---------- 风格库（可替换 / 增减风格） ----------
# 键 = 前端展示名，值 = 发送给模型的风格提示词
# gender_prefix 会在生成时拼接（男/女不同 prompt）
STYLES = {
    "动漫少女": {
        "prompt": "japanese anime style, vibrant colors, clean line art, beautiful detailed eyes, soft shading, cute portrait",
        "gender": "female",
        "emoji": "🌸",
        "gradient": "linear-gradient(135deg, #ff9a9e, #fad0c4)",
        "preview": "/static/style_previews/anime_girl.jpg",
    },
    "动漫少年": {
        "prompt": "japanese anime style, vibrant colors, sharp line art, cool confident expression, detailed eyes, portrait",
        "gender": "male",
        "emoji": "⚔️",
        "gradient": "linear-gradient(135deg, #667eea, #764ba2)",
        "preview": "/static/style_previews/anime_boy.jpg",
    },
    "油画质感": {
        "prompt": "classical oil painting, impressionist, rich brushstroke texture, renaissance portrait, warm lighting",
        "gender": "neutral",
        "emoji": "🎨",
        "gradient": "linear-gradient(135deg, #f6d365, #fda085)",
        "preview": "/static/style_previews/oil.jpg",
    },
    "东方水墨": {
        "prompt": "traditional chinese ink wash painting, elegant, minimalist, bamboo and mist, portrait",
        "gender": "neutral",
        "emoji": "🎋",
        "gradient": "linear-gradient(135deg, #2c3e50, #4ca1af)",
        "preview": "/static/style_previews/ink.jpg",
    },
    "赛博朋克": {
        "prompt": "cyberpunk style, neon glow, futuristic, cinematic lighting, holographic, portrait",
        "gender": "neutral",
        "emoji": "🌃",
        "gradient": "linear-gradient(135deg, #ee0979, #ff6a00)",
        "preview": "/static/style_previews/cyber.jpg",
    },
    "水彩梦境": {
        "prompt": "soft watercolor painting, dreamy, pastel colors, gentle blending, artistic portrait",
        "gender": "neutral",
        "emoji": "💧",
        "gradient": "linear-gradient(135deg, #a8edea, #fed6e3)",
        "preview": "/static/style_previews/watercolor.jpg",
    },
}

# ---------- 吧唧尺寸 ----------
BADGE_MM = 58          # 58mm 徽章
BLEED_MM = 70          # 70mm 出血线（PET 冷裱膜直径）
DPI = 300              # 打印分辨率
BADGE_PX = int(BADGE_MM / 25.4 * DPI)   # 58mm 对应像素（约 685px）
BLEED_PX = int(BLEED_MM / 25.4 * DPI)   # 70mm 对应像素（约 827px）
PRINT_GRID_MM = 89     # 四宫格拼版边长 89×89

# ---------- MOCK 模式 ----------
# 无 API key / 现场断网时，用本地处理生成"风格化"占位图，保证全流程可联调、可演示。
# 生成环境变量 BADGE_MOCK=0 可强制走真实阶跃接口。
MOCK_MODE = os.environ.get("BADGE_MOCK", "1") == "1"

# ---------- 订单存储 ----------
DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
DB_PATH = os.path.join(DATA_DIR, "orders.sqlite3")
UPLOAD_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "uploads")
GENERATED_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "generated")
OUTPUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "output")

# 单张生成超时（秒）与重试次数（验收：单张<=15s，失败自动重试2次）
GENERATE_TIMEOUT = 30
GENERATE_RETRIES = 2

# 打印队列间歇（秒），每版后停 N 秒，后台可调
PRINT_INTERVAL = int(os.environ.get("PRINT_INTERVAL", "5"))

# 打印机名（空 = 系统默认打印机）
PRINTER_NAME = os.environ.get("PRINTER_NAME", "")
