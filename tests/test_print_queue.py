# -*- coding: utf-8 -*-
"""
test_print_queue — 静默打印队列模块测试
红绿循环 Phase 1-3：状态机 queued→printing→done/error，5秒间歇，重打印
"""
import os
import time
import tempfile


def test_queue_starts_empty():
    """打印队列初始化后为空"""
    from modules.print_queue import PrintQueue
    pq = PrintQueue(interval_seconds=0, mock=True)
    assert len(pq.get_queue()) == 0


def test_add_item_creates_queued_state():
    """添加队列条目，状态为 queued"""
    from modules.print_queue import PrintQueue, STATUS_QUEUED
    pq = PrintQueue(interval_seconds=0, mock=True)
    item_id = pq.add("test_file.png")
    q = pq.get_queue()
    assert len(q) == 1
    assert q[0]["id"] == item_id
    assert q[0]["status"] == STATUS_QUEUED
    assert q[0]["file_path"] == "test_file.png"


def test_process_item_transitions_to_done():
    """处理条目后状态变为 done"""
    from modules.print_queue import PrintQueue, STATUS_DONE
    pq = PrintQueue(interval_seconds=0, mock=True)
    item_id = pq.add("test_file.png")
    result = pq.process_next()
    assert result is True
    item = pq.get_item(item_id)
    assert item["status"] == STATUS_DONE
    assert "printed_at" in item


def test_process_empty_queue_returns_false():
    """空队列处理返回 False"""
    from modules.print_queue import PrintQueue
    pq = PrintQueue(interval_seconds=0, mock=True)
    assert pq.process_next() is False


def test_error_state_on_print_failure():
    """打印失败时状态变为 error"""
    from modules.print_queue import PrintQueue, STATUS_ERROR
    pq = PrintQueue(interval_seconds=0, mock=True, fail_on_purpose=True)
    item_id = pq.add("test_file.png")
    pq.process_next()
    item = pq.get_item(item_id)
    assert item["status"] == STATUS_ERROR
    assert "error" in item


def test_reprint_creates_new_queued_item():
    """重打印生成新的 queued 条目"""
    from modules.print_queue import PrintQueue, STATUS_QUEUED, STATUS_DONE
    pq = PrintQueue(interval_seconds=0, mock=True)
    item_id = pq.add("test_file.png")
    pq.process_next()
    assert pq.get_item(item_id)["status"] == STATUS_DONE
    new_id = pq.reprint(item_id)
    assert new_id != item_id
    new_item = pq.get_item(new_id)
    assert new_item["status"] == STATUS_QUEUED


def test_interval_configurable():
    """间歇时间可配置"""
    from modules.print_queue import PrintQueue
    pq5 = PrintQueue(interval_seconds=5, mock=True)
    pq10 = PrintQueue(interval_seconds=10, mock=True)
    assert pq5.interval_seconds == 5
    assert pq10.interval_seconds == 10


def test_interval_setter():
    """间歇时间可通过 setter 调节"""
    from modules.print_queue import PrintQueue
    pq = PrintQueue(interval_seconds=5, mock=True)
    pq.set_interval(15)
    assert pq.interval_seconds == 15


def test_get_queue_status_summary():
    """获取队列状态汇总"""
    from modules.print_queue import PrintQueue
    pq = PrintQueue(interval_seconds=0, mock=True)
    pq.add("f1.png")
    pq.add("f2.png")
    pq.process_next()
    summary = pq.get_status()
    assert "queued" in summary
    assert "printing" in summary
    assert "done" in summary
    assert "error" in summary
    assert summary["done"] >= 1
    assert summary["queued"] >= 1


def test_get_item_returns_none_if_not_found():
    """查询不存在的条目返回 None"""
    from modules.print_queue import PrintQueue
    pq = PrintQueue(interval_seconds=0, mock=True)
    assert pq.get_item("nonexistent") is None


def test_multiple_items_processed_in_order():
    """多条目按顺序处理"""
    from modules.print_queue import PrintQueue, STATUS_DONE
    pq = PrintQueue(interval_seconds=0, mock=True)
    id1 = pq.add("f1.png")
    id2 = pq.add("f2.png")
    id3 = pq.add("f3.png")
    pq.process_next()
    pq.process_next()
    pq.process_next()
    assert pq.get_item(id1)["status"] == STATUS_DONE
    assert pq.get_item(id2)["status"] == STATUS_DONE
    assert pq.get_item(id3)["status"] == STATUS_DONE
