# 外接球题建模示例 · 参考导读

用途：固定顶点的立体几何题，展示完整解答、外接球、关键直径及辅助线。新题无动点时优先从本例换题。

- [离线单文件成品](成品/外接球题建模示例.html)
- [统一页面规范](../../references/page-spec.md) · [换题步骤](../../references/example-guide.md) · [验收标准](../../references/verification.md)

## 原题与数学基准

P、A、B、C 是球 O 表面上的四点，PA⊥平面 ABC，∠ABC=90°，PA=5、AB=3、BC=4，求球表面积。完整解答按“底面直角 → 空间直径 → 球心半径 → 面积”四张推导卡组织，答案 **50π（B）**。

教学坐标：B=(0,0,0)，A=(3,0,0)，C=(0,4,0)，P=(3,0,5)。M=(1.5,2,0)，O=(1.5,2,2.5)。渲染变换 `(x,y,z) → (x−1.5,z−2.5,2−y)`；不要将这个变换和缩放常数沿用到新题。

AC=5，PC=5√2，R=5√2/2。O 是 PC 中点，OA=OB=OC=OP=R，表面积 4πR²=50π。使用 [check_math.mjs](开发资料/check_math.mjs) 独立验算，不以页面显示值作为证明。

## 默认画面与状态

| 设置 | 页面初始化后的默认值 |
|---|---|
| 讲解 | 全部四张推导展开；底部四张概览可定位相应推导 |
| 图层 | 底面与侧面、外接球、直径 PC、球心与辅助线、直角标记开启；坐标轴关闭 |
| 标注 | 顶点字母和边长开启；字号 22px（14–32） |
| 透明度 | 外接球 8%，范围 0–20%；只调整球面材质 |
| 顶点选择 | 初始无选择；多选累积，空白不清空 |
| 精细度 | 自动，按像素预算调整 DPR |

HTML 的部分 checkbox 初始未 `checked`；`showFullSolution()` 会在初始化时同步它们。判断默认状态应以初始化完成后的页面与 state 为准。

## 文件与实现入口

| 文件/入口 | 责任 | 换题时关注 |
|---|---|---|
| [layout.html](开发资料/源码/layout.html) | 页头、两个 tab、原题/推导/设置、舞台浮层 | 题名、题干、`proof-0…3`、`data-proof`、读数与图层文字 |
| [style.css](开发资料/源码/style.css) | 共享暗色与响应式样式 | 优先保留；后置完整解题规则覆盖早期旧声明 |
| [app.js](开发资料/源码/app.js) | 数学坐标、几何缓存、标签、相机、事件、抽屉 | 顶点表/渲染坐标、场景组、state、checks、球材质、读数 |
| `showFullSolution / focusProof` | 初始展开与概览定位 | 新题推导卡数量改变时同步边界；定位不能重置设置 |
| `invalidate / render / resize` | 按需渲染及模型适配 | 保留机制；按新题重算模型包围半径和中心 |
| `pickVertex / measureLabels / syncLabels` | 命中与标签缓存 | 点名和坐标需替换，保留命中与尺寸缓存 |
| [build_demo.py](开发资料/build_demo.py) | 从本例源码重建单双文件 | 此脚本只适用于当前示例目录层级 |

图层映射：`cSolid→solid`，`cSphere→sphere`，`cDiameter→diameter`，`cGuide→guide`，`cAngles→angles`，`cAxes→axes`。其他通用项为 `cLabels/cLengths`、`sFont/sOpacity`、`data-quality` 与顶点选择集合。新增或删除图层时同步 DOM、state 和实际 scene group。

本例无直接拖动动点。鼠标/手指拖动空白或固定顶点后移过阈值，会调整相机；轻点顶点/标签切换高亮。不要把固定点拖动误写成移动其空间坐标。

## 截图参照

| 视口 | 模型 | 完整讲解 | 显示设置 |
|---|---|---|---|
| 电脑 1600×1000 | [截图](开发资料/验证记录/截图/desktop.png)（含常驻讲解） | 同左 | [截图](开发资料/验证记录/截图/desktop-settings.png) |
| 平板竖屏 820×1180 | [截图](开发资料/验证记录/截图/portrait.png) | [底部抽屉](开发资料/验证记录/截图/portrait-proof.png) | [底部抽屉](开发资料/验证记录/截图/portrait-settings.png) |
| 平板横屏 1180×820 | [截图](开发资料/验证记录/截图/landscape.png) | [左侧抽屉](开发资料/验证记录/截图/landscape-proof.png) | [左侧抽屉](开发资料/验证记录/截图/landscape-settings.png) |
| 手机 390×844 | [截图](开发资料/验证记录/截图/phone.png) | [截图](开发资料/验证记录/截图/phone-proof.png) | [截图](开发资料/验证记录/截图/phone-settings.png) |

![电脑默认画面](开发资料/验证记录/截图/desktop.png)

## 复现与证据

以下是示例维护入口，在仓库根目录、当前 Python/Node 环境运行，会重写本例源码工作 HTML、成品及验证记录。若只想隔离复现，先按 [换题指南](../../references/example-guide.md) 复制源码、运行通用组装器和打包器，不运行示例维护构建器。

```bash
python "examples/外接球题建模示例/开发资料/build_demo.py"
node "examples/外接球题建模示例/开发资料/check_math.mjs"
python "examples/外接球题建模示例/开发资料/check_browser.py"
python "examples/外接球题建模示例/开发资料/inspect_demo.py"
```

浏览器由 `GEO3D_BROWSER`（或 `BROWSER_EXECUTABLE_PATH`）可选指定；未指定则用 Playwright Chromium，首次需按 [验证文档](../../references/verification.md) 安装开发依赖与浏览器。脚本默认测试本例成品，也接受替代成品目录以验证重建输出。

已有 [browser-report.json](开发资料/验证记录/browser-report.json) 记录 114 项检查，缓存几何数量 31、静止额外渲染帧 0。这是具体历史版本的证据，不是新题的固定数量门槛。来源为 Chrome/Chromium、鼠标与可信 CDP 触摸、模拟平板视口；实体 iPad/Safari 尚未覆盖。

标签是有限轮次避让。更换题目、增加标签或改变字号后，仍须重新检查各视口和公式区，不承诺任意密度都无重叠。
