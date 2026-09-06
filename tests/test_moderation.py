# -*- coding: utf-8 -*-
"""
test_moderation — 内容审核模块测试
红绿循环 Phase 1-1：阶跃视觉模型判定图片安全性
"""
import os
import sys
import base64

# conftest.py 已注入 site-packages 和项目根目录到 sys.path


def test_parse_safe_response():
    """parse_moderation_response 正确解析安全图片的判定结果"""
    from modules.moderation import parse_moderation_response
    result = parse_moderation_response('{"safe": true, "category": "safe", "confidence": 0.95}')
    assert result["safe"] is True
    assert result["category"] == "safe"
    assert result["confidence"] == 0.95


def test_parse_unsafe_response():
    """parse_moderation_response 正确解析不合规图片的判定结果"""
    from modules.moderation import parse_moderation_response
    result = parse_moderation_response('{"safe": false, "category": "pornography", "confidence": 0.92}')
    assert result["safe"] is False
    assert result["category"] == "pornography"
    assert result["confidence"] == 0.92


def test_parse_violence_response():
    """parse_moderation_response 正确解析暴力类内容"""
    from modules.moderation import parse_moderation_response
    result = parse_moderation_response('{"safe": false, "category": "violence", "confidence": 0.88}')
    assert result["safe"] is False
    assert result["category"] == "violence"


def test_parse_political_response():
    """parse_moderation_response 正确解析涉政类内容"""
    from modules.moderation import parse_moderation_response
    result = parse_moderation_response('{"safe": false, "category": "political", "confidence": 0.85}')
    assert result["safe"] is False
    assert result["category"] == "political"


def test_parse_malformed_json():
    """parse_moderation_response 处理非 JSON 格式的回复：返回 safe=False 兜底"""
    from modules.moderation import parse_moderation_response
    result = parse_moderation_response("这张图片看起来很正常")
    assert result["safe"] is False
    assert result["confidence"] == 0.0


def test_parse_with_markdown_fence():
    """parse_moderation_response 处理带 markdown 代码块包裹的 JSON"""
    from modules.moderation import parse_moderation_response
    raw = '```json\n{"safe": true, "category": "safe", "confidence": 0.99}\n```'
    result = parse_moderation_response(raw)
    assert result["safe"] is True
    assert result["category"] == "safe"
    assert result["confidence"] == 0.99


def test_parse_missing_fields():
    """parse_moderation_response 处理缺少字段的情况"""
    from modules.moderation import parse_moderation_response
    result = parse_moderation_response('{"safe": true}')
    assert result["safe"] is True
    assert result["category"] == "safe"
    assert result["confidence"] == 0.0


def test_moderate_image_mock_returns_safe():
    """MOCK 模式下 moderate_image 返回 safe=True"""
    from modules.moderation import moderate_image
    test_img = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "uploads", "test_face.jpg")
    result = moderate_image(test_img, mock=True)
    assert result["safe"] is True
    assert result["category"] == "safe"
    assert "confidence" in result


def test_moderate_image_returns_required_keys():
    """moderate_image 返回结果包含所有必需字段"""
    from modules.moderation import moderate_image
    test_img = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "uploads", "test_face.jpg")
    result = moderate_image(test_img, mock=True)
    for key in ("safe", "category", "confidence", "detail"):
        assert key in result, f"缺少必需字段: {key}"


def test_moderation_result_is_dict():
    """moderate_image 返回类型是 dict"""
    from modules.moderation import moderate_image
    test_img = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "uploads", "test_face.jpg")
    result = moderate_image(test_img, mock=True)
    assert isinstance(result, dict)
