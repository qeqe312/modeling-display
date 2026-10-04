# 正四棱台2023真题演示 · 参考导读

用途：一个点沿棱运动，模型、滑条和实时数学读数同步。默认 P 位于 CC′ 中点，同时显示题目涉及的辅助平面。

- [离线单文件成品](https://github.com/qeqe312/modeling-display/blob/main/examples/%E6%AD%A3%E5%9B%9B%E6%A3%B1%E5%8F%B02023%E7%9C%9F%E9%A2%98%E6%BC%94%E7%A4%BA/%E6%88%90%E5%93%81/%E6%AD%A3%E5%9B%9B%E6%A3%B1%E5%8F%B02023%E7%9C%9F%E9%A2%98%E6%BC%94%E7%A4%BA.html)（[本地](成品/正四棱台2023真题演示.html)）
- [统一页面规范](https://github.com/qeqe312/modeling-display/blob/main/references/page-spec.md)（[本地](../../references/page-spec.md)） · [换题步骤](https://github.com/qeqe312/modeling-display/blob/main/references/example-guide.md)（[本地](../../references/example-guide.md)） · [实现要点](https://github.com/qeqe312/modeling-display/blob/main/references/implementation.md)（[本地](../../references/implementation.md)）

## 原题与数学基准

正四棱台 ABCD–A′B′C′D′，AB=2A′B′，P 在 CC′ 上。第一问：P 为中点时，棱锥 P–BCD 与棱台剩余部分的体积比。第二问：侧棱与底面成 60°，平面 A′BD⊥平面 PBD 时，求 PA 与平面 PBC 所成角的正弦值。

取 AB=2、A′B′=1（等比缩放不改答案），h=√6/2。教学坐标：

```text
A=(-1,-1,0) B=(1,-1,0) C=(1,1,0) D=(-1,1,0)
A′=(-.5,-.5,h) B′=(.5,-.5,h) C′=(.5,.5,h) D′=(-.5,.5,h)
t=CP/CC′ ∈ [0,1]
P=(1−t/2,1−t/2,ht)
```

渲染变换 `(x,y,z)→(x,z−h/2,−y)`。棱锥体积 V₁=2th/3，剩余体积 V₂=(7−2t)h/3；中点为 **1:6**。这里 V₂ 是“剩余”，不能混成整个棱台的 1:7。

平面法向量可取 n₁=(2h,2h,2)，n₂=(2ht,2ht,2t−4)，内积=16t−8，所以垂直条件 t=1/2。此时 **sinθ=4√273/91≈0.7262730392**，θ≈46.57485°。垂足 F=(5/7,−1,4h/7) 对本题 t>0 的平面 PBC 固定；新题不得照搬固定 F。

**t=0 时 P=C，平面 PBC 退化，θ 未定义。** 页面隐藏该角相关对象、读数显示“未定义”，不能把 t→0 的极限当作端点角度。独立验算见 [check_math.mjs](https://github.com/qeqe312/modeling-display/blob/main/examples/%E6%AD%A3%E5%9B%9B%E6%A3%B1%E5%8F%B02023%E7%9C%9F%E9%A2%98%E6%BC%94%E7%A4%BA/%E5%BC%80%E5%8F%91%E8%B5%84%E6%96%99/check_math.mjs)（[本地](开发资料/check_math.mjs)）。

## 默认状态和控件映射

| 项目 | 默认值 / 绑定 |
|---|---|
| 动点 | t=0.5；“显示设置”最前含滑条、端点/中点快捷位置、运动读数 |
| 主要图层 | `cSolid→solid`、`cPlane1→plane1`、`cPlane2→plane2`、`cLineAngle→lineAngle` 开启 |
| 可选图层 | `cVolume→volume`、`cAngles→angles`、`cAxes→axes` 关闭 |
| 文字 | 顶点字母开启、边长关闭；字号 22px（14–32） |
| 透明度 | 主体面 8%，范围 0–30%；改变全部主体面材质 |
| 精细度与选择 | 自动；无初始选择，多选累积；P 保留橙色球与光晕作为拖动提示 |

可见的运动滑条与舞台直接拖动必须共用 `setT()`。模型里的 P 球和偏移后的 P 标签都可抓取，轨迹范围由同一入口钳制。抓住 P 时相机方位、仰角、距离、target 都锁定，第二根手指和滚轮不能改变相机。

## 文件与关键实现入口

| 文件/入口 | 责任 | 换题时关注 |
|---|---|---|
| [layout.html](https://github.com/qeqe312/modeling-display/blob/main/examples/%E6%AD%A3%E5%9B%9B%E6%A3%B1%E5%8F%B02023%E7%9C%9F%E9%A2%98%E6%BC%94%E7%A4%BA/%E5%BC%80%E5%8F%91%E8%B5%84%E6%96%99/%E6%BA%90%E7%A0%81/layout.html)（[本地](开发资料/源码/layout.html)） | 完整解答、运动/显示设置、舞台浮层 | 原题、四张推导、`data-proof`、滑条读数、图层文字 |
| [style.css](https://github.com/qeqe312/modeling-display/blob/main/examples/%E6%AD%A3%E5%9B%9B%E6%A3%B1%E5%8F%B02023%E7%9C%9F%E9%A2%98%E6%BC%94%E7%A4%BA/%E5%BC%80%E5%8F%91%E8%B5%84%E6%96%99/%E6%BA%90%E7%A0%81/style.css)（[本地](开发资料/源码/style.css)） | 与外接球共享基础样式，末尾增加动点组件 | 保留后置完整解题覆盖块；长公式与读数宽度可微调 |
| [model.js](https://github.com/qeqe312/modeling-display/blob/main/examples/%E6%AD%A3%E5%9B%9B%E6%A3%B1%E5%8F%B02023%E7%9C%9F%E9%A2%98%E6%BC%94%E7%A4%BA/%E5%BC%80%E5%8F%91%E8%B5%84%E6%96%99/%E6%BA%90%E7%A0%81/model.js)（[本地](开发资料/源码/model.js)） | 顶点、数学、模型缓存、标签、动点参数 | `calculate / setT / screenToT`、坐标映射、依赖图形和退化 |
| [engine.js](https://github.com/qeqe312/modeling-display/blob/main/examples/%E6%AD%A3%E5%9B%9B%E6%A3%B1%E5%8F%B02023%E7%9C%9F%E9%A2%98%E6%BC%94%E7%A4%BA/%E5%BC%80%E5%8F%91%E8%B5%84%E6%96%99/%E6%BA%90%E7%A0%81/engine.js)（[本地](开发资料/源码/engine.js)） | 相机、按需渲染、手势、抽屉、设置监听 | 保留指针归属、捕获清理、相机锁定与标签缓存 |
| `setT` | 唯一参数更新入口 | 同步世界/教学坐标、滑条、读数、图形、选中 P 的坐标 |
| `screenToT` | 考虑 camera viewOffset 的射线–棱最近点反解 | 只适用于直棱；曲线要另推反解；退化返回 null |
| `focusProof` | 概览定位讲解 | 不改 t、图层、相机或选择集合 |
| [build_demo.py](https://github.com/qeqe312/modeling-display/blob/main/examples/%E6%AD%A3%E5%9B%9B%E6%A3%B1%E5%8F%B02023%E7%9C%9F%E9%A2%98%E6%BC%94%E7%A4%BA/%E5%BC%80%E5%8F%91%E8%B5%84%E6%96%99/build_demo.py)（[本地](开发资料/build_demo.py)） | 拼接两份 JS，再重建已有单双文件 | 只适用于本例目录层级 |

`model.js` 与 `engine.js` 共用同一 IIFE；构建生成的 `app.js` 不应作为唯一修改来源。动态直线共享单位 TubeGeometry，以变换表示长度方向；三角形缓冲原地更新。移动 t 不新建材质、几何或 DOM 标签。

抓取标签时保存参数偏移避免第一次移动跳点；端点重合时 P 球优先命中，但其他顶点标签仍可点选。鼠标/触摸/笔采用同一状态机。取消、失焦或横竖屏切换必须清理手势，不留下相机锁死。

## 截图参照

| 视口 | 模型 | 完整讲解 | 显示设置 |
|---|---|---|---|
| 电脑 1600×1000 | [默认画面](https://github.com/qeqe312/modeling-display/blob/main/examples/%E6%AD%A3%E5%9B%9B%E6%A3%B1%E5%8F%B02023%E7%9C%9F%E9%A2%98%E6%BC%94%E7%A4%BA/%E5%BC%80%E5%8F%91%E8%B5%84%E6%96%99/%E9%AA%8C%E8%AF%81%E8%AE%B0%E5%BD%95/%E6%88%AA%E5%9B%BE/%E7%94%B5%E8%84%91-%E6%A8%A1%E5%9E%8B.png)（[本地](开发资料/验证记录/截图/电脑-模型.png)） | [常驻面板](https://github.com/qeqe312/modeling-display/blob/main/examples/%E6%AD%A3%E5%9B%9B%E6%A3%B1%E5%8F%B02023%E7%9C%9F%E9%A2%98%E6%BC%94%E7%A4%BA/%E5%BC%80%E5%8F%91%E8%B5%84%E6%96%99/%E9%AA%8C%E8%AF%81%E8%AE%B0%E5%BD%95/%E6%88%AA%E5%9B%BE/%E7%94%B5%E8%84%91-%E9%A2%98%E7%9B%AE%E8%AE%B2%E8%A7%A3.png)（[本地](开发资料/验证记录/截图/电脑-题目讲解.png)） | [设置](https://github.com/qeqe312/modeling-display/blob/main/examples/%E6%AD%A3%E5%9B%9B%E6%A3%B1%E5%8F%B02023%E7%9C%9F%E9%A2%98%E6%BC%94%E7%A4%BA/%E5%BC%80%E5%8F%91%E8%B5%84%E6%96%99/%E9%AA%8C%E8%AF%81%E8%AE%B0%E5%BD%95/%E6%88%AA%E5%9B%BE/%E7%94%B5%E8%84%91-%E6%98%BE%E7%A4%BA%E8%AE%BE%E7%BD%AE.png)（[本地](开发资料/验证记录/截图/电脑-显示设置.png)） |
| 平板竖屏 820×1180 | [模型](https://github.com/qeqe312/modeling-display/blob/main/examples/%E6%AD%A3%E5%9B%9B%E6%A3%B1%E5%8F%B02023%E7%9C%9F%E9%A2%98%E6%BC%94%E7%A4%BA/%E5%BC%80%E5%8F%91%E8%B5%84%E6%96%99/%E9%AA%8C%E8%AF%81%E8%AE%B0%E5%BD%95/%E6%88%AA%E5%9B%BE/%E5%B9%B3%E6%9D%BF%E7%AB%96%E5%B1%8F-%E6%A8%A1%E5%9E%8B.png)（[本地](开发资料/验证记录/截图/平板竖屏-模型.png)） | [底部抽屉](https://github.com/qeqe312/modeling-display/blob/main/examples/%E6%AD%A3%E5%9B%9B%E6%A3%B1%E5%8F%B02023%E7%9C%9F%E9%A2%98%E6%BC%94%E7%A4%BA/%E5%BC%80%E5%8F%91%E8%B5%84%E6%96%99/%E9%AA%8C%E8%AF%81%E8%AE%B0%E5%BD%95/%E6%88%AA%E5%9B%BE/%E5%B9%B3%E6%9D%BF%E7%AB%96%E5%B1%8F-%E9%A2%98%E7%9B%AE%E8%AE%B2%E8%A7%A3.png)（[本地](开发资料/验证记录/截图/平板竖屏-题目讲解.png)） | [底部抽屉](https://github.com/qeqe312/modeling-display/blob/main/examples/%E6%AD%A3%E5%9B%9B%E6%A3%B1%E5%8F%B02023%E7%9C%9F%E9%A2%98%E6%BC%94%E7%A4%BA/%E5%BC%80%E5%8F%91%E8%B5%84%E6%96%99/%E9%AA%8C%E8%AF%81%E8%AE%B0%E5%BD%95/%E6%88%AA%E5%9B%BE/%E5%B9%B3%E6%9D%BF%E7%AB%96%E5%B1%8F-%E6%98%BE%E7%A4%BA%E8%AE%BE%E7%BD%AE.png)（[本地](开发资料/验证记录/截图/平板竖屏-显示设置.png)） |
| 平板横屏 1180×820 | [模型](https://github.com/qeqe312/modeling-display/blob/main/examples/%E6%AD%A3%E5%9B%9B%E6%A3%B1%E5%8F%B02023%E7%9C%9F%E9%A2%98%E6%BC%94%E7%A4%BA/%E5%BC%80%E5%8F%91%E8%B5%84%E6%96%99/%E9%AA%8C%E8%AF%81%E8%AE%B0%E5%BD%95/%E6%88%AA%E5%9B%BE/%E5%B9%B3%E6%9D%BF%E6%A8%AA%E5%B1%8F-%E6%A8%A1%E5%9E%8B.png)（[本地](开发资料/验证记录/截图/平板横屏-模型.png)） | [左侧抽屉](https://github.com/qeqe312/modeling-display/blob/main/examples/%E6%AD%A3%E5%9B%9B%E6%A3%B1%E5%8F%B02023%E7%9C%9F%E9%A2%98%E6%BC%94%E7%A4%BA/%E5%BC%80%E5%8F%91%E8%B5%84%E6%96%99/%E9%AA%8C%E8%AF%81%E8%AE%B0%E5%BD%95/%E6%88%AA%E5%9B%BE/%E5%B9%B3%E6%9D%BF%E6%A8%AA%E5%B1%8F-%E9%A2%98%E7%9B%AE%E8%AE%B2%E8%A7%A3.png)（[本地](开发资料/验证记录/截图/平板横屏-题目讲解.png)） | [左侧抽屉](https://github.com/qeqe312/modeling-display/blob/main/examples/%E6%AD%A3%E5%9B%9B%E6%A3%B1%E5%8F%B02023%E7%9C%9F%E9%A2%98%E6%BC%94%E7%A4%BA/%E5%BC%80%E5%8F%91%E8%B5%84%E6%96%99/%E9%AA%8C%E8%AF%81%E8%AE%B0%E5%BD%95/%E6%88%AA%E5%9B%BE/%E5%B9%B3%E6%9D%BF%E6%A8%AA%E5%B1%8F-%E6%98%BE%E7%A4%BA%E8%AE%BE%E7%BD%AE.png)（[本地](开发资料/验证记录/截图/平板横屏-显示设置.png)） |
| 手机 390×844 | [模型](https://github.com/qeqe312/modeling-display/blob/main/examples/%E6%AD%A3%E5%9B%9B%E6%A3%B1%E5%8F%B02023%E7%9C%9F%E9%A2%98%E6%BC%94%E7%A4%BA/%E5%BC%80%E5%8F%91%E8%B5%84%E6%96%99/%E9%AA%8C%E8%AF%81%E8%AE%B0%E5%BD%95/%E6%88%AA%E5%9B%BE/%E6%89%8B%E6%9C%BA-%E6%A8%A1%E5%9E%8B.png)（[本地](开发资料/验证记录/截图/手机-模型.png)） | [讲解](https://github.com/qeqe312/modeling-display/blob/main/examples/%E6%AD%A3%E5%9B%9B%E6%A3%B1%E5%8F%B02023%E7%9C%9F%E9%A2%98%E6%BC%94%E7%A4%BA/%E5%BC%80%E5%8F%91%E8%B5%84%E6%96%99/%E9%AA%8C%E8%AF%81%E8%AE%B0%E5%BD%95/%E6%88%AA%E5%9B%BE/%E6%89%8B%E6%9C%BA-%E9%A2%98%E7%9B%AE%E8%AE%B2%E8%A7%A3.png)（[本地](开发资料/验证记录/截图/手机-题目讲解.png)） | [设置](https://github.com/qeqe312/modeling-display/blob/main/examples/%E6%AD%A3%E5%9B%9B%E6%A3%B1%E5%8F%B02023%E7%9C%9F%E9%A2%98%E6%BC%94%E7%A4%BA/%E5%BC%80%E5%8F%91%E8%B5%84%E6%96%99/%E9%AA%8C%E8%AF%81%E8%AE%B0%E5%BD%95/%E6%88%AA%E5%9B%BE/%E6%89%8B%E6%9C%BA-%E6%98%BE%E7%A4%BA%E8%AE%BE%E7%BD%AE.png)（[本地](开发资料/验证记录/截图/手机-显示设置.png)） |

![电脑默认画面](开发资料/验证记录/截图/电脑-模型.png)

讲解 tab 的结构与外接球一致。所有截图都由 `inspect_demo.py` 从重建成品生成，视口、coarse 输入与页面错误记录在截图目录的 `inspection.json`；新增示例也应包含讲解和设置状态。

动点另有 [t=0.25 内部位置](https://github.com/qeqe312/modeling-display/blob/main/examples/%E6%AD%A3%E5%9B%9B%E6%A3%B1%E5%8F%B02023%E7%9C%9F%E9%A2%98%E6%BC%94%E7%A4%BA/%E5%BC%80%E5%8F%91%E8%B5%84%E6%96%99/%E9%AA%8C%E8%AF%81%E8%AE%B0%E5%BD%95/%E6%88%AA%E5%9B%BE/%E5%8A%A8%E7%82%B9-%E5%86%85%E9%83%A8%E4%BD%8D%E7%BD%AE.png)（[本地](开发资料/验证记录/截图/动点-内部位置.png)） 与 [P=C 的端点退化](https://github.com/qeqe312/modeling-display/blob/main/examples/%E6%AD%A3%E5%9B%9B%E6%A3%B1%E5%8F%B02023%E7%9C%9F%E9%A2%98%E6%BC%94%E7%A4%BA/%E5%BC%80%E5%8F%91%E8%B5%84%E6%96%99/%E9%AA%8C%E8%AF%81%E8%AE%B0%E5%BD%95/%E6%88%AA%E5%9B%BE/%E5%8A%A8%E7%82%B9-C%E7%AB%AF%E7%82%B9.png)（[本地](开发资料/验证记录/截图/动点-C端点.png)），供比较滑条、实时读数与辅助对象的变化。

## 复现与证据

以下是示例维护入口，在仓库根目录、当前 Python/Node 环境运行，会重写本例源码合并结果、成品及验证记录。若只想隔离复现，先按 [换题指南](https://github.com/qeqe312/modeling-display/blob/main/references/example-guide.md)（[本地](../../references/example-guide.md)） 复制源码、运行通用组装器和打包器，不运行示例维护构建器。

```bash
python "examples/正四棱台2023真题演示/开发资料/build_demo.py"
node "examples/正四棱台2023真题演示/开发资料/check_math.mjs"
python "examples/正四棱台2023真题演示/开发资料/check_browser.py"
python "examples/正四棱台2023真题演示/开发资料/inspect_demo.py"
```

环境安装与 `GEO3D_BROWSER` 可选设置见 [验收标准](https://github.com/qeqe312/modeling-display/blob/main/references/verification.md)（[本地](../../references/verification.md)）。已有 [browser-report.json](https://github.com/qeqe312/modeling-display/blob/main/examples/%E6%AD%A3%E5%9B%9B%E6%A3%B1%E5%8F%B02023%E7%9C%9F%E9%A2%98%E6%BC%94%E7%A4%BA/%E5%BC%80%E5%8F%91%E8%B5%84%E6%96%99/%E9%AA%8C%E8%AF%81%E8%AE%B0%E5%BD%95/browser-report.json)（[本地](开发资料/验证记录/browser-report.json)） 和 [验证说明](https://github.com/qeqe312/modeling-display/blob/main/examples/%E6%AD%A3%E5%9B%9B%E6%A3%B1%E5%8F%B02023%E7%9C%9F%E9%A2%98%E6%BC%94%E7%A4%BA/%E5%BC%80%E5%8F%91%E8%B5%84%E6%96%99/%E9%AA%8C%E8%AF%81%E8%AE%B0%E5%BD%95/%E9%AA%8C%E8%AF%81%E8%AF%B4%E6%98%8E.md)（[本地](开发资料/验证记录/验证说明.md)） 包含 187 项具体检查：轨迹、滑条同步、鼠标/可信 CDP 触摸、相机锁定、端点退化、缓存与静止渲染等。

图层全部预热后几何数量 27、静止额外帧 0。JS render CPU P95 是桌面提交与标签更新时间，不能解释为 GPU 完成时间、实体平板帧率或触摸延迟保证；最新值见 JSON，不使用某次耗时作为规范。实体 iPad/Safari 未实测；新题须重跑适用验收，不能沿用本题条数作为通过证据。
