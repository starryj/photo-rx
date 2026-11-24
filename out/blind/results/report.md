# 统一盲测报告（批五后）

样本 180 条，8 批交叉，判卷只比对入口选择。

| 入口 | 通过 | 总数 | 准确率 | 95% CI |
|---|---|---|---|---|
| color-decision | 18 | 18 | 100.0% | [82.4%, 100.0%] |
| structure-read | 17 | 18 | 94.4% | [74.2%, 99.0%] |
| shoot-plan | 17 | 18 | 94.4% | [74.2%, 99.0%] |
| ways-of-seeing | 12 | 18 | 66.7% | [43.7%, 83.7%] |
| chinese-eye | 14 | 18 | 77.8% | [54.8%, 91.0%] |
| sequence-edit | 15 | 18 | 83.3% | [60.8%, 94.2%] |
| cull-select | 17 | 18 | 94.4% | [74.2%, 99.0%] |
| photo-vision | 7 | 12 | 58.3% | [32.0%, 80.7%] |

| 合计 | 156 | 180 | 86.7% | [80.9%, 90.9%] |

## 失败明细

- **structure-read** 应=`ways-of-seeing` 实=`photo-vision` — 为什么我看不出这张哪里好
- **structure-read** 应=`chinese-eye` 实=`structure-read` — 这张是不是太满了
- **shoot-plan** 应=`ways-of-seeing` 实=`shoot-plan` — 为什么别人的阴天照就有味道
- **shoot-plan** 应=`chinese-eye` 实=`shoot-plan` — 雾天怎么拍才有那个意境
- **shoot-plan** 应=`sequence-edit` 实=`cull-select` — 同一天的片子怎么挑怎么排
- **ways-of-seeing** 应=`ways-of-seeing` 实=`chinese-eye` — 修掉细节之后反而更像了，这是为什么
- **ways-of-seeing** 应=`ways-of-seeing` 实=`chinese-eye` — 为什么留白会让人觉得安静
- **ways-of-seeing** 应=`none` 实=`ways-of-seeing` — 给我讲讲格式塔心理学的历史
- **chinese-eye** 应=`chinese-eye` 实=`structure-read` — 画面太空了，是不是要加点东西进去
- **chinese-eye** 应=`ways-of-seeing` 实=`chinese-eye` — 为什么这张会让人觉得空
- **sequence-edit** 应=`sequence-edit` 实=`color-decision` — 这组色彩调子不统一，要不要都调成一个方向
- **sequence-edit** 应=`sequence-edit` 实=`photo-vision` — 组照和单张的标准一样吗
- **sequence-edit** 应=`structure-read` 实=`photo-vision` — 单看这一张怎么改
- **sequence-edit** 应=`ways-of-seeing` 实=`sequence-edit` — 为什么这组看着没有情绪
- **sequence-edit** 应=`none` 实=`sequence-edit` — 帮我把这组照片排版成画册
- **sequence-edit** 应=`none` 实=`sequence-edit` — 给这组照片起个标题
- **cull-select** 应=`cull-select` 实=`sequence-edit` — 这组里有一张特别出彩，其他都要让位吗
- **cull-select** 应=`shoot-plan` 实=`cull-select` — 这几张是补拍好还是留现有的
- **cull-select** 应=`chinese-eye` 实=`cull-select` — 留白不够的那张要不要删
- **photo-vision** 应=`photo-vision` 实=`ways-of-seeing` — 这张照片我总觉得不对，但说不清是构图还是颜色
- **photo-vision** 应=`photo-vision` 实=`ways-of-seeing` — 同一张照片，有人说构图好有人说颜色差，我听谁的
- **photo-vision** 应=`photo-vision` 实=`none` — 我拍了一年，想找个框架检查自己的进步
- **photo-vision** 应=`photo-vision` 实=`none` — 我该先练构图还是先练用光
- **photo-vision** 应=`photo-vision` 实=`none` — 我这个题材该往哪个方向深挖
