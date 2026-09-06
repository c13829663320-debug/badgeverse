"""
badgeverse.print_layout
89×89mm 四宫格拼版打印脚本（CLI）
用途：把已生成的圆面纸（或任意图片）排进 89×89 四宫格，生成可直接打印的 PNG。

用法：
    python print_layout.py <输入图> [--out <输出.png>] [--grid 4]
    # 例：python print_layout.py generated/xxx_result.jpg --out output/print_demo.png

说明：生成的是 89×89mm、300dpi 的白底四宫格拼版，可直接交给佳能 TS5380 用
      4"x6" 或 A4 彩喷纸打印。打印后按格裁开、覆膜、圆裁、压制即得 4 枚面纸。
"""
import os
import sys
import argparse

import config
from image_utils import crop_to_circle, build_print_grid


def main():
    ap = argparse.ArgumentParser(description="BadgeVerse 89×89 四宫格拼版")
    ap.add_argument("input", help="输入图片路径")
    ap.add_argument("--out", default=None, help="输出 PNG 路径, 默认 output/print_<时间>.png")
    args = ap.parse_args()

    if not os.path.exists(args.input):
        print(f"[错误] 输入图不存在: {args.input}")
        sys.exit(1)

    # 1) 裁成 70mm 圆形
    import time, uuid
    code = time.strftime("%Y%m%d_%H%M%S") + "_" + uuid.uuid4().hex[:3].upper()
    os.makedirs(config.OUTPUT_DIR, exist_ok=True)
    circle_path = os.path.join(config.OUTPUT_DIR, f"circle_{code}.png")
    crop_to_circle(args.input, circle_path)
    print(f"[1/2] 圆形面纸已生成: {circle_path}")

    # 2) 拼版
    out_path = args.out or os.path.join(config.OUTPUT_DIR, f"print_{code}.png")
    grid = build_print_grid(circle_path, config.OUTPUT_DIR, code)
    print(f"[2/2] 89×89 四宫格拼版已生成: {grid}")
    print("提示：用 TS5380 打印此图后，按格裁开 → 覆膜 → 圆裁 → 压制即可。")


if __name__ == "__main__":
    main()
