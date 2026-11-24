# without_skill 对照（批八收尾）

日期：2026-11-24
目的：给出「只有技能名、没有技能描述」时的路由下限，与有技能描述的全量盲测对比。

## 做法

- 从 `out/blind/cases.json` 的 180 条路由用例里，用固定种子（20261124）随机抽 24 条。
- 判卷员只看到 8 个入口 id 的名字：color-decision、structure-read、shoot-plan、ways-of-seeing、chinese-eye、sequence-edit、cull-select、photo-vision；**没有描述、没有关键词、没有 expect**。
- 允许判 `none`（不属于这套摄影工具）。
- 提示文件 `out/blind/without-skill-cases.json`（只有 id + prompt）；期望另存 `out/blind/without-skill-expected.json`，判卷员不可见。

## 结果

- 18/24 = 75.0%，Wilson 95% CI [55.1%, 88.0%]。
- 错 6 条：
  - W10 期望 chinese-eye → 判 shoot-plan（「题记/三远」被当成拍摄构思）
  - W11 期望 ways-of-seeing → 判 none（观看机制类问题被判为不属于）
  - W17 期望 none → 判 sequence-edit（普通照片提问被高估）
  - W20 期望 cull-select → 判 sequence-edit（选片 vs 组照排序）
  - W21 期望 cull-select → 判 none
  - W23 期望 photo-vision → 判 none

## 对比

- 有技能描述的全量盲测：176/180 = 97.8%，Wilson [94.4%, 99.1%]（见 `out/blind/design-notes.md`）。
- 只有名字时 75.0%，说明路由主要靠描述与边界条目，不只靠名字；但名字本身带语义，这个下限不是「完全无技能」的绝对零点。

## 局限

- N=24，抽样误差大；只抽一次，未做重复判卷。
- 判卷员看到的是本项目的 8 个 id，名字有提示性（如 color-decision、cull-select）。
