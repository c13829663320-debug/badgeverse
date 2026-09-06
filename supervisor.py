# -*- coding: utf-8 -*-
"""
BadgeVerse 服务启动脚本（稳定版）
- 独立进程，带自动重启逻辑
"""
import os
import sys
import subprocess
import time
import signal

SITE_PACKAGES = r"D:\StepFun\resources\app.asar.unpacked\tools\win\python-3.11.9\Lib\site-packages"
if os.path.isdir(SITE_PACKAGES) and SITE_PACKAGES not in sys.path:
    sys.path.insert(0, SITE_PACKAGES)

BASE = os.path.dirname(os.path.abspath(__file__))
os.chdir(BASE)
if BASE not in sys.path:
    sys.path.insert(0, BASE)

MAX_RESTART = 5
RESTART_DELAY = 3

def run():
    restart_count = 0
    while restart_count < MAX_RESTART:
        print(f"[BadgeVerse Supervisor] 启动 Flask (第 {restart_count + 1} 次)", flush=True)
        try:
            # 信号转发
            proc = subprocess.Popen(
                [sys.executable, os.path.join(BASE, "run_server.py")],
                cwd=BASE,
                env=os.environ.copy(),
            )
            # 等待进程结束
            while True:
                ret = proc.poll()
                if ret is not None:
                    print(f"[BadgeVerse Supervisor] Flask 退出 code={ret}", flush=True)
                    break
                time.sleep(1)
        except KeyboardInterrupt:
            print("[BadgeVerse Supervisor] 收到中断信号，退出", flush=True)
            try:
                proc.terminate()
                proc.wait(timeout=5)
            except:
                proc.kill()
            break
        except Exception as e:
            print(f"[BadgeVerse Supervisor] 异常: {e}", flush=True)

        restart_count += 1
        if restart_count < MAX_RESTART:
            print(f"[BadgeVerse Supervisor] {RESTART_DELAY} 秒后重启...", flush=True)
            time.sleep(RESTART_DELAY)

    print("[BadgeVerse Supervisor] 达到最大重启次数，退出", flush=True)


if __name__ == "__main__":
    run()
