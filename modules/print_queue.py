# -*- coding: utf-8 -*-
"""
BadgeVerse · 静默打印队列模块
Windows 驱动直连打印机，状态机 queued→printing→done/error，
每版后间歇（默认5秒，后台可调），支持手动重打印。
"""
import os
import time
import uuid
import threading
import subprocess

# 状态常量
STATUS_QUEUED = "queued"
STATUS_PRINTING = "printing"
STATUS_DONE = "done"
STATUS_ERROR = "error"

# 默认间歇秒数
DEFAULT_INTERVAL = 5


def _get_default_printer():
    """获取系统默认打印机名"""
    try:
        result = subprocess.run(
            ["powershell", "-Command",
             "(Get-CimInstance -Query 'SELECT * FROM Win32_Printer WHERE Default=$true').Name"],
            capture_output=True, text=True, timeout=10
        )
        name = result.stdout.strip()
        return name if name else None
    except Exception:
        return None


def _do_print(file_path, printer_name=None):
    """
    静默打印图片文件（Windows）。
    使用 rundll32 shimgvw.dll 调用系统打印，不弹出预览窗口。
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"打印文件不存在: {file_path}")

    if printer_name:
        # 指定打印机：用 printto 动词
        cmd = [
            "rundll32", "C:\\WINDOWS\\System32\\shimgvw.dll,ImageView_PrintTo",
            file_path, printer_name, "", ""
        ]
    else:
        # 默认打印机：用 print 动词
        cmd = ["rundll32", "C:\\WINDOWS\\System32\\shimgvw.dll,ImageView_PrintFull",
               file_path]

    result = subprocess.run(cmd, capture_output=True, timeout=60)
    if result.returncode != 0:
        raise RuntimeError(f"打印命令失败 (code={result.returncode}): {result.stderr[:200]}")


class PrintQueue:
    """打印队列：线程安全的状态机管理"""

    def __init__(self, interval_seconds=DEFAULT_INTERVAL, mock=False,
                 fail_on_purpose=False, printer_name=None):
        self._lock = threading.Lock()
        self._queue = []
        self.interval_seconds = interval_seconds
        self._mock = mock
        self._fail_on_purpose = fail_on_purpose
        self._printer_name = printer_name
        self._last_print_time = 0

    def add(self, file_path, order_id=None):
        """添加打印任务到队列，返回条目 ID"""
        with self._lock:
            item_id = uuid.uuid4().hex[:12]
            item = {
                "id": item_id,
                "file_path": file_path,
                "order_id": order_id,
                "status": STATUS_QUEUED,
                "created_at": time.time(),
                "printed_at": None,
                "error": None,
            }
            self._queue.append(item)
            return item_id

    def process_next(self):
        """处理下一个 queued 条目，返回 True 表示处理了一条，False 表示队列为空"""
        with self._lock:
            # 找下一个 queued 条目
            item = None
            for it in self._queue:
                if it["status"] == STATUS_QUEUED:
                    item = it
                    break
            if item is None:
                return False

            # 检查间歇时间
            now = time.time()
            if self._last_print_time > 0 and self.interval_seconds > 0:
                elapsed = now - self._last_print_time
                if elapsed < self.interval_seconds:
                    # 还没到间歇时间，不处理
                    return False

            item["status"] = STATUS_PRINTING

        # 在锁外执行实际打印（耗时操作）
        try:
            if self._mock:
                # MOCK 模式：模拟打印
                if self._fail_on_purpose:
                    raise RuntimeError("模拟打印失败")
            else:
                _do_print(item["file_path"], self._printer_name)

            with self._lock:
                item["status"] = STATUS_DONE
                item["printed_at"] = time.time()
                self._last_print_time = time.time()
            return True

        except Exception as e:
            with self._lock:
                item["status"] = STATUS_ERROR
                item["error"] = str(e)
                item["printed_at"] = time.time()
                self._last_print_time = time.time()
            return True  # 仍然返回 True，因为处理了一条（虽然失败了）

    def reprint(self, original_id):
        """重打印：根据原条目创建新的 queued 条目，返回新 ID"""
        with self._lock:
            original = None
            for it in self._queue:
                if it["id"] == original_id:
                    original = it
                    break
            if original is None:
                return None

            new_id = uuid.uuid4().hex[:12]
            new_item = {
                "id": new_id,
                "file_path": original["file_path"],
                "order_id": original.get("order_id"),
                "status": STATUS_QUEUED,
                "created_at": time.time(),
                "printed_at": None,
                "error": None,
            }
            self._queue.append(new_item)
            return new_id

    def get_item(self, item_id):
        """获取单条队列条目"""
        with self._lock:
            for it in self._queue:
                if it["id"] == item_id:
                    return dict(it)
            return None

    def get_queue(self):
        """获取整个队列（副本）"""
        with self._lock:
            return [dict(it) for it in self._queue]

    def get_status(self):
        """获取队列状态汇总"""
        with self._lock:
            summary = {
                "queued": 0,
                "printing": 0,
                "done": 0,
                "error": 0,
                "total": len(self._queue),
            }
            for it in self._queue:
                summary[it["status"]] = summary.get(it["status"], 0) + 1
            return summary

    def set_interval(self, seconds):
        """调节间歇时间"""
        self.interval_seconds = max(0, int(seconds))

    def clear_done(self):
        """清理已完成的条目"""
        with self._lock:
            self._queue = [it for it in self._queue if it["status"] != STATUS_DONE]
