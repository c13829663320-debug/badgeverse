# 吧唧星球 · BadgeVerse — 参赛 MVP 代码骨架

「让每个人在 60 秒内，把此刻的自己，变成一枚能别在胸口的记忆。」

本仓库是可运行的参赛 MVP 骨架，覆盖 「上传照片 → 选风格 → AI 风格化生成(阶跃 StepFun，失败自动重试 2 次) → 70mm 圆形裁切 → 下单取件号 → 89×89 四宫格拼版打印」全链路。

---

## 一、快速启动

```bash
cd badgeverse
pip install -r requirements.txt
python app.py
# 浏览器打开 http://127.0.0.1:5000
```

> 手机扫码联调：电脑和手机连同一 WiFi，手机访问 `http://<电脑本机IP>:5000`。

**默认是 MOCK 演示模式**（无需 API key 也能跑通全流程，适合现场断网、省额度、先联调）。接真实阶跃接口见下节。

---

## 二、接入真实阶跃 StepFun 图像 API

设置环境变量后重启：

```bash
export STEPFUN_API_KEY="你的Key"
export BADGE_MOCK=0
python app.py
```

可选环境变量（`config.py` 内可改）：

| 变量 | 默认 | 说明 |
| --- | --- | --- |
| `STEPFUN_API_KEY` | 空 | 阶跃 API Key |
| `STEPFUN_BASE_URL` | `https://api.stepfun.com/v1` | 接口地址（可替换为兼容接口） |
| `STEPFUN_IMAGE_MODEL` | `step-1x-medium` | 图像模型 |
| `BADGE_MOCK` | `1` | `1`=MOCK，`0`=真实调用 |

> 说明：代码把 `config.STYLES` 里每个风格映射成一段风格 prompt 发给阶跃；若你的接口不支持「图生图」，可在 `image_utils._call_stepfun` 里把 `image` 字段去掉、仅用 prompt（届时请换成文字生成或换用支持图生图的模型）。

---

## 三、接口一览

| 方法 | 路径 | 说明 |
| --- | --- | --- |
| GET | `/` | H5 前端 |
| GET | `/health` | 健康检查（返回 mock 状态） |
| POST | `/api/upload` | 上传照片，返回 `file_id` |
| POST | `/api/generate` | 按风格生成，返回 `result_url`/`gen_ms`/`mock` |
| POST | `/api/order` | 下单，返回 `pickup_code`（取件号）+ `print_file` |
| GET | `/api/orders` | 后台订单记录 |
| GET | `/api/stats` | 累计生成数 / 成功率 / 平均耗时 |

---

## 四、拼版打印脚本（命令行）

```bash
python print_layout.py generated/xxx_result.jpg
# 生成 output/print_<code>.png
```

产物是 **89×89mm / 300dpi 白底四宫格**，直接交给佳能 TS5380 用彩喷纸打印，打印后按格裁开 → 覆膜 → 圆裁 → 压制，一次出 4 枚面纸。

---

## 五、工艺与尺寸对照

| 参数 | 值 | 说明 |
| --- | --- | --- |
| 徽章直径 | 58mm | 手动压机 |
| 出血线 / 冷裱膜 | 70mm | PET 冷裱膜 |
| 打印用纸 | 140g 亚光彩喷纸 | A4 |
| 打印分辨率 | 300dpi | 拼版清晰度 |
| 拼版规格 | 89×89 四宫格 | 单版约 55–60 秒出 4 枚 |
| 生成耗时目标 | ≤ 15 秒/张 | 阶跃，失败自动重试 2 次 |

---

## 六、后台数据（路演可展示）

`GET /api/stats` 返回累计生成数、成功率、平均耗时——即路演时的 `实测数据` 来源。现场可用：

```bash
curl http://127.0.0.1:5000/api/stats
```

---

## 七、目录结构

```
badgeverse/
├── app.py            # Flask 后端（H5 + API + 取件号 + 日志）
├── image_utils.py    # 阶跃生成(重试/MOCK) + 70mm 圆裁 + 四宫格拼版
├── print_layout.py   # 89×89 拼版打印 CLI
├── config.py         # 配置 + 风格库 + 尺寸
├── requirements.txt
├── templates/
│   └── index.html    # H5 前端
├── uploads/          # 用户上传图
├── generated/        # 风格化结果
├── output/           # 拼版打印图
└── data/orders.sqlite3  # 订单记录
```

---

## 八、后续迭代（MVP 之外，见作战手册）

- 微信真实收款 / 商户号
- 微信小程序（审核周期）→ 赛后考虑
- 机械臂全自动作业（具身智能 vision）
- NFC 芯片 + 线上社区
- 多终端并发调度、复杂风格库运营后台
- IP 形象库与版权合规深度体系
