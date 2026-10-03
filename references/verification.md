# 验算与自测规范

两道强制关卡：**数学必须独立验算，交互必须真实事件测试。**
只做静态代码检查不算验证。

---

## 一、数学验算（Node，独立重写）

**不复用页面代码——重新写一遍**，这才叫独立验证。

### 必查项

| # | 检查 | 方法 |
|---|---|---|
| 1 | 题目条件真的成立 | 用反三角函数反算。如"侧棱与底面成 60°"→ `asin(Δy / 棱长) × 180/π` 应得 60.0000 |
| 2 | 长度比 / 体积比 | 与理论值比对；**必须检查互补性**：`V₁ + V₂` 是否等于所在整体？ |
| 3 | 动点参数 | 解析解 == 数值解（二分法求点积零点），比对到 1e-9 |
| 4 | 最终答案 | 与精确形式比对到 1e-9，如 `4*Math.sqrt(273)/91` |
| 5 | 拖动反算精度 | 端点 0/0.25/0.5/0.75/1 的 round-trip 全还原；越界夹取；退化保护返回 null |
| 6 | 拖动连续性 | t 始终 ∈[0,1]，单向滑动时单调，单帧最大跳变 < 0.02 |
| 7 | 变化趋势 | 如两平面夹角随 t 的曲线（t=0→60°、t=0.5→90°、t=1→60°，关于 0.5 对称） |

### 关键教训

**手算期望值极易出错。** 曾把棱锥截面边长按"到顶点距离线性插值"算错，导致测试误报 FAIL。
凡是期望值，一律用公式现算，不要凭感觉估。

**⚠️ 验算脚本自己也会错，报错时先怀疑脚本。**

| 错误 | 现象 | 正确写法 |
|---|---|---|
| `project()` 写成 `zc = −dot(d, f)` | 前方点被误判"在相机背后"，所有采样被跳过，`maxErr = -Infinity` | `zc = dot(d, f)` |
| 相机基写成 `right = cross(upWorld, f)`，射线用 `+(-f)` | 深度判据全反 | `right = cross(f, upWorld)`（f = 相机→目标），射线方向相加用 `+f` |
| 动点 x/z **写死**成端点值 `[1, y, 1]` | 误报"页面 t=1/2 结论错误" | 必须真正 `lerp(C, C′, t)` |

第三条那个坑：改对后点积在 t=0.5 精确为 0 —— **页面一直是对的，是脚本错了。**

### 相机模型参考实现（Node）

```js
const FOV = 45 * Math.PI / 180;

function makeCam(azim, elev, dist, target) {
  const dir = [Math.cos(elev)*Math.sin(azim), Math.sin(elev), Math.cos(elev)*Math.cos(azim)];
  const pos = add(target, mul(dir, dist));
  const f = norm(sub(target, pos));            // ★ 相机前方单位向量
  const right = norm(cross(f, [0,1,0]));       // ★ f × up，不是 up × f
  const up = cross(right, f);
  return { pos, f, right, up };
}

function project(pt, cam, w, h) {
  const d = sub(pt, cam.pos);
  const zc = dot(d, cam.f);                    // ★ 前方点 zc > 0
  if (zc <= 1e-9) return null;
  const fy = 1 / Math.tan(FOV / 2), fx = fy / (w / h);
  return { x: dot(d, cam.right) * fx / zc, y: dot(d, cam.up) * fy / zc };
}

function rayDir(px, py, w, h, cam) {
  const fy = 1 / Math.tan(FOV / 2), fx = fy / (w / h);
  const ndcX = (px / w) * 2 - 1;
  const ndcY = -((py / h) * 2 - 1);
  return norm(add(add(mul(cam.right, ndcX / fx), mul(cam.up, ndcY / fy)), cam.f));  // ★ +f
}
```

---

## 二、交互自测（headless Chrome + 真实 PointerEvent）

### 为什么必须派发真实事件
静态代码检查查不出"按下了却选不中"这类状态机缺陷。只有真实事件序列才能覆盖。

### 方法
在页面副本末尾注入测试脚本，结果 JSON 写进 `document.title`，用 `--dump-dom` 读回：

```bash
chrome --headless=new --disable-gpu --no-sandbox --window-size=1400,900 \
       --virtual-time-budget=9000 --dump-dom "file:///.../_selftest.html" \
  | grep -o '<title>[^<]*</title>'
```

```js
function pe(type, x, y) {
  var o = { pointerId: 1, pointerType: 'mouse', isPrimary: true,
            clientX: x, clientY: y, bubbles: true, cancelable: true,
            button: 0, buttons: (type === 'pointerup' ? 0 : 1) };
  canvas.dispatchEvent(new PointerEvent(type, o));
}
function down(x,y){pe('pointerdown',x,y);}
function up(x,y){pe('pointerup',x,y);}
function move(x,y){pe('pointermove',x,y);}
```

### 页面侧需要暴露只读句柄
页面主逻辑通常包在 IIFE 里，外部测不到闭包变量。在 IIFE 末尾加（生产可整块删除）：

```js
window.__S = {
  state: state, cam: cam, camera: camera, selKeys: selKeys, renderer: renderer,
  setT: setT, applyPickStyles: applyPickStyles, screenToT: screenToT,
  pickVertex: pickVertex, computeP: computeP,
  get pLabelRect() { return pLabelRect; }
};
window.__GEO = {};
Object.keys(V).forEach(function (k) { window.__GEO[k] = V[k]; });
```

### 必测 12 项

| # | 用例 | 断言 |
|---|---|---|
| 1 | 点动点小球 | 能选中（`selKeys` 含该点） |
| 2 | 再点一次 | 取消选中 |
| 3 | 点动点**标签** | 能选中 ← 验证标签矩形命中区生效 |
| 4 | 从标签拖动 | t 改变且与起始值显著不同 |
| 5 | 滑块同步 | `slider.value ≈ state.t` |
| 6 | 拖拽时相机 | `azim / elev / dist` 漂移 **= 0** |
| 7 | 普通顶点点选 | 仍可用 ← **新增功能不得破坏既有能力** |
| 8 | 多选累积 | 点 A 再点 B → `['A','B']` |
| 9 | 点空白 | 已有高亮**不被清空** |
| 10 | 拖动动点 | 不误高亮其它顶点 |
| 11 | 空白处拖动 | 仍是旋转（`azim` 变化） |
| 12 | 反算往返精度 | 端点 0/0.25/0.5/0.75/1 全部还原（≤1e-12） |

### 主题类额外检查（改配色后）
```js
var cs = getComputedStyle(document.documentElement);
// 确认变量真的生效，且 body / panel 的实算背景色正确
// 应为 rgb(13,17,23)；若不同说明 --bg 被改动了
```

### ⚠️ 每次改源码后必须重新生成测试副本
否则测的是**旧副本**，修复看起来"没生效"。
生成脚本里加一句特征串断言，确认新代码确实进了副本：
```python
for token in ['doTapKey', "heldKey: 'P'", 'TOL_P']:
    assert token in copy, 'missing: ' + token
```

---

## 三、常见"假失败"（先排除这些再改代码）

| 现象 | 真因 |
|---|---|
| 往返精度 != 0，但量级 1e-16 | 这是**机器精度**，断言写成 `=== 0` 过严。改为 `< 1e-12` |
| 某功能"修复后仍失败" | 测试副本没重新生成，测的还是旧的 |
| 所有采样点被跳过，`maxErr = -Infinity` | 验算脚本的深度判据符号写反了 |
| 页面结论"错了"但代数算出来是对的 | 验算脚本里动点没真正插值，x/z 写死了 |

---

## 四、视觉确认（交付前）

用 headless Chrome 截图，**至少覆盖 3 种视口**：

```bash
# 桌面（宽屏，面板静态）
chrome --headless=new --window-size=1600,1000 --virtual-time-budget=8000 \
       --screenshot=shot_desktop.png "file:///.../演示.html"

# 窄屏（触屏断点边缘）
chrome --headless=new --window-size=780,1000 ...

# 平板竖屏（抽屉模式）
chrome --headless=new --window-size=820,1180 ...
```

逐张检查：
- [ ] 3D 模型完整、棱线清晰、没有颜色消失
- [ ] 顶点标签**无叠字**
- [ ] 面板文字**无深色叠深色**（暗色主题常见）
- [ ] 读数区数值与预期一致
- [ ] 平板竖屏是抽屉，不是左右挤压
