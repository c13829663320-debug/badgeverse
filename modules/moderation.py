# -*- coding: utf-8 -*-
"""
BadgeVerse · 内容审核模块
调阶跃视觉模型（step-1o-turbo-vision）判定图片安全性：涉黄/涉暴/涉政 + 置信度
返回: {"safe": bool, "category": str, "confidence": float, "detail": str}
"""
import os
import re
import json
import base64

import config

# 阶跃视觉模型配置
MODERATION_MODEL = os.environ.get("STEPFUN_VISION_MODEL", "step-1o-turbo-vision")
MODERATION_TIMEOUT = 30  # 秒

# 安全判定 prompt
MODERATION_PROMPT = (
    "你是一个图片内容安全审核员。请仔细分析这张图片，判断是否包含以下违规内容：\n"
    "1. 涉黄（色情、裸露、性行为）\n"
    "2. 涉暴（暴力、血腥、武器、恐怖）\n"
    "3. 涉政（政治敏感、违禁标志、反动旗帜）\n\n"
    "请只回复一个 JSON 对象，不要有任何其他文字：\n"
    '{"safe": true/false, "category": "safe/pornography/violence/political", "confidence": 0.0-1.0}'
)


def _b64_image(path):
    """读取图片文件并编码为 data URL"""
    ext = os.path.splitext(path)[1].lower()
    mime = {".png": "image/png", ".webp": "image/webp"}.get(ext, "image/jpeg")
    with open(path, "rb") as f:
        data = base64.b64encode(f.read()).decode()
    return f"data:{mime};base64,{data}"


def parse_moderation_response(text):
    """
    解析视觉模型返回的内容判定结果。
    处理：纯 JSON、markdown 代码块包裹、非 JSON 文本。
    返回: {"safe": bool, "category": str, "confidence": float, "detail": str}
    """
    # 尝试从 markdown 代码块中提取 JSON
    json_match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', text, re.DOTALL)
    if json_match:
        text = json_match.group(1)

    # 尝试直接提取 JSON 对象
    json_match = re.search(r'\{[^{}]*\}', text, re.DOTALL)
    if not json_match:
        # 无法解析 → 兜底返回 unsafe
        return {"safe": False, "category": "unknown", "confidence": 0.0,
                "detail": f"无法解析审核结果: {text[:200]}"}

    try:
        data = json.loads(json_match.group(0))
    except json.JSONDecodeError:
        return {"safe": False, "category": "unknown", "confidence": 0.0,
                "detail": f"JSON 解析失败: {text[:200]}"}

    return {
        "safe": bool(data.get("safe", False)),
        "category": str(data.get("category", "safe")),
        "confidence": float(data.get("confidence", 0.0)),
        "detail": f"模型判定: {data.get('category', 'unknown')} (置信度: {data.get('confidence', 0.0)})",
    }


def _call_stepfun_vision(image_path):
    """调用阶跃视觉模型 API，返回原始文本"""
    import requests

    headers = {
        "Authorization": f"Bearer {config.STEPFUN_API_KEY}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": MODERATION_MODEL,
        "messages": [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": MODERATION_PROMPT},
                    {"type": "image_url", "image_url": {"url": _b64_image(image_path)}},
                ],
            }
        ],
        "max_tokens": 256,
        "temperature": 0.1,
    }
    url = f"{config.STEPFUN_BASE_URL}/chat/completions"
    resp = requests.post(url, json=payload, headers=headers, timeout=MODERATION_TIMEOUT)
    resp.raise_for_status()
    data = resp.json()
    return data["choices"][0]["message"]["content"]


def moderate_image(image_path, mock=None):
    """
    对图片进行内容安全审核。
    mock: None 时跟随 config.MOCK_MODE；True 时直接返回安全结果（不调 API）。
    返回: {"safe": bool, "category": str, "confidence": float, "detail": str}
    """
    if mock is None:
        mock = config.MOCK_MODE

    if mock or not config.STEPFUN_API_KEY:
        # MOCK 模式：直接放行
        return {"safe": True, "category": "safe", "confidence": 1.0,
                "detail": "MOCK 模式：未调用审核 API，默认放行"}

    try:
        raw = _call_stepfun_vision(image_path)
        return parse_moderation_response(raw)
    except Exception as e:
        # API 调用失败 → 兜底返回 unsafe，记录详情
        return {"safe": False, "category": "error", "confidence": 0.0,
                "detail": f"审核 API 调用失败: {e}"}
