@echo off
chcp 65001 >nul 2>&1
title BadgeVerse 服务

echo ========================================
echo   BadgeVerse 一键启动
echo ========================================
echo.

:: 杀掉旧进程
taskkill /f /im ssh.exe >nul 2>&1
echo [1/4] 清理旧进程完成

:: 设置环境变量
set STEPFUN_API_KEY=2n20IUrZ1b7NKUmAYylCXq5QmJnchTTEjhiZ3BJn6soOM0T5PUWyQIg42Uy9hKjfB
set BADGE_MOCK=0
set PYTHONPATH=D:\StepFun\resources\app.asar.unpacked\tools\win\python-3.11.9\Lib\site-packages

:: 启动 Flask 服务（新窗口）
echo [2/4] 启动 Flask 服务...
start "BadgeVerse-Flask" /min python "E:\jieyueAI\badgeverse_mvp\badgeverse_mvp\run_server.py"

:: 等待 Flask 就绪
timeout /t 6 /nobreak >nul

:: 启动 SSH 隧道（新窗口）— 用 localhost.run（无安全拦截页）
echo [3/4] 启动公网隧道...
start "BadgeVerse-Tunnel" /min ssh -o StrictHostKeyChecking=no -o ServerAliveInterval=30 -o ServerAliveCountMax=3 -R 80:localhost:5000 nokey@localhost.run

:: 等待隧道建立
timeout /t 12 /nobreak >nul

echo [4/4] 服务已启动！
echo.
echo ========================================
echo   本地访问: http://127.0.0.1:5000
echo   管理后台: http://127.0.0.1:5000/admin
echo   公网地址: 查看 Tunnel 窗口输出的 https://xxx.serveousercontent.com
echo ========================================
echo.
echo 关闭此窗口不会停止服务。
echo 要停止服务请关闭 BadgeVerse-Flask 和 BadgeVerse-Tunnel 窗口。
echo.
pause
