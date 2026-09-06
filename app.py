"""
badgeverse.app
吧唧星球 BadgeVerse · 参赛 MVP 后端
链路：H5 上传照片 -> 选风格 -> 阶跃 API 风格化生成(重试2次) -> 70mm 圆形裁切 -> 下单取件号 -> 打印队列

运行：python app.py  （默认 http://127.0.0.1:5000 ，局域网 0.0.0.0:5000 供手机扫码）
"""
import os
import io
import time
import uuid
import sqlite3
import datetime

from flask import Flask, request, jsonify, render_template, send_from_directory

import config
from image_utils import stylize_image, crop_to_circle, build_print_grid

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 12 * 1024 * 1024  # 12MB


# ----------------------------- 工具 -----------------------------
def ensure_dirs():
    for d in (config.UPLOAD_DIR, config.GENERATED_DIR, config.OUTPUT_DIR, config.DATA_DIR):
        os.makedirs(d, exist_ok=True)


def get_db():
    conn = sqlite3.connect(config.DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    ensure_dirs()
    conn = get_db()
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            pickup_code TEXT UNIQUE,
            style TEXT,
            created_at TEXT,
            gen_ms INTEGER,
            status TEXT,
            source_file TEXT,
            result_file TEXT,
            print_file TEXT,
            error TEXT
        )
        """
    )
    conn.commit()
    conn.close()


def make_pickup_code():
    """生成唯一取件号，如 BV-20260906-8F3K。"""
    date = datetime.date.today().strftime("%Y%m%d")
    tail = uuid.uuid4().hex[:4].upper()
    code = f"BV-{date}-{tail}"
    conn = get_db()
    exists = conn.execute("SELECT 1 FROM orders WHERE pickup_code=?", (code,)).fetchone()
    conn.close()
    if exists:
        return make_pickup_code()
    return code


def log_order(conn, pickup_code, style, gen_ms, status, source_file, result_file, print_file, error=None):
    conn.execute(
        """INSERT OR REPLACE INTO orders
           (pickup_code, style, created_at, gen_ms, status, source_file, result_file, print_file, error)
           VALUES (?,?,?,?,?,?,?,?,?)""",
        (pickup_code, style, datetime.datetime.now().isoformat(timespec="seconds"),
         gen_ms, status, source_file, result_file, print_file, error),
    )
    conn.commit()


# ----------------------------- 页面 -----------------------------
@app.route("/")
def index():
    return render_template("index.html", styles=config.STYLES)


@app.route("/health")
def health():
    return jsonify(ok=True, mock=config.MOCK_MODE)


# ----------------------------- 上传 -----------------------------
@app.route("/api/upload", methods=["POST"])
def upload():
    if "file" not in request.files:
        return jsonify(ok=False, error="未收到文件"), 400
    f = request.files["file"]
    if not f or not f.filename:
        return jsonify(ok=False, error="文件为空"), 400
    if f.content_length and f.content_length > 10 * 1024 * 1024:
        return jsonify(ok=False, error="图片需小于 10MB"), 400
    ext = os.path.splitext(f.filename)[1].lower() or ".jpg"
    if ext not in (".jpg", ".jpeg", ".png", ".webp"):
        return jsonify(ok=False, error="仅支持 jpg/png/webp"), 400
    fid = uuid.uuid4().hex
    path = os.path.join(config.UPLOAD_DIR, f"{fid}{ext}")
    f.save(path)
    return jsonify(ok=True, file_id=fid, file_path=path)


# ----------------------------- 生成（核心） -----------------------------
@app.route("/api/generate", methods=["POST"])
def generate():
    data = request.get_json(silent=True) or {}
    file_id = data.get("file_id")
    style = data.get("style", "动漫")
    if style not in config.STYLES:
        return jsonify(ok=False, error="不支持的风格"), 400

    # 找到上传文件
    src = None
    for name in os.listdir(config.UPLOAD_DIR):
        if name.startswith(file_id):
            src = os.path.join(config.UPLOAD_DIR, name)
            break
    if not src:
        return jsonify(ok=False, error="未找到上传的图片，请重新上传"), 404

    t0 = time.time()
    try:
        # stylize_image 内部处理阶跃调用(重试2次)或 MOCK 生图
        out_path, gen_ms, mock_used = stylize_image(src, style, file_id)
    except Exception as e:  # noqa
        # 降级：报错提示 + 人工处理
        return jsonify(ok=False, error=f"生成失败：{e}，请重试或联系现场工作人员"), 500

    result_path = os.path.join(config.GENERATED_DIR, f"{file_id}_result.jpg")
    result_path = crop_to_circle(out_path, result_path)

    return jsonify(
        ok=True,
        result_url=f"/generated/{os.path.basename(result_path)}",
        gen_ms=int(gen_ms * 1000),
        mock=mock_used,
    )


@app.route("/generated/<name>")
def generated_file(name):
    return send_from_directory(config.GENERATED_DIR, name)


# ----------------------------- 下单 -----------------------------
@app.route("/api/order", methods=["POST"])
def order():
    data = request.get_json(silent=True) or {}
    style = data.get("style", "动漫")
    result_file = data.get("result_file", "")
    source_file = data.get("source_file", "")
    gen_ms = int(data.get("gen_ms", 0) or 0)

    pickup = make_pickup_code()
    conn = get_db()
    # 把生成图排进 89x89 四宫格打印
    print_path = None
    rg = os.path.join(config.GENERATED_DIR, os.path.basename(result_file))
    if os.path.exists(rg):
        print_path = build_print_grid(rg, config.OUTPUT_DIR, pickup)
    log_order(conn, pickup, style, gen_ms, "pending", source_file, result_file, print_path)
    conn.close()
    return jsonify(ok=True, pickup_code=pickup, print_file=print_path)


# ----------------------------- 后台：订单/统计 -----------------------------
@app.route("/api/orders")
def orders():
    conn = get_db()
    rows = conn.execute("SELECT * FROM orders ORDER BY id DESC LIMIT 100").fetchall()
    conn.close()
    return jsonify(ok=True, orders=[dict(r) for r in rows])


@app.route("/api/stats")
def stats():
    conn = get_db()
    total = conn.execute("SELECT COUNT(*) c FROM orders").fetchone()["c"]
    ok_n = conn.execute("SELECT COUNT(*) c FROM orders WHERE status='pending'").fetchone()["c"]
    avg_ms = conn.execute("SELECT AVG(gen_ms) a FROM orders").fetchone()["a"]
    conn.close()
    return jsonify(ok=True, total=total, success=ok_n, avg_gen_ms=int(avg_ms or 0))


if __name__ == "__main__":
    init_db()
    print(f"[BadgeVerse] MOCK={config.MOCK_MODE}  阶跃key={'已配置' if config.STEPFUN_API_KEY else '未配置'}")
    print(f"[BadgeVerse] 启动 http://127.0.0.1:5000 （局域网访问用 http://<本机IP>:5000，手机扫码同一WiFi）")
    app.run(host="0.0.0.0", port=5000, debug=False)
