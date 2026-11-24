# 郭熙 OCR 抽样的运行状态（2026-11-24）

- 原始计划：27 条（`out\ocr-sample-linquan`，S01–S27，全部 block 定位）。
- 实际：S01 是整页块，第一张就把本地 qwen3-vl:4b 卡住（Ollama `ollama ps` 显示 `qwen3-vl:4b ... Stopping...`，无法卸载；服务端单并发 worker 也被占住）。24 条未完成。
- 缩样重试：筛出 11 条小于 400KB 的裁图（`out\ocr-sample-linquan-small`）。S02、S03 正常返回，均与引文逐字一致（相似度 1.00）。S12 再次把服务卡住，S13–S27 未获得转写。
- 服务与 Ollama 进程在本会话沙箱内无法终止（taskkill `Access denied`），需要在本机重启 Ollama（或重启电脑）后再补跑。
- 结论边界：郭熙这批**没有形成可用的 OCR 覆盖结论**；只确认了 S02、S03 两条，不得把 9 条 0.00 当成「OCR 错」或「空转写」。
