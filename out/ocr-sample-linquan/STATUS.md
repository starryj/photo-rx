# 郭熙 OCR 抽样运行状态（2026-11-24）

- 计划 27 条（`out\ocr-sample-linquan`，S01–S27，全部 block 定位）。
- 实际完成 6 条：S02、S03（p027）、S04、S06（p047）四条转写与引文逐字一致（相似度 1.00）；S01（p023）是整页密排块，272.8s 后返回空串；S05（p047）请求失败，无转写。
- 未完成 21 条。第二个重试在 S12 上把本地 qwen3-vl:4b 卡死（`ollama ps` 显示 `Stopping...`，无法卸载；服务单并发 worker 被占）。随后缩样重试里 S02/S03 重复通过、S12 再次卡死。
- 沙箱内 `taskkill` 对 Ollama/服务进程返回 `Access denied`，无法在本会话恢复；需在本机重启 Ollama（或重启电脑）后按原 manifest 断点续跑：
  `python tools\ocr_verify.py run --out out\ocr-sample-linquan`
- 结论边界：郭熙这批只确认了 4 条逐字一致、1 条空转写、21 条未跑；**不得把未跑条目记成 OCR 错**，也不宣称整本覆盖。
