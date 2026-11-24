# 郭熙 OCR 抽样运行状态（2026-11-24）

- 计划 27 条（`out\ocr-sample-linquan`，S01–S27，全部 block 定位），已全部尝试。
- 13 条拿到响应：
  - 10 条有文字，全部与引文逐字或轻微一致（S02/S03 p027、S04/S06 p047、S05/S07/S09/S11、S08/S10）；
  - 3 条空转写：S01（p023）、S12、S13，均为整页密排块，250–273s 后返回空串。
- 14 条请求失败（S14–S27）：Ollama 在 S13 之后退出，视觉服务返回连接错误；不是 OCR 错，也不是原文有误。
- 恢复 Ollama 时沙箱内启动被拒：`ollama serve` 报 `remove C:\Users\27669\.ollama\models\manifests: Access is denied`，无法从本会话恢复；需在本机重启 Ollama 应用（或重启电脑）。
- 恢复后按原 manifest 断点续跑（已有失败记录会保留，加 `--retry-failed` 重跑失败项）：
  `python tools\ocr_verify.py run --out out\ocr-sample-linquan --retry-failed`
- 结论边界：郭熙这批只确认「有字的 10 条全部对得上」与「3 条密排块空转写」；14 条失败不能记成 OCR 错，也不宣称整本覆盖。报告见 `report.md`，表内失败/空转写均已标注。
