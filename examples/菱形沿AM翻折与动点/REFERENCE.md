# 菱形沿 AM 翻折与动点 · 参考导读

用途：平面图形绕固定折痕翻到空间、一个可直接拖动的圆弧动点，以及依赖动点的中点、连线、角度和体积联动。所有运动入口放在显示设置；打开即可阅读四项完整判断。

- [离线单文件成品](https://github.com/qeqe312/modeling-display/blob/main/examples/%E8%8F%B1%E5%BD%A2%E6%B2%BFAM%E7%BF%BB%E6%8A%98%E4%B8%8E%E5%8A%A8%E7%82%B9/%E6%88%90%E5%93%81/%E8%8F%B1%E5%BD%A2%E6%B2%BFAM%E7%BF%BB%E6%8A%98%E4%B8%8E%E5%8A%A8%E7%82%B9.html)（[本地](成品/菱形沿AM翻折与动点.html)）
- [页面规范](https://github.com/qeqe312/modeling-display/blob/main/references/page-spec.md)（[本地](../../references/page-spec.md)） · [换题指南](https://github.com/qeqe312/modeling-display/blob/main/references/example-guide.md)（[本地](../../references/example-guide.md)）
- [原题截图](https://github.com/qeqe312/modeling-display/blob/main/examples/%E8%8F%B1%E5%BD%A2%E6%B2%BFAM%E7%BF%BB%E6%8A%98%E4%B8%8E%E5%8A%A8%E7%82%B9/%E5%BC%80%E5%8F%91%E8%B5%84%E6%96%99/%E9%A2%98%E7%9B%AE/%E5%8E%9F%E9%A2%98.png)（[本地](开发资料/题目/原题.png)） · [题意确认](https://github.com/qeqe312/modeling-display/blob/main/examples/%E8%8F%B1%E5%BD%A2%E6%B2%BFAM%E7%BF%BB%E6%8A%98%E4%B8%8E%E5%8A%A8%E7%82%B9/%E5%BC%80%E5%8F%91%E8%B5%84%E6%96%99/%E9%A2%98%E7%9B%AE/%E9%A2%98%E6%84%8F%E7%A1%AE%E8%AE%A4.md)（[本地](开发资料/题目/题意确认.md)）

## 数学基准

菱形 ABCD，AB＝2、∠ABC＝60°，M 是 BC 中点。△ABM 绕 AM 翻折为 △AB₁M，N 为 B₁D 中点。答案 **A、C**。

```text
M=(0,0,0) A=(√3,0,0) B=(0,-1,0) C=(0,1,0) D=(√3,2,0)
φ∈[0,π], t=φ/π
B₁=(0,-cosφ,sinφ)
N=(√3/2,1-cosφ/2,sinφ/2)
render(x,y,z)=(x-√3/2,z-.45,.5-y)
inverse(X,Y,Z)=(X+√3/2,.5-Z,Y+.45)
```

固定底面 AMCD 位于 z＝0，折痕 AM 沿 x 轴；MB₁＝1，AB₁＝2。B₁ 沿上半圆，N 沿半径 1/2 的从属半圆，不能把 N 当成另一个任意动点。

| 判断 | 精确结论 |
|---|---|
| A | 0＜φ＜π 时，两面垂直，90° |
| B | CN＝1，取值集合 {1}；原选项 [1,√3] 错误 |
| C | AM 与 CN 夹角恒为 π/6＝30° |
| D | V＝(√3/3)sinφ，90° 最大；O＝(√3/2,1,1/2)，R＝√2，OC＝1，C 在球内 |

端点 0°、180° 时 B₁、M、C 共线，辅助平面未定义。外接球层只展示最大体积时的球：离开 90° 隐藏球面和 O，同时提示原因。

## 默认状态与控件

默认 φ＝60°，固定底面水平朝下，球坐标视角 azim＝0.42、elev＝0.46。原图灰色虚线、固定底面蓝色、翻折面与 B₁ 橙色、N 与 CN 紫色。

`cSolid→faces`、`cOriginal→original`、`cPlane1→plane1`、`cPlane2→plane2`、`cLineAngle→lineAngle`、`cAngles→angles` 默认打开。`cNTrack→nTrack`、`cVolume→volume`、`cSphere→sphere`、`cAxes→axes` 默认关闭。顶点字母开启、边长关闭，字号22px、主体面opacity0.14。

滑条、0°/90°/180°快捷位置、播放/暂停、速度15/30/60°每秒均在设置内。主画面仅有紧凑读数和直接拖点。播放在两个端点往返；抓 B₁、失焦或页面隐藏时暂停，静止不维持循环。

## 模型与交互入口

| 文件/函数 | 复用与修改边界 |
|---|---|
| [layout.html](https://github.com/qeqe312/modeling-display/blob/main/examples/%E8%8F%B1%E5%BD%A2%E6%B2%BFAM%E7%BF%BB%E6%8A%98%E4%B8%8E%E5%8A%A8%E7%82%B9/%E5%BC%80%E5%8F%91%E8%B5%84%E6%96%99/%E6%BA%90%E7%A0%81/layout.html)（[本地](开发资料/源码/layout.html)） | 保留两 tab、完整推导、运动控制和显示设置；替换原题、图层文字、公式与退化提示 |
| [style.css](https://github.com/qeqe312/modeling-display/blob/main/examples/%E8%8F%B1%E5%BD%A2%E6%B2%BFAM%E7%BF%BB%E6%8A%98%E4%B8%8E%E5%8A%A8%E7%82%B9/%E5%BC%80%E5%8F%91%E8%B5%84%E6%96%99/%E6%BA%90%E7%A0%81/style.css)（[本地](开发资料/源码/style.css)） | 保留认可的暗色侧栏/抽屉；末尾是播放控件与选项排版 |
| [model.js](https://github.com/qeqe312/modeling-display/blob/main/examples/%E8%8F%B1%E5%BD%A2%E6%B2%BFAM%E7%BF%BB%E6%8A%98%E4%B8%8E%E5%8A%A8%E7%82%B9/%E5%BC%80%E5%8F%91%E8%B5%84%E6%96%99/%E6%BA%90%E7%A0%81/model.js)（[本地](开发资料/源码/model.js)） | 坐标、折痕圆弧、从属关系、缓存几何、读数与状态 |
| `setT(value,fromPlayback)` | 唯一参数入口；同步 B₁、N、面/线、滑条、选点坐标、长度/夹角/体积和临界图层 |
| `screenToT(px,py)` | 屏幕点反投影为世界射线，交圆所在平面，再 atan2 恢复角度；不能复用棱上比例反解 |
| `screenToT` 的边视角分支 | 圆平面近乎侧对观察者时，计算圆上点到世界射线距离的局部极小值；投影重合则选接近当前参数的连续分支。退化投影没有唯一逆解 |
| `togglePlayback / advancePlayback` | 用户启动时请求动画帧，共用 setT 更新；暂停后恢复按需渲染 |
| [engine.js](https://github.com/qeqe312/modeling-display/blob/main/examples/%E8%8F%B1%E5%BD%A2%E6%B2%BFAM%E7%BF%BB%E6%8A%98%E4%B8%8E%E5%8A%A8%E7%82%B9/%E5%BC%80%E5%8F%91%E8%B5%84%E6%96%99/%E6%BA%90%E7%A0%81/engine.js)（[本地](开发资料/源码/engine.js)） | 从已认可的单动点引擎改编：保留相机、9px阈值、点选、双指、抽屉、缓存；动点命中改为 B₁，并加入播放调度 |
| [check_math.mjs](https://github.com/qeqe312/modeling-display/blob/main/examples/%E8%8F%B1%E5%BD%A2%E6%B2%BFAM%E7%BF%BB%E6%8A%98%E4%B8%8E%E5%8A%A8%E7%82%B9/%E5%BC%80%E5%8F%91%E8%B5%84%E6%96%99/check_math.mjs)（[本地](开发资料/check_math.mjs)） | 独立 Rodrigues 旋转、叉积、体积行列式、球心线性方程，不调用页面公式 |
| [check_browser.py](https://github.com/qeqe312/modeling-display/blob/main/examples/%E8%8F%B1%E5%BD%A2%E6%B2%BFAM%E7%BF%BB%E6%8A%98%E4%B8%8E%E5%8A%A8%E7%82%B9/%E5%BC%80%E5%8F%91%E8%B5%84%E6%96%99/check_browser.py)（[本地](开发资料/check_browser.py)） | 最终单文件断网加载，鼠标、CDP可信触摸、射线反解、所有控件、相机锁定和性能 |

一般折叠题应重新推导固定轴、旋转方向与合法角度，不照抄本题 x 轴或半圆。若固定轴任意，先在教学坐标中用 Rodrigues 旋转构造点，再把世界射线变换到圆的局部坐标反解。点的位置、边线和所有辅助对象仍由单一参数派生。

## 复现与截图

从仓库根目录，使用当前环境解释器：

```sh
python "examples/菱形沿AM翻折与动点/开发资料/build_demo.py"
node "examples/菱形沿AM翻折与动点/开发资料/check_math.mjs"
python "examples/菱形沿AM翻折与动点/开发资料/check_browser.py"
python "examples/菱形沿AM翻折与动点/开发资料/inspect_demo.py"
```

浏览器默认使用 Playwright Chromium，也可用 `GEO3D_BROWSER` 指向已有 Chromium 系浏览器，保持沙箱。

| 视口 | 模型 | 设置 | 全部答案 | 90° 外接球 |
|---|---|---|---|---|
| 1600×1000 | [电脑](https://github.com/qeqe312/modeling-display/blob/main/examples/%E8%8F%B1%E5%BD%A2%E6%B2%BFAM%E7%BF%BB%E6%8A%98%E4%B8%8E%E5%8A%A8%E7%82%B9/%E5%BC%80%E5%8F%91%E8%B5%84%E6%96%99/%E9%AA%8C%E8%AF%81%E8%AE%B0%E5%BD%95/%E6%88%AA%E5%9B%BE/%E7%94%B5%E8%84%91-%E6%A8%A1%E5%9E%8B.png)（[本地](开发资料/验证记录/截图/电脑-模型.png)） | [设置](https://github.com/qeqe312/modeling-display/blob/main/examples/%E8%8F%B1%E5%BD%A2%E6%B2%BFAM%E7%BF%BB%E6%8A%98%E4%B8%8E%E5%8A%A8%E7%82%B9/%E5%BC%80%E5%8F%91%E8%B5%84%E6%96%99/%E9%AA%8C%E8%AF%81%E8%AE%B0%E5%BD%95/%E6%88%AA%E5%9B%BE/%E7%94%B5%E8%84%91-%E6%98%BE%E7%A4%BA%E8%AE%BE%E7%BD%AE.png)（[本地](开发资料/验证记录/截图/电脑-显示设置.png)） | [答案](https://github.com/qeqe312/modeling-display/blob/main/examples/%E8%8F%B1%E5%BD%A2%E6%B2%BFAM%E7%BF%BB%E6%8A%98%E4%B8%8E%E5%8A%A8%E7%82%B9/%E5%BC%80%E5%8F%91%E8%B5%84%E6%96%99/%E9%AA%8C%E8%AF%81%E8%AE%B0%E5%BD%95/%E6%88%AA%E5%9B%BE/%E7%94%B5%E8%84%91-%E5%AE%8C%E6%95%B4%E7%AD%94%E6%A1%88.png)（[本地](开发资料/验证记录/截图/电脑-完整答案.png)） | [球面](https://github.com/qeqe312/modeling-display/blob/main/examples/%E8%8F%B1%E5%BD%A2%E6%B2%BFAM%E7%BF%BB%E6%8A%98%E4%B8%8E%E5%8A%A8%E7%82%B9/%E5%BC%80%E5%8F%91%E8%B5%84%E6%96%99/%E9%AA%8C%E8%AF%81%E8%AE%B0%E5%BD%95/%E6%88%AA%E5%9B%BE/%E7%94%B5%E8%84%91-%E6%9C%80%E5%A4%A7%E4%BD%93%E7%A7%AF%E5%A4%96%E6%8E%A5%E7%90%83.png)（[本地](开发资料/验证记录/截图/电脑-最大体积外接球.png)） |
| 820×1180 | [平板竖屏](https://github.com/qeqe312/modeling-display/blob/main/examples/%E8%8F%B1%E5%BD%A2%E6%B2%BFAM%E7%BF%BB%E6%8A%98%E4%B8%8E%E5%8A%A8%E7%82%B9/%E5%BC%80%E5%8F%91%E8%B5%84%E6%96%99/%E9%AA%8C%E8%AF%81%E8%AE%B0%E5%BD%95/%E6%88%AA%E5%9B%BE/%E5%B9%B3%E6%9D%BF%E7%AB%96%E5%B1%8F-%E6%A8%A1%E5%9E%8B.png)（[本地](开发资料/验证记录/截图/平板竖屏-模型.png)） | [设置](https://github.com/qeqe312/modeling-display/blob/main/examples/%E8%8F%B1%E5%BD%A2%E6%B2%BFAM%E7%BF%BB%E6%8A%98%E4%B8%8E%E5%8A%A8%E7%82%B9/%E5%BC%80%E5%8F%91%E8%B5%84%E6%96%99/%E9%AA%8C%E8%AF%81%E8%AE%B0%E5%BD%95/%E6%88%AA%E5%9B%BE/%E5%B9%B3%E6%9D%BF%E7%AB%96%E5%B1%8F-%E6%98%BE%E7%A4%BA%E8%AE%BE%E7%BD%AE.png)（[本地](开发资料/验证记录/截图/平板竖屏-显示设置.png)） | [答案](https://github.com/qeqe312/modeling-display/blob/main/examples/%E8%8F%B1%E5%BD%A2%E6%B2%BFAM%E7%BF%BB%E6%8A%98%E4%B8%8E%E5%8A%A8%E7%82%B9/%E5%BC%80%E5%8F%91%E8%B5%84%E6%96%99/%E9%AA%8C%E8%AF%81%E8%AE%B0%E5%BD%95/%E6%88%AA%E5%9B%BE/%E5%B9%B3%E6%9D%BF%E7%AB%96%E5%B1%8F-%E5%AE%8C%E6%95%B4%E7%AD%94%E6%A1%88.png)（[本地](开发资料/验证记录/截图/平板竖屏-完整答案.png)） | [球面](https://github.com/qeqe312/modeling-display/blob/main/examples/%E8%8F%B1%E5%BD%A2%E6%B2%BFAM%E7%BF%BB%E6%8A%98%E4%B8%8E%E5%8A%A8%E7%82%B9/%E5%BC%80%E5%8F%91%E8%B5%84%E6%96%99/%E9%AA%8C%E8%AF%81%E8%AE%B0%E5%BD%95/%E6%88%AA%E5%9B%BE/%E5%B9%B3%E6%9D%BF%E7%AB%96%E5%B1%8F-%E6%9C%80%E5%A4%A7%E4%BD%93%E7%A7%AF%E5%A4%96%E6%8E%A5%E7%90%83.png)（[本地](开发资料/验证记录/截图/平板竖屏-最大体积外接球.png)） |
| 1180×820 | [平板横屏](https://github.com/qeqe312/modeling-display/blob/main/examples/%E8%8F%B1%E5%BD%A2%E6%B2%BFAM%E7%BF%BB%E6%8A%98%E4%B8%8E%E5%8A%A8%E7%82%B9/%E5%BC%80%E5%8F%91%E8%B5%84%E6%96%99/%E9%AA%8C%E8%AF%81%E8%AE%B0%E5%BD%95/%E6%88%AA%E5%9B%BE/%E5%B9%B3%E6%9D%BF%E6%A8%AA%E5%B1%8F-%E6%A8%A1%E5%9E%8B.png)（[本地](开发资料/验证记录/截图/平板横屏-模型.png)） | [设置](https://github.com/qeqe312/modeling-display/blob/main/examples/%E8%8F%B1%E5%BD%A2%E6%B2%BFAM%E7%BF%BB%E6%8A%98%E4%B8%8E%E5%8A%A8%E7%82%B9/%E5%BC%80%E5%8F%91%E8%B5%84%E6%96%99/%E9%AA%8C%E8%AF%81%E8%AE%B0%E5%BD%95/%E6%88%AA%E5%9B%BE/%E5%B9%B3%E6%9D%BF%E6%A8%AA%E5%B1%8F-%E6%98%BE%E7%A4%BA%E8%AE%BE%E7%BD%AE.png)（[本地](开发资料/验证记录/截图/平板横屏-显示设置.png)） | [答案](https://github.com/qeqe312/modeling-display/blob/main/examples/%E8%8F%B1%E5%BD%A2%E6%B2%BFAM%E7%BF%BB%E6%8A%98%E4%B8%8E%E5%8A%A8%E7%82%B9/%E5%BC%80%E5%8F%91%E8%B5%84%E6%96%99/%E9%AA%8C%E8%AF%81%E8%AE%B0%E5%BD%95/%E6%88%AA%E5%9B%BE/%E5%B9%B3%E6%9D%BF%E6%A8%AA%E5%B1%8F-%E5%AE%8C%E6%95%B4%E7%AD%94%E6%A1%88.png)（[本地](开发资料/验证记录/截图/平板横屏-完整答案.png)） | [球面](https://github.com/qeqe312/modeling-display/blob/main/examples/%E8%8F%B1%E5%BD%A2%E6%B2%BFAM%E7%BF%BB%E6%8A%98%E4%B8%8E%E5%8A%A8%E7%82%B9/%E5%BC%80%E5%8F%91%E8%B5%84%E6%96%99/%E9%AA%8C%E8%AF%81%E8%AE%B0%E5%BD%95/%E6%88%AA%E5%9B%BE/%E5%B9%B3%E6%9D%BF%E6%A8%AA%E5%B1%8F-%E6%9C%80%E5%A4%A7%E4%BD%93%E7%A7%AF%E5%A4%96%E6%8E%A5%E7%90%83.png)（[本地](开发资料/验证记录/截图/平板横屏-最大体积外接球.png)） |
| 390×844 | [手机](https://github.com/qeqe312/modeling-display/blob/main/examples/%E8%8F%B1%E5%BD%A2%E6%B2%BFAM%E7%BF%BB%E6%8A%98%E4%B8%8E%E5%8A%A8%E7%82%B9/%E5%BC%80%E5%8F%91%E8%B5%84%E6%96%99/%E9%AA%8C%E8%AF%81%E8%AE%B0%E5%BD%95/%E6%88%AA%E5%9B%BE/%E6%89%8B%E6%9C%BA-%E6%A8%A1%E5%9E%8B.png)（[本地](开发资料/验证记录/截图/手机-模型.png)） | [设置](https://github.com/qeqe312/modeling-display/blob/main/examples/%E8%8F%B1%E5%BD%A2%E6%B2%BFAM%E7%BF%BB%E6%8A%98%E4%B8%8E%E5%8A%A8%E7%82%B9/%E5%BC%80%E5%8F%91%E8%B5%84%E6%96%99/%E9%AA%8C%E8%AF%81%E8%AE%B0%E5%BD%95/%E6%88%AA%E5%9B%BE/%E6%89%8B%E6%9C%BA-%E6%98%BE%E7%A4%BA%E8%AE%BE%E7%BD%AE.png)（[本地](开发资料/验证记录/截图/手机-显示设置.png)） | [答案](https://github.com/qeqe312/modeling-display/blob/main/examples/%E8%8F%B1%E5%BD%A2%E6%B2%BFAM%E7%BF%BB%E6%8A%98%E4%B8%8E%E5%8A%A8%E7%82%B9/%E5%BC%80%E5%8F%91%E8%B5%84%E6%96%99/%E9%AA%8C%E8%AF%81%E8%AE%B0%E5%BD%95/%E6%88%AA%E5%9B%BE/%E6%89%8B%E6%9C%BA-%E5%AE%8C%E6%95%B4%E7%AD%94%E6%A1%88.png)（[本地](开发资料/验证记录/截图/手机-完整答案.png)） | [球面](https://github.com/qeqe312/modeling-display/blob/main/examples/%E8%8F%B1%E5%BD%A2%E6%B2%BFAM%E7%BF%BB%E6%8A%98%E4%B8%8E%E5%8A%A8%E7%82%B9/%E5%BC%80%E5%8F%91%E8%B5%84%E6%96%99/%E9%AA%8C%E8%AF%81%E8%AE%B0%E5%BD%95/%E6%88%AA%E5%9B%BE/%E6%89%8B%E6%9C%BA-%E6%9C%80%E5%A4%A7%E4%BD%93%E7%A7%AF%E5%A4%96%E6%8E%A5%E7%90%83.png)（[本地](开发资料/验证记录/截图/手机-最大体积外接球.png)） |

验证数值、实际检查项和成品校验值见 [验证记录](https://github.com/qeqe312/modeling-display/blob/main/examples/%E8%8F%B1%E5%BD%A2%E6%B2%BFAM%E7%BF%BB%E6%8A%98%E4%B8%8E%E5%8A%A8%E7%82%B9/%E5%BC%80%E5%8F%91%E8%B5%84%E6%96%99/%E9%AA%8C%E8%AF%81%E8%AE%B0%E5%BD%95/%E9%AA%8C%E8%AF%81%E8%AF%B4%E6%98%8E.md)（[本地](开发资料/验证记录/验证说明.md)）。平板验证使用 Chrome 可信触摸/视口模拟；实体 iPad/Safari 未实测。
