# 实现规范：复用已认可的引擎

纯二维题采用 [Canvas 平面实现](plane-geometry.md) 与[椭圆二维示例](../examples/椭圆动圆切线与定距离（二维）/REFERENCE.md)。本文件以下的相机、世界射线与 Mesh 说明面向空间三维；页面、标签、抽屉和按需渲染原则也适用于二维。

三维实现按 [示例索引](../examples/README.md) 选择固定、沿棱运动或翻折模型，不从历史模板重新发明交互。结构/外观见 [page-spec.md](page-spec.md)，逐文件换题方法见 [example-guide.md](example-guide.md)。这里解释影响正确性或流畅度的实现不变量。

## 1. 模块与更新职责

| 部分 | 固定模型参考 | 单动点参考 |
|---|---|---|
| 文案与 DOM | layout.html | layout.html |
| 视觉与响应式 | style.css | style.css（尾部增加运动组件） |
| 数学/对象/标签/读数 | app.js 的题目相关段 | model.js |
| 相机/输入/抽屉/渲染 | app.js 的【D】及后续部分 | engine.js |
| 组装顺序 | app.js | model.js → engine.js，合成一个 script |

动点 `model.js` 打开 IIFE，`engine.js` 关闭同一 IIFE；二者共享词法变量，不能拆成各自的 ES module 或两个独立 script。`源码/app.js` 是构建结果，不是动点例的编辑来源。

建议区分：教学坐标 `STANDARD`、渲染顶点 `V`、显示 `state`、`groups`、`selected:Set`、标签缓存 `labels`、相机 `cam/target`。字段名可改，但 HTML、事件、测试必须同步。

## 2. 数学坐标与模型适配

教学坐标选择便于证明的标准建系；渲染坐标可平移居中、换基。明确写出正向与逆向映射，选择列表显示教学坐标。

示例的映射不同：外接球 `(x,y,z)→(x−1.5,z−2.5,2−y)`；棱台 `(x,y,z)→(x,z−h/2,−y)`。不能把这些偏移照抄到新题。模型尺寸、适配包围半径、相机距离上下限、线半径也需要重新计算。

相机沿用三个示例的球坐标环绕方式，保持世界竖直方向向上：

```js
cam.elev = Math.max(-1.49, Math.min(1.49, cam.elev));
camera.up.set(0, 1, 0);
camera.position.set(
  target.x + cam.dist*Math.cos(cam.elev)*Math.sin(cam.azim),
  target.y + cam.dist*Math.sin(cam.elev),
  target.z + cam.dist*Math.cos(cam.elev)*Math.cos(cam.azim)
);
camera.lookAt(target);
camera.updateMatrixWorld();
```

FOV 默认40°。快捷视角默认300ms平滑过渡，减少动画偏好时立即设置。手动输入取消未完成的过渡。`resize()` 用实测 `.stage-bottom` 高度、顶部控件预留及模型包围半径计算 fit，并用 `setViewOffset` 把视觉中心移到可用区域；不能仅用全画布宽高导致模型压住公式。

鼠标与单指空白拖动共用 `cam.azim -= dx * .006`、`cam.elev += dy * .006`，位移使用 CSS 像素；仰角到达 ±1.49 rad 后反向拖动应立即恢复。保留 9px 拖动阈值，并补齐起点位移。除非用户另有要求，不改用轨迹球、相机滚转或连续翻转。

### 默认朝向与坐标同步

先确定模型的默认摆放：有明确底面时将该底面作为最低面；没有明确底面时优先选择一个顶点朝下。尽量避免最低支撑是一条棱，再选择能清楚显示关键结构的方位、仰角与距离。模型朝向和相机位置需要一起考虑，不能只调相机而忽略模型在世界竖直方向上的摆放。

初始状态、“立体”和“复位视角”共用所选默认视角；“居中”保留 `cam.azim` 与 `cam.elev`，只更新适配所需的 target、距离及视口偏移。用户手动旋转时不吸附默认朝向。

换基时明确教学坐标到渲染坐标的正逆映射，同步变换几何、坐标轴与辅助对象；选择列表、公式和读数仍使用教学坐标。例如正四面体以底面中心 F 为教学原点，映射为 `(x,y,z)→6(x,z−r,−y)`，使 BCD 水平且 A 朝上；该例的原点、倍率和偏移均不作为其他题目的固定要求。

## 3. 几何缓存

固定模型：一次建立几何，切图层只改 `visible`，改变透明度只改材质。材质按颜色/透明度复用，小球与选择光晕共享几何。

动态模型：拓扑不变时保持 BufferGeometry 和 Mesh 实例不变。

- 三角面：复用9个浮点坐标，写 `position.array`，置 `needsUpdate=true`；根据材质是否需要法线处理法线更新。
- 棱线：复用单位 TubeGeometry（单位y线段、半径1、径向6段），以 position、quaternion、scale 设置端点、长度与线半径。零长度时隐藏。
- 角弧：预分配线段/缓冲，随参数更新位置。轨迹变拓扑时可采用对象池，过量对象隐藏；仅不可复用的对象才创建/释放。
- 动态缓冲若不重算 bounds，可像棱台例明确 `frustumCulled=false`；否则需要更新边界，避免旧 bounds 错误裁剪。
- 顶点组与主体面组分离。隐藏面不应让顶点或主要棱线消失。

禁止把“每次 setT 删除 group 并创建 TubeGeometry/SphereGeometry”当作默认实现；也不能只 dispose 而继续逐帧分配。

## 4. 唯一参数入口

棱上点的约束先定义为 `P(t)=C+t(C′−C)`，`t∈[0,1]`。其它轨迹需要自己的参数化、合法域与反解。

```js
function setT(raw) {
  if (!Number.isFinite(raw)) return;
  state.t = Math.max(0, Math.min(1, raw));
  // 用题目参数化更新 P 与教学坐标。
  // 重新计算读数；更新既有动态 Mesh / buffer。
  // 同步 slider、快捷状态、运动读数、选中 P 的坐标。
  // 若对象定义性改变，更新图层/标签有效性。
  invalidate();
}
```

滑条 input、快捷按钮和模型拖动均调用此入口。计算用原始数值，格式化只发生在显示阶段；滑条步长造成的显示量化必须与位置精度说明一致。

## 5. 透视正确的棱上反解

从指针位置建立完整相机射线，包含投影矩阵的 view offset。不要只用 `projectionMatrix[0/5]` 手算方向，否则会丢掉偏移。

```js
// rayO/rayD/u/w 为缓存 Vector3；px/py 是相对 canvas 的 CSS 像素。
rayO.copy(camera.position);
rayD.set(2*px/width-1, 1-2*py/height, .5)
  .unproject(camera).sub(rayO).normalize();
u.subVectors(V.Cp,V.C);
w.subVectors(rayO,V.C);
const uu=u.lengthSq(), ud=u.dot(rayD);
const den=uu-ud*ud;
if (!Number.isFinite(den) || den<1e-9) return null;
const rawT=(w.dot(u)-ud*w.dot(rayD))/den;
return Number.isFinite(rawT) ? rawT : null;
```

这是单位射线与棱所在直线最近点的参数。先保留 rawT，在 `setT` 才限制范围；抓字母或球边缘时记录 `dragOffset=state.t−rawTAtDown`，移动使用 `rawT+dragOffset`，避免按下跳点。

接近平行/无效视口时返回 null、保持原位置，不产生突跳。原例的 aspect<0.35 或 >3 保护是实现选择；若新布局有更极端比例，应调整或改用适合该视口的方法并验证，不能声称拖动仍有效。

屏幕投影线段的比例在透视下不等于空间参数，不能代替解析反解。相机 pan、zoom、preset、view offset 后都需要往返验证。

## 6. 手势状态机

统一 Pointer Events 与 pointer capture，顺序为：右键/Shift平移、直接抓动点、空白旋转；第二指在普通相机操作中进入 pinch。

| 状态 | move 行为 | 结束条件 |
|---|---|---|
| point | 只允许所属 pointer 更新参数；保持整个相机不变 | 主指松开/取消；若还有手指留在屏幕，阻断至手指全部离开 |
| rotate | 超过9px后调整 azim/elev，首次补全从起点的位移 | 松开；未移动且<700ms才切换按下时命中的顶点 |
| pan | 按相机 right/up、视口高度和距离计算位移 | 松开 |
| pinch | 两指距离缩放，中心位移平移 | 降为一指后标记已移动，禁止误触点选 |
| blocked | 不移动点或相机 | 全部手指释放 |

点拖动时新手指与滚轮不能接管相机。松手不能二次 pick：保留 pointerdown 的 key。pointercancel 不触发选择；失焦、切方向、打开抽屉、文档隐藏均清理手势与捕获。

画布 `touch-action:none`，仅画布对可取消的 touchmove 防默认；不要阻止抽屉滚动或全页面用户缩放。右键 contextmenu 需拦截。

## 7. 点选与标签

普通球投影的默认容差为鼠标22px、触摸/pen40px，标签命中取实际显示矩形并包含相对画布偏移。端点处 P 球与静态端点重合时，应先识别 P 的近球核心，再识别各字母矩形，再考虑扩大容差，避免端点标签把动点抢走或过大 P 容差吞掉所有其它标签。

标签记录包含 key、position、visible、width/height、hit。文本/字号/显隐/选择样式改变后置 `metricsDirty`，下一次渲染批量测量。常规拖动中只读缓存，不交替修改DOM和读取offset尺寸。

`syncLabels()`：投影深度裁剪 → 基于中心外推 → 按实际矩形松弛避让 → 约束在可用模型区域 → 写 translate3d 与 hit。重合点需要确定的分离方向。隐藏标签清空 hit，避免幽灵命中。

多选采用 Set；再次轻点取消该点，轻点空白保持已有选择。清空按钮与 Escape 清除高亮。选择列表坐标随动点更新，但不会改标签字母或创建新几何。

## 8. 按需渲染与精细度

```js
function invalidate() {
  if (!frame && !contextLost && !document.hidden)
    frame=requestAnimationFrame(render);
}
function render(now) {
  frame=0;
  // 只有进行中的相机过渡才更新其状态。
  renderer.render(scene,camera);
  syncLabels();
  if (tween) invalidate();
}
```

输入事件合并到一个pending帧，静止时不持续轮询。页面隐藏、WebGL丢失时停止；恢复后请求一帧。不要为动点添加永久脉动动画来维持全速渲染。

两示例的精细度调的是像素比，不是几何细分：

`DPR=min(deviceDPR,模式上限,√(像素预算/(宽×高)))`

默认：自动200万像素、fine上限1.65/coarse1.35；清晰350万、上限2；省电上限1。根据设备/模型可调整预算，但不要默认使用无限制 deviceDPR。画布 resize 与 PixelRatio 同步，不能只改CSS导致模糊。

## 9. 抽屉、读数与错误

共用 `tabSelect`/`setDrawer`；抽屉开启为 dialog/aria-modal，管理焦点、Tab边界与关闭后焦点返回。关闭时使用 inert 防隐藏控件受焦；切方向自动关闭。

`focusProof()` 只切讲解 tab、打开必要的抽屉、突出并滚动对应卡片，不重置 state、cam、target、selected 或 t。手机临时隐藏的“复位视角”可以由其它入口完成同类操作。

读数注明当前/题设位置。法向量、投影或角度在退化状态下未定义时，显示“未定义”，同时隐藏无意义的对象与标签；不要显示 NaN 或为了视觉连续而编造数学值。

缺库、WebGL初始化失败或contextlost显示可读提示。`#geo-debug` 可暴露受控状态和测量句柄，普通页面不暴露；测试代码不能因此修改正式页面的默认行为。
