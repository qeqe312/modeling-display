# 椭圆动圆切线与定距离（二维）· 参考导读

这是纯二维解析几何的首选参考：固定圆心、可变半径、两条切线、椭圆交点、垂足轨迹与定点定长。页面使用原生 Canvas 2D，不加载 Three.js；沿用暗色、完整解题、显示设置、390px 侧栏和触屏抽屉。

- [离线成品](https://github.com/qeqe312/modeling-display/blob/main/examples/%E6%A4%AD%E5%9C%86%E5%8A%A8%E5%9C%86%E5%88%87%E7%BA%BF%E4%B8%8E%E5%AE%9A%E8%B7%9D%E7%A6%BB%EF%BC%88%E4%BA%8C%E7%BB%B4%EF%BC%89/%E6%88%90%E5%93%81/%E6%A4%AD%E5%9C%86%E5%8A%A8%E5%9C%86%E5%88%87%E7%BA%BF%E4%B8%8E%E5%AE%9A%E8%B7%9D%E7%A6%BB.html)（[本地](成品/椭圆动圆切线与定距离.html)）
- [二维实现与换题经验](https://github.com/qeqe312/modeling-display/blob/main/references/plane-geometry.md)（[本地](../../references/plane-geometry.md)）
- [开发资料与重建命令](https://github.com/qeqe312/modeling-display/blob/main/examples/%E6%A4%AD%E5%9C%86%E5%8A%A8%E5%9C%86%E5%88%87%E7%BA%BF%E4%B8%8E%E5%AE%9A%E8%B7%9D%E7%A6%BB%EF%BC%88%E4%BA%8C%E7%BB%B4%EF%BC%89/%E5%BC%80%E5%8F%91%E8%B5%84%E6%96%99/README.md)（[本地](开发资料/README.md)）
- [源码](https://github.com/qeqe312/modeling-display/blob/main/examples/%E6%A4%AD%E5%9C%86%E5%8A%A8%E5%9C%86%E5%88%87%E7%BA%BF%E4%B8%8E%E5%AE%9A%E8%B7%9D%E7%A6%BB%EF%BC%88%E4%BA%8C%E7%BB%B4%EF%BC%89/%E5%BC%80%E5%8F%91%E8%B5%84%E6%96%99/%E6%BA%90%E7%A0%81/app.js)（[本地](开发资料/源码/app.js)） · [原题](https://github.com/qeqe312/modeling-display/blob/main/examples/%E6%A4%AD%E5%9C%86%E5%8A%A8%E5%9C%86%E5%88%87%E7%BA%BF%E4%B8%8E%E5%AE%9A%E8%B7%9D%E7%A6%BB%EF%BC%88%E4%BA%8C%E7%BB%B4%EF%BC%89/%E5%BC%80%E5%8F%91%E8%B5%84%E6%96%99/%E9%A2%98%E7%9B%AE/%E5%8E%9F%E9%A2%98.png)（[本地](开发资料/题目/原题.png)）
- [数学报告](https://github.com/qeqe312/modeling-display/blob/main/examples/%E6%A4%AD%E5%9C%86%E5%8A%A8%E5%9C%86%E5%88%87%E7%BA%BF%E4%B8%8E%E5%AE%9A%E8%B7%9D%E7%A6%BB%EF%BC%88%E4%BA%8C%E7%BB%B4%EF%BC%89/%E5%BC%80%E5%8F%91%E8%B5%84%E6%96%99/%E9%AA%8C%E8%AF%81%E8%AE%B0%E5%BD%95/math-report.json)（[本地](开发资料/验证记录/math-report.json)） · [浏览器报告](https://github.com/qeqe312/modeling-display/blob/main/examples/%E6%A4%AD%E5%9C%86%E5%8A%A8%E5%9C%86%E5%88%87%E7%BA%BF%E4%B8%8E%E5%AE%9A%E8%B7%9D%E7%A6%BB%EF%BC%88%E4%BA%8C%E7%BB%B4%EF%BC%89/%E5%BC%80%E5%8F%91%E8%B5%84%E6%96%99/%E9%AA%8C%E8%AF%81%E8%AE%B0%E5%BD%95/browser-report.json)（[本地](开发资料/验证记录/browser-report.json)） · [验证说明](https://github.com/qeqe312/modeling-display/blob/main/examples/%E6%A4%AD%E5%9C%86%E5%8A%A8%E5%9C%86%E5%88%87%E7%BA%BF%E4%B8%8E%E5%AE%9A%E8%B7%9D%E7%A6%BB%EF%BC%88%E4%BA%8C%E7%BB%B4%EF%BC%89/%E5%BC%80%E5%8F%91%E8%B5%84%E6%96%99/%E9%AA%8C%E8%AF%81%E8%AE%B0%E5%BD%95/%E9%AA%8C%E8%AF%81%E8%AF%B4%E6%98%8E.md)（[本地](开发资料/验证记录/验证说明.md)）
- [归档一致性报告](https://github.com/qeqe312/modeling-display/blob/main/examples/%E6%A4%AD%E5%9C%86%E5%8A%A8%E5%9C%86%E5%88%87%E7%BA%BF%E4%B8%8E%E5%AE%9A%E8%B7%9D%E7%A6%BB%EF%BC%88%E4%BA%8C%E7%BB%B4%EF%BC%89/%E5%BC%80%E5%8F%91%E8%B5%84%E6%96%99/%E9%AA%8C%E8%AF%81%E8%AE%B0%E5%BD%95/archive-report.json)（[本地](开发资料/验证记录/archive-report.json)）
- [桌面截图](https://github.com/qeqe312/modeling-display/blob/main/examples/%E6%A4%AD%E5%9C%86%E5%8A%A8%E5%9C%86%E5%88%87%E7%BA%BF%E4%B8%8E%E5%AE%9A%E8%B7%9D%E7%A6%BB%EF%BC%88%E4%BA%8C%E7%BB%B4%EF%BC%89/%E5%BC%80%E5%8F%91%E8%B5%84%E6%96%99/%E9%AA%8C%E8%AF%81%E8%AE%B0%E5%BD%95/%E6%88%AA%E5%9B%BE/%E7%94%B5%E8%84%91-%E6%A8%A1%E5%9E%8B.png)（[本地](开发资料/验证记录/截图/电脑-模型.png)） · [平板竖屏](https://github.com/qeqe312/modeling-display/blob/main/examples/%E6%A4%AD%E5%9C%86%E5%8A%A8%E5%9C%86%E5%88%87%E7%BA%BF%E4%B8%8E%E5%AE%9A%E8%B7%9D%E7%A6%BB%EF%BC%88%E4%BA%8C%E7%BB%B4%EF%BC%89/%E5%BC%80%E5%8F%91%E8%B5%84%E6%96%99/%E9%AA%8C%E8%AF%81%E8%AE%B0%E5%BD%95/%E6%88%AA%E5%9B%BE/%E5%B9%B3%E6%9D%BF%E7%AB%96%E5%B1%8F-%E6%A8%A1%E5%9E%8B.png)（[本地](开发资料/验证记录/截图/平板竖屏-模型.png)） · [平板横屏](https://github.com/qeqe312/modeling-display/blob/main/examples/%E6%A4%AD%E5%9C%86%E5%8A%A8%E5%9C%86%E5%88%87%E7%BA%BF%E4%B8%8E%E5%AE%9A%E8%B7%9D%E7%A6%BB%EF%BC%88%E4%BA%8C%E7%BB%B4%EF%BC%89/%E5%BC%80%E5%8F%91%E8%B5%84%E6%96%99/%E9%AA%8C%E8%AF%81%E8%AE%B0%E5%BD%95/%E6%88%AA%E5%9B%BE/%E5%B9%B3%E6%9D%BF%E6%A8%AA%E5%B1%8F-%E6%A8%A1%E5%9E%8B.png)（[本地](开发资料/验证记录/截图/平板横屏-模型.png)）

## 数学基准与图形含义

椭圆 `x²/4＋y²＝1`，A＝(−2,0)，D＝(0,2)，O＝(0,0)。r 的有效题意范围为 `0＜r＜2√2，r≠2`，初始 r＝1.4。

两条有限切线斜率满足 k₁k₂＝1。MN 所在直线为 `y＝m(x＋10/3)`，m＝3(4−r²)/32，恒过 E＝(−10/3,0)。P＝(−10m²/[3(1＋m²)],10m/[3(1＋m²)])；取 OE 中点 Q＝(−5/3,0)，|PQ|＝5/3。

紫色辅助圆是 `(x＋5/3)²＋y²＝25/9`；亮橙色实际轨迹只有两段开弧。O 与端点极限 (−30/73,±80/73) 不属于有效轨迹。r＝0、2、2√2 允许作边界观察，但 MN、P 的题意定义不成立，相关对象隐藏、读数显示“未定义”。

显示约定来自本题的用户反馈：

- 切线从 A 朝圆上切点延伸，到画布边缘，不加箭头；椭圆内为实线，超出椭圆为虚线。
- MN 只显示 M 到 N 的线段，不画延长线。E 仍用于证明直线 MN 过定点。
- 当 r＞2 时，M 位于对应射线反向；这条前向射线从 A 起就在椭圆外，因此全部为虚线。题目中的 AM 斜率仍属于整条直线。
- T₁、T₂ 是圆上的切点，与椭圆上的 M、N 不同；默认隐藏，可在设置打开。

这些是本题的绘图选择，不应把所有新题的直线强制改成射线，或把所有辅助线都隐藏。

## 源码边界与换题位置

| 文件 / 函数 | 可复用的内容 | 换题时必须重新推导 |
|---|---|---|
| `layout.html`、`style.css` | 两 tab、完整讲解、抽屉、公式概览、胶囊标签 | 原题、推导、控件名与图层映射 |
| `app.js` 的 `compute()`、`points`、`setR()` | 单一参数入口与同步职责 | 参数范围、交点、切点、垂足、读数及退化 |
| `screen()`、`world()`、`fit()` | 等单位平面变换、平移缩放、UI 预留 | 主体包围范围与默认尺度 |
| `ray()`、`shape()`、`render()` | 画布裁剪、CSS 像素虚线、缓存 Path2D | 实虚线分界：当前公式仅适用于 A 在本椭圆左顶点 |
| `pick()` 与 Pointer Events | 标签/点联合命中、按下一次判定、指针归属、视图锁定 | 把指针反解成新参数；本题半径拖动与圆弧角度反解不能照抄到任意曲线 |
| `syncLabels()`、`invalidate()` | 标签尺寸缓存、避让、按需渲染 | 标签集、长度标注与可见性 |
| `proof()`、`setDrawer()` | 定位推导保留状态、焦点与方向切换 | proof 映射与题目 tab 数量 |

`app.js` 按“题目数据/数学 → 平面映射/绘制 → 指针交互 → 页面控制”组织，构建直接读取保留的这份源码。先做新题数学，再替换题目依赖；保留共用输入和布局后，对新成品执行自己的独立数学与可信输入检查。

## 控件映射

`sR / data-r → setR → circle、M/N、P、滑条和读数`；圆周、R 及其标签都可拖。P 及其标签沿实际圆弧拖动，反解半径。动点期间 `view.cx、view.cy、view.scale` 全部锁定。

`data-layer → state` 包含 ellipse、circle、tangents、chord、projection、trace、aux、contact、grid；文字 labels/lengths 独立。字号默认22px、14–32px，填充透明度8%，精细度自动。顶点多选累积，空白点击保留。

成品只含单文件 HTML、说明和项目 MIT 许可证。没有第三方库，因此不需要 Three.js 许可证、双文件库或 ZIP。
