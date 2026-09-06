# -*- coding: utf-8 -*-
"""
badgeverse.app
吧唧星球 BadgeVerse · 参赛 MVP 后端
链路：H5 上传照片 -> 内容审核 -> 选风格 -> 阶跃风格化生成 -> 文字叠加
      -> 70mm 圆形裁切 -> 下单取件号 -> 打印队列 -> 静默打印

运行：python app.py  （默认 http://127.0.0.1:5000，局域网 0.0.0.0:5000）
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
from modules.moderation import moderate_image
from modules.text_overlay import add_text_to_image, get_available_fonts, \
    get_available_colors, get_available_positions
from modules.print_queue import PrintQueue, STATUS_QUEUED, STATUS_DONE, STATUS_ERROR
from modules.offline_fallback import OfflineFallback, get_fallback_images
from modules.failure_logger import FailureLogger
from modules.order_manager import OrderManager

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 12 * 1024 * 1024  # 12MB

# ----------------------------- 全局单例 -----------------------------
print_queue = PrintQueue(interval_seconds=config.PRINT_INTERVAL, mock=True)
offline_fallback = OfflineFallback()
failure_logger = None  # 延迟初始化
order_manager = None  # 延迟初始化


# ----------------------------- 工具 -----------------------------
def ensure_dirs():
    for d in (config.UPLOAD_DIR, config.GENERATED_DIR, config.OUTPUT_DIR, config.DATA_DIR):
        os.makedirs(d, exist_ok=True)


def get_db():
    conn = sqlite3.connect(config.DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    global failure_logger, order_manager
    ensure_dirs()
    conn = get_db()
    conn.execute("""
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
    """)
    conn.commit()
    conn.close()
    failure_logger = FailureLogger(config.DB_PATH)
    order_manager = OrderManager(config.DB_PATH)


def make_pickup_code():
    date = datetime.date.today().strftime("%Y%m%d")
    tail = uuid.uuid4().hex[:4].upper()
    return f"BV-{date}-{tail}"


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
    from modules.text_overlay import get_available_fonts, get_available_colors, get_available_positions
    return render_template("index.html", styles=config.STYLES,
                           fonts=get_available_fonts(),
                           colors=get_available_colors(),
                           positions=get_available_positions())


@app.route("/admin")
def admin():
    return render_template("admin.html")


@app.route("/health")
def health():
    return jsonify(ok=True, mock=config.MOCK_MODE,
                   offline=offline_fallback.is_offline())


# ----------------------------- 上传 + 内容审核 -----------------------------
@app.route("/api/upload", methods=["POST"])
def upload():
    if "file" not in request.files:
        return jsonify(ok=False, error="未收到文件"), 400
    f = request.files["file"]
    if not f or not f.filename:
        return jsonify(ok=False, error="文件为空"), 400
    ext = os.path.splitext(f.filename)[1].lower() or ".jpg"
    if ext not in (".jpg", ".jpeg", ".png", ".webp"):
        return jsonify(ok=False, error="仅支持 jpg/png/webp"), 400
    fid = uuid.uuid4().hex
    path = os.path.join(config.UPLOAD_DIR, f"{fid}{ext}")
    f.save(path)

    # 内容审核
    mod_result = moderate_image(path)
    if not mod_result["safe"]:
        try:
            os.remove(path)
        except OSError:
            pass
        return jsonify(ok=False, error=f"图片未通过内容审核: {mod_result.get('detail','')}"), 403

    return jsonify(ok=True, file_id=fid, file_path=path)


# ----------------------------- 生成 + 文字叠加 -----------------------------
@app.route("/api/generate", methods=["POST"])
def generate():
    data = request.get_json(silent=True) or {}
    file_id = data.get("file_id")
    style = data.get("style", "动漫")
    text = data.get("text", "")
    font_index = int(data.get("font_index", 0))
    color_name = data.get("color_name", "白色")
    position_name = data.get("position_name", "底部")

    if style not in config.STYLES:
        return jsonify(ok=False, error="不支持的风格"), 400

    src = None
    for name in os.listdir(config.UPLOAD_DIR):
        if name.startswith(file_id):
            src = os.path.join(config.UPLOAD_DIR, name)
            break
    if not src:
        return jsonify(ok=False, error="未找到上传的图片"), 404

    t0 = time.time()
    try:
        out_path, gen_ms, mock_used = stylize_image(src, style, file_id)
    except Exception as e:
        if failure_logger:
            failure_logger.log_error(file_id, "generation_failed", str(e))
        return jsonify(ok=False, error=f"生成失败：{e}"), 500

    result_path = os.path.join(config.GENERATED_DIR, f"{file_id}_result.jpg")
    result_path = crop_to_circle(out_path, result_path)

    # 文字叠加
    if text:
        from PIL import Image
        img = Image.open(result_path)
        img = add_text_to_image(img, text, font_index, color_name, position_name)
        img.save(result_path, "JPEG", quality=95)

    return jsonify(
        ok=True,
        result_url=f"/generated/{os.path.basename(result_path)}",
        gen_ms=int(gen_ms * 1000),
        mock=mock_used,
    )


@app.route("/generated/<name>")
def generated_file(name):
    return send_from_directory(config.GENERATED_DIR, name)


# ----------------------------- 文字叠加选项 API -----------------------------
@app.route("/api/fonts")
def fonts():
    return jsonify(ok=True, fonts=get_available_fonts())


@app.route("/api/colors")
def colors():
    return jsonify(ok=True, colors=get_available_colors())


@app.route("/api/positions")
def positions():
    return jsonify(ok=True, positions=get_available_positions())


# ----------------------------- 下单 + 打印队列 -----------------------------
@app.route("/api/order", methods=["POST"])
def order():
    data = request.get_json(silent=True) or {}
    style = data.get("style", "动漫")
    result_file = data.get("result_file", "")
    source_file = data.get("source_file", "")
    gen_ms = int(data.get("gen_ms", 0) or 0)

    # 断网兜底
    if offline_fallback.is_offline():
        fb = offline_fallback.create_fallback_order()
        if fb:
            result_file = fb.get("file_path", result_file)

    pickup = make_pickup_code()
    conn = get_db()
    print_path = None
    rg = os.path.join(config.GENERATED_DIR, os.path.basename(result_file))
    if os.path.exists(rg):
        print_path = build_print_grid(rg, config.OUTPUT_DIR, pickup)
    else:
        # 兜底：直接用结果图
        print_path = rg if os.path.exists(rg) else None

    log_order(conn, pickup, style, gen_ms, "pending", source_file, result_file, print_path)
    conn.close()

    # 加入打印队列
    if print_path:
        print_queue.add(print_path, order_id=pickup)
        # 尝试处理队列
        print_queue.process_next()

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


# ----------------------------- 后台管理 API -----------------------------
@app.route("/api/admin/queue")
def admin_queue():
    return jsonify(print_queue.get_status())


@app.route("/api/admin/offline", methods=["POST"])
def admin_offline():
    data = request.get_json(silent=True) or {}
    offline = bool(data.get("offline", False))
    offline_fallback.set_offline(offline)
    return jsonify(ok=True, offline=offline_fallback.is_offline())


@app.route("/api/admin/interval", methods=["POST"])
def admin_interval():
    data = request.get_json(silent=True) or {}
    seconds = int(data.get("seconds", 5))
    print_queue.set_interval(seconds)
    return jsonify(ok=True, interval_seconds=print_queue.interval_seconds)


@app.route("/api/admin/errors")
def admin_errors():
    if failure_logger:
        return jsonify(failure_logger.get_errors())
    return jsonify([])


@app.route("/api/admin/reprint", methods=["POST"])
def admin_reprint():
    data = request.get_json(silent=True) or {}
    item_id = data.get("item_id", "")
    new_id = print_queue.reprint(item_id)
    if new_id:
        print_queue.process_next()
        return jsonify(ok=True, new_item_id=new_id)
    return jsonify(ok=False, error="条目不存在")


@app.route("/api/admin/stats")
def admin_stats():
    conn = get_db()
    total = conn.execute("SELECT COUNT(*) c FROM orders").fetchone()["c"]
    ok_n = conn.execute("SELECT COUNT(*) c FROM orders WHERE status='pending'").fetchone()["c"]
    avg_ms = conn.execute("SELECT AVG(gen_ms) a FROM orders").fetchone()["a"]
    conn.close()
    err_summary = failure_logger.get_summary() if failure_logger else {"total": 0, "by_type": {}}
    return jsonify(
        total=total, success=ok_n,
        avg_gen_ms=int(avg_ms or 0),
        queue=print_queue.get_status(),
        offline=offline_fallback.is_offline(),
        interval_seconds=print_queue.interval_seconds,
        error_summary=err_summary,
    )


if __name__ == "__main__":
    init_db()
    print(f"[BadgeVerse] MOCK={config.MOCK_MODE}  阶跃key={'已配置' if config.STEPFUN_API_KEY else '未配置'}")
    print(f"[BadgeVerse] 启动 http://127.0.0.1:5000 （局域网 http://<本机IP>:5000）")
    app.run(host="0.0.0.0", port=5000, debug=False)
