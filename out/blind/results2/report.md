# 统一盲测报告（批五后）

样本 180 条，8 批交叉，判卷只比对入口选择。

| 入口 | 通过 | 总数 | 准确率 | 95% CI |
|---|---|---|---|---|
| color-decision | 18 | 18 | 100.0% | [82.4%, 100.0%] |
| structure-read | 18 | 18 | 100.0% | [82.4%, 100.0%] |
| shoot-plan | 18 | 18 | 100.0% | [82.4%, 100.0%] |
| ways-of-seeing | 17 | 18 | 94.4% | [74.2%, 99.0%] |
| chinese-eye | 17 | 18 | 94.4% | [74.2%, 99.0%] |
| sequence-edit | 18 | 18 | 100.0% | [82.4%, 100.0%] |
| cull-select | 18 | 18 | 100.0% | [82.4%, 100.0%] |
| photo-vision | 11 | 12 | 91.7% | [64.6%, 98.5%] |

| 合计 | 176 | 180 | 97.8% | [94.4%, 99.1%] |

## 失败明细

- **ways-of-seeing** 应=`chinese-eye` 实=`none` — 什么叫气韵生动
- **ways-of-seeing** 应=`none` 实=`photo-vision` — 帮我写个摄影学习计划
- **cull-select** 应=`ways-of-seeing` 实=`none` — 为什么我觉得好但别人不喜欢
- **photo-vision** 应=`photo-vision` 实=`ways-of-seeing` — 同一张照片，有人说构图好有人说颜色差，我听谁的
