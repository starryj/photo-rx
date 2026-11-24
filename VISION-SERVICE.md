# 本地视觉解析服务（vision-service）设计方案

> 一个常驻本机的小服务：**给一个文件（PDF / EPUB / 图片目录），它还你结构化的正文、图块、以及每张图版的一句话解读。**
> 不只服务摄影书蒸馏，以后任何「把文件变成可读结构」的活都走它。

位置：`G:\AI_Workspace\06-VisionService\`　端口：`11500`　不设开机自启。

---

## 一、为什么是这个形态

要解决三件事，缺一件这套活就跑不通：

| 需求 | 谁来干 | 为什么不能换 |
|---|---|---|
| 扫描版 PDF 的版面还原与 OCR | **MinerU**（已在跑，Docker，`127.0.0.1:8000`） | 实测 10 本 PDF 里 **7 本是纯扫描**（文字层 0–1%，整页一张图）。PyMuPDF 对这些书一个字都取不出来 |
| 图版的定性解读「这图在讲什么」 | **本地 VLM** `qwen3-vl:4b`（ollama `11434`） | 实测 14 秒/图、零成本；MinerU 自带的 image_analysis 只给「一张照片，图中有…」这类通用描述，答不了「这张在演示同时对比」 |
| 定量测量（位置/面积/亮度） | **脚本**，不走模型 | 实测模型把地平线 49.95% 读成 25%。定量归代码，模型只做定性 |

三者用一个 HTTP 服务封在一起，对外只有一组接口。

---

## 二、拓扑

```
调用方（DSH 技能 / 你自己的脚本 / 其他项目）
        │  HTTP  JSON
        ▼
┌──────────────────────────────────────────┐
│  vision-service  127.0.0.1:11500         │
│  FastAPI + uvicorn（venv 内）             │
│  ├─ 队列 / 作业状态 / 缓存                 │
│  ├─ VLM 路由器（本地 ↔ 在线）              │
│  └─ 三条腿：                              │
│       ├── MinerU   127.0.0.1:8000 (Docker)│
│       ├── Ollama   127.0.0.1:11434        │
│       └── 云端 VLM  可选，默认关闭          │
└──────────────────────────────────────────┘
```

**为什么用 FastAPI**（你问的那条）：值得装。三个实际好处不是"更现代"，是省事——

1. `/docs` 自动出交互文档，你不用记接口，浏览器点一下就能试；
2. 文件上传（multipart）与 Pydantic 校验内建，不用手写解析；
3. 长任务能挂 `BackgroundTasks`，不用自己写线程池。

装在 **服务目录内的 venv**（`06-VisionService\.venv`），不碰 anaconda 全局。这样这个目录整个可以搬到别的机器直接用。

---

## 三、VLM 路由：本地还是在线，怎么判

**默认永远本地。** 在线必须显式打开。原因不只是钱——你的 life 库坚持不上云，摄影书同样是个人资料，保守默认是唯一安全默认。

判定顺序（短路，命中即停）：

```
1) 先问「这题需不需要模型」
   定量类（位置 / 面积 / 比例 / 色值 / 亮度）
        → 不走 VLM，交给 measure 脚本。直接返回 needs_measure=True
   混合类（"这图在演示什么现象" + "那块面积多大"）
        → 拆两步：VLM 答定性，脚本答定量，最后合并

2) 输入是否可本地处理
   图 ≤ 2048px、JPEG/PNG          → 本地
   > 2048px                        → 本地先缩放，仍读不准再考虑在线
   HEIC / RAW / TIFF               → 本地先转码

3) 语种与版面
   中英文横排                      → 本地
   竖排 / 繁体 / 手写 / 注疏混排    → 本地成功率低 → 建议在线（需 opt-in）
   多栏密集注疏整页                → MinerU 解析；MinerU 失败再谈在线 OCR

4) 规模与预算闸
   批量 > 50 张                    → 先报预估耗时，问用户
   任何在线调用                     → 必须 allow_cloud=true，否则拒绝并返回提示
```

在线失败与本地失败分开记账，便于以后判断要不要常备在线通道。

**在线通道怎么配**：不写死厂商。读 `config.yaml` 里的 `cloud:` 段（base_url / model / api_key_env），谁配了就都能用。没配就是本地。

---

## 四、接口

全部 JSON 进出。长任务返回 `job_id`，用 `/v1/jobs/{id}` 轮询。

### GET /health
```json
{"status":"ok","mineru":{"ok":true,"version":"3.4.5","queued":0},
 "ollama":{"ok":true,"models":["qwen3-vl:4b"]},
 "cloud":{"enabled":false}}
```
**用法就是一行** —— 批一跑到一半服务挂了，先跑这句，不要先怀疑蒸馏质量。

```powershell
Invoke-RestMethod http://127.0.0.1:11500/health | ConvertTo-Json -Depth 4
```

### GET /v1/models
可用 VLM 清单与各自能力（分辨率上限、语种、上次平均耗时）。

### POST /v1/describe
单图定性描述。
```json
{"image":"E:\\...\\p042.png",
 "task":"figure_semantics",
 "schema":{"phenomenon":"string","evidence":"string","confidence":"number"},
 "allow_cloud":false}
```
`task` 是**模板 id**，不是 prompt 全文。缓存键用它，prompt 模板改版本号。

内置模板：

| task | 问什么 |
|---|---|
| `figure_semantics` | 这张图版在演示什么现象 / 用什么手段演示 |
| `page_region` | 这一页哪一块是正文、哪一块是图注、哪一块是纯图 |
| `chart_read` | 这张图表在表达什么关系，坐标轴是什么 |
| `layout_multi` | 多栏页面按什么顺序读 |
| `quality_check` | 这张扫描页是否可读（模糊/歪斜/缺页边） |

### POST /v1/batch
```json
{"items":[{"image":"...","task":"figure_semantics"}, ...], "allow_cloud":false}
```
返回 `job_id`；`GET /v1/jobs/{id}` 给进度与结果数组。

### POST /v1/pdf/probe
PDF 体检，**整个服务的关键闸**。
```json
{"pdf":"E:\\...\\book.pdf"}
```
```json
{"pages":210,"text_ratio":0.67,"chars_per_page":772,
 "image_blocks":422,"big_image_pages":0,
 "verdict":"local_text|ocr|mixed",
 "recommend":{"backend":"hybrid-engine","effort":"medium","start":0,"end":209}}
```
判定规则（**先标定，不临场调**，见第七节）：

| 条件 | verdict | 建议 |
|---|---|---|
| 文字页 ≥ 80% 且字/页 ≥ 300 | `local_text` | 直接抽文字，图版单独渲染 |
| 文字页 ≤ 5% | `ocr` | MinerU 全页 OCR |
| 其余 | `mixed` | MinerU 全本，按页取文字或图 |

### POST /v1/pdf/parse
```json
{"pdf":"...","backend":"hybrid-engine","effort":"medium",
 "start":0,"end":-1,"return_images":true,"image_analysis":false}
```
返回 `job_id`。产物落 `out/<书名>/`：
```
book.md            # 正文 + 图块占位 [[FIG p042-1]]
content_list.json  # MinerU 原始结构（含 bbox）
images/            # 图块裁切，文件名带页码与序号
meta.json          # 页数、耗时、后端、失败页
```

### POST /v1/pdf/render
指定页渲染 PNG（给 VLM 读整版用，绕开图块切分）。
```json
{"pdf":"...","page":42,"dpi":150}
```

### GET /v1/jobs/{id}
```json
{"id":"j_7f3a","state":"running","done":128,"total":163,
 "elapsed_s":812,"eta_s":220,"errors":[]}
```

---

## 五、缓存与并发

**缓存键** = `sha256(文件或图块字节) + task_id + prompt_version + model_id`。
不用 prompt 全文做键——模板一改就全失效，且键会膨胀。
命中直接返回，`{"cached":true}` 标出。放在 `06-VisionService\.cache\<前2位>\<hash>.json`。

**并发**（GPU 只有一块，串行是对的）：

| 后端 | 并发 | 说明 |
|---|---|---|
| ollama | 1 | 信号量；GPU 16 GB 只够一个 4B 模型 |
| mineru | 1 | 容器自带 `max_concurrent_requests=3`，但本机实测别超 1 |
| cloud | 3 | 可配 |

排队超 30 分钟的作业写进 `jobs/*.json`，服务重启后可续。

---

## 六、部署与运维

```
G:\AI_Workspace\06-VisionService\
  .venv\
  app\
    main.py          # 路由
    backends.py      # mineru / ollama / cloud 三个适配器
    router_policy.py # 第三节的判定树
    cache.py
    jobs.py
  config.yaml        # 端口、模型、并发、云开关
  templates\         # task 的 prompt 模板（带版本号）
  out\               # 解析产物
  .cache\
  logs\              # 按天轮转
  start.ps1 / stop.ps1 / status.ps1
  README.md          # 第一行就是健康检查
```

README 里那一行（评审补的，同意——服务不开自启，就必须有一条一眼能验活路的命令）：

```powershell
curl.exe -s http://127.0.0.1:11500/health
# {"ok":true,"mineru":"up(3.4.5,pipeline)","ollama":"up(qwen3-vl:4b)","cloud":"off"}
```

**依赖**（装进 venv，不动全局）：`fastapi` `uvicorn[standard]` `pymupdf` `requests` `pyyaml`。

**启停**：`start.ps1` 起 uvicorn 并写 pid；`status.ps1` 打健康检查；`stop.ps1` 读 pid 关。**不写开机自启**（按你的习惯）。
启动时若发现 MinerU 或 Ollama 没起，**不自动拉起**，只在 `/health` 里报红——原因同"不自动重启 watcher"。

**日志**：`logs/2026-11-23.log`，每次调用一行（task、耗时、走本地还是云、命中缓存与否、费用）。

### 6.1 落地时踩到的六个坑（写在这里，省得重踩）

| 坑 | 症状 | 修法 |
|---|---|---|
| venv 用 anaconda 3.14 建 | pip 装 fastapi/pymupdf 卡死；`Unable to copy venvlauncher.exe` | `python -m venv --system-site-packages .venv`，只额外装 fastapi（纯 Python） |
| PyMuPDF 2.x 改名 | 用 `import fitz` 打 FutureWarning | `import pymupdf as fitz` |
| .ps1 编码 | powershell 5.1 报 `ParserError: MissingEndCurlyBrace` | 脚本存 **UTF-8 with BOM** |
| `Start-Process -RedirectStandardOutput` | 子进程句柄挂在调用者上，调用方卡满 120 s | `Invoke-CimMethod Win32_Process Create` + `cmd /c … 1>>log 2>>errlog`，进程完全脱离 |
| stop 只杀 pid 文件里的进程 | 端口仍被占（venv 的 python.exe 是转发壳，真监听的是子进程） | `taskkill /PID <pid> /T /F` + 兜底杀监听者 + 校验端口释放 |
| MinerU `results` 当成 list | `KeyError: 0` | `results` 是**按文件名 stem 索引的 dict**；值里有 `md_content` / `content_list`（JSON 字符串）/ `images`（name → data-uri） |

### 6.2 probe 的口径（被 PDF 水印骗过一次）

初版按「每页字数 ≥100」判有文字层，结果伊登《色彩艺术》每页都有 60 字的
`PDF created with pdfFactory trial version` 水印 → 125 页纯扫描书被判成 **100% 有文字层**。
这是最坏的一种错（该 OCR 的被判成可直读）。

现在只统计「真实文字页」：先去水印（BOILERPLATE 列表：annas-archive / z-library / 1lib.sk /
pdffactory / document generated by / 本文件由 …），再看是否 ≥100 字符。
`ratio ≥0.80 → local_text`，`≤0.10 → ocr`，其余 `mixed`；另出 `img_per_page` 与
`image_heavy(≥0.9)` 两个独立信号。9 本书复测全部正确。

---

## 六·五、并入本地工作台（`#/vision`「解析服务」页）

服务独立跑在 11500，但**平时不用开浏览器标签**：工作台 9630 里有一页直接操作它。

```
kb-workbench\
  server.py                  # 加 /api/vision/{path} 反代（写在所有 /api/ 路由之前）
  web\index.html             # nav 加「解析服务」项 + 引 vision.css / vision.js（js 在 app.js 之前）
  web\app.js                 # VIEWS.vision = window.VisionView.render
  web\vision.js / vision.css # 页面本体
```

页面五块：

1. **KPI**：本地 VLM 模型名与 ollama 状态 / MinerU 后端 / 在线通道（off 时列出缺哪几项）/ 缓存条数与体积。
2. **VLM 通道**：`本地` `在线` `自动` 三档按钮（POST `/v1/config/channel`），右侧「在线通道配置」展开后填 base_url / model / api_key / enabled，保存后可按「测试连通」。**api_key 只回显「已配置」，不回明文。**
3. **描述台**：填本地图片路径或选文件 → 选 task 芯片（`chart_read` `figure_semantics` `layout_multi` `page_region` `quality_check`）→ 出结果，回执里带 `used/model/ms/送图尺寸/是否命中缓存`。
4. **PDF 体检与解析**：先 `/v1/pdf/probe` 看判定（有字页占比、每页字数、每页大图、MinerU 预计耗时），
   再「按页渲染成图」逐页送去描述，或「整本交 MinerU」走 `/v1/pdf/parse`（后台 job，产物落 `out\parse\<stem>\`）。
5. **任务模板 / 作业**：模板的 task_id 与字数；作业列出 id、状态、进度、消息，完成的行第二行显示产物目录与 `正文 N 字 · M 块 · K 张图`。

反代的三个细节：

- `body = await request.body()` **整段透传**，不重组 multipart——否则一并传 PDF 就坏。
- 连接失败回 **503** 并附「跑一次 `G:\AI_Workspace\06-VisionService\start.ps1`」，不是 500。
- 服务里已有一条 `/api/{kb}/{path}` 两段通配（知识库代理），**反代必须写在它前面**，否则 `/api/vision/health` 会被吃成 `unknown kb: vision`。

页面上的那句话也写进服务了：**测量归脚本，模型只做定性。**
同一个 qwen3-vl:4b 把 DSC_3836 的地平线读成 25%（真值 49.95%）——尺寸、比例、亮度一律不进模型。

---

## 七、批一开工前的校准（必须先做）

服务写完不算完，要先证明它读得对。用 10 张**答案已知**的图版页：

- 取伊登《色彩艺术》里七种对比的教学图版（文字层完好，图注写明了在演示什么——这就是 ground truth）
- 让本地 VLM 只看图、不看文字，描述「在演示什么」
- 与图注比对

**通过线**：≥ 7/10 判定可用；< 7/10 则先调 prompt 模板，仍不过就这类任务改走云端或改走「文字层优先、视觉只做确认」。

同一批也用来标定 `/v1/pdf/probe` 的阈值：拿三本已知版式的书（纯文字层 / 纯扫描 / 混合）跑一遍，把 `text_ratio` 与 `chars_per_page` 的实际分布记下来，阈值按分布定，不拍脑袋。

---

## 八、已知风险

| 风险 | 现状 | 处置 |
|---|---|---|
| MinerU 解析慢 | 实测 10 页扫描件 >10 分钟（hybrid-engine） | 见下方实测记录；必要时降 `effort` 或改 `pipeline` 后端 |
| 4B 模型定性也会错 | 未测 | 第七节校准 |
| 扫描页 OCR 错字 | 未测 | 用「关键术语命中率」抽查，不追求全对 |
| 图块切分把跨页大图切断 | 已知会发生 | content_list 里有 bbox，跨页图按最近的两块合并 |
| 云端 key 泄露 | — | key 只从环境变量读，日志不落 key |

---

## 九、和蒸馏的关系

蒸馏流程只依赖三个动作：

1. `POST /v1/pdf/probe` → 决定这本书怎么读
2. `POST /v1/pdf/parse` → 拿 md + images
3. `POST /v1/batch`（task=`figure_semantics`）→ 给关键图版一句话

**服务里不放任何摄影知识**。它是通用管道，摄影书的判断留在 `photo-vision` 那边。这条边界要守住，否则以后别的项目用不了它。
