# 反证闸第三轮（gate3）

日期：2026-11-24
用例：`out/gate3/cases.json`（30 条，7 张卡各 4 条 + router 2 条；id ce-21…pv-22）
盲评：判卷员只看到 `cases-blind.json`（id + prompt，无 expect 与 note）

## 第一轮

- 结果：29/30。
- 唯一错误：`cd-22`（color-decision）——「构图是不是太散」按期望应 block（转 structure-read），判卷员判 pass。
- 归因：color-decision 的 B 段只写了「不做精确色差测量」「不替结构问题辩护」等散条，缺一条显式的结构边界。
- 修法：在 color-decision.md「不要在以下情况使用」加一条：构图、结构、平衡问题走 structure-read，不拿色彩判断替结构判断背书；`revision` 升 5，重新编译（run-20261124-172633-d7eb47）。

## 第二轮（换判卷员，同一套 30 条）

- 结果：30/30（100%），Wilson 95% 下界约 88.6%。
- 分卡：color-decision 4/4、structure-read 4/4、shoot-plan 4/4、sequence-edit 4/4、cull-select 4/4、chinese-eye 4/4、ways-of-seeing 4/4、photo-vision 2/2。

## 判定口径

- 只有卡里「不要在以下情况使用」的显式条目才算 block。
- 「失败模式」是症状清单，不是拒单理由；把失败模式当 block 会造成误拦（沿用 gate2 修正后的口径）。

## 局限

- 用例由本项目作者编写，不是独立第三方；判卷员每轮一人，未做多人一致性。
- 30 条只覆盖七卡的典型边界，不覆盖长尾意图。
