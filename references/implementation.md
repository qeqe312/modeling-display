# 技术实现细节

本文件是 `SKILL.md` 的实现分册。代码片段供实现参考，具体页面必须经过独立数学及浏览器验证。
坐标约定：**y 轴向上**，模型沿 y 居中，`V.A` = A，`V.Ap` = A′。

---

## 1. 相机：自写球坐标

不使用 `examples/` 下的 OrbitControls（r148 后该目录已删除）。自写约 30 行，且能自由实现旋转/缩放/平移三合一。

```js
var cam = { azim: Math.PI * 0.24, elev: 0.34, dist: 6.6 };
var target = new THREE.Vector3(0, 0, 0);

function applyCamera() {
  cam.elev = Math.max(-1.5, Math.min(1.5, cam.elev));   // 钳制，防止翻面
  var ce = Math.cos(cam.elev);
  camera.position.set(
    target.x + cam.dist * ce * Math.sin(cam.azim),
    target.y + cam.dist * Math.sin(cam.elev),
    target.z + cam.dist * ce * Math.cos(cam.azim)
  );
  camera.lookAt(target);
}
```

**操作映射**

| 操作 | 手势 | 实现 |
|---|---|---|
| 旋转 | 左键拖拽 / 单指 | `cam.azim -= dx * 0.008; cam.elev += dy * 0.008` |
| 缩放 | 滚轮 / 双指捏合 | `cam.dist *= (1 + Math.sign(deltaY) * 0.09)` |
| 平移 | 右键或 Shift+左键 / 双指拖 | `right`/`up` 取 `camera.matrix` 第 0/1 列，`target.addScaledVector(right, -dx*k)`，`k = cam.dist * 0.0016` |

**必须** `canvas.addEventListener('contextmenu', e => e.preventDefault())`，否则右键平移会弹出菜单。

---

## 2. 命中检测：屏幕空间（不要用 Raycaster）

手指远比顶点小球粗，射线打在小球上基本打不中。

```js
function pickVertex(px, py, w, h, tol) {
  var best = null, bestD = Infinity;

  function test(key, pos, t) {
    var p = pos.clone().project(camera);      // 世界 → NDC
    if (p.z > 1) return;                      // 在相机背后
    var x = (p.x * 0.5 + 0.5) * w;            // NDC → 像素
    var y = (-p.y * 0.5 + 0.5) * h;           // 注意 y 翻转
    var d = Math.hypot(x - px, y - py);
    if (d < t && d < bestD) { bestD = d; best = key; }
  }

  Object.keys(V).forEach(function (k) { test(k, V[k], tol); });

  // ★ 动点用放大容差单独判一次，且优先于普通顶点：
  //   它常贴着端点（如 P 贴着 C、C′），不优先会出现"想拖 P 却选中 C′"
  test('P', computeP(), Math.max(tol, TOL_P));

  // ★ 标签矩形命中区（见第 5 节，解决"点字母点不中"）
  if (best !== 'P' && pLabelRect) {
    var r = pLabelRect;
    if (px >= r.x0 && px <= r.x1 && py >= r.y0 && py <= r.y1) best = 'P';
  }
  return best;
}
```

**容差集中定义**（不要在多处硬编码数字）：

```js
function pickTol(base, pointerType) {
  return (pointerType === 'touch' || pointerType === 'pen') ? base + 20 : base + 4;
}
var TOL_P = pickTol(22, 'mouse');   // → 鼠标 26px / 触摸 46px
// 普通顶点直接用 40(触摸) / 22(鼠标)
```

**共享的可变状态**（供 pickVertex 读标签矩形）：
```js
var selKeys = [];              // 选中顶点 key 数组（多选）
function isSel(k) { return selKeys.indexOf(k) >= 0; }
var pLabelRect = null;         // 由 syncLabels 每帧更新
var TOL_P = pickTol(22, 'mouse');
```

---

## 3. 拖动动点：射线–棱最近点解析解

### 为什么不能用屏幕线段投影

把棱的两端投影到屏幕连成线段、取指针的投影参数 —— **透视投影下三维棱上的等分点在屏幕上并不等分**。
透视投影下误差随相机、深度与采样位置变化，不把单次实验误差当成固定百分比；两端点投影本身仍应对应 t=0 和 t=1。

### 正确做法

```js
var _rayO = new THREE.Vector3(), _rayD = new THREE.Vector3();
var _segU = new THREE.Vector3(), _rayW = new THREE.Vector3();

// 屏幕像素 → 世界射线方向
function rayDirFromScreen(px, py, w, h) {
  var fy = camera.projectionMatrix.elements[5];   // = 1/tan(fov/2)，别自己重算
  var fx = camera.projectionMatrix.elements[0];   // = fy / aspect
  var ndcX = (px / w) * 2 - 1;
  var ndcY = -((py / h) * 2 - 1);                 // 屏幕 y 向下，NDC y 向上
  _rayO.setFromMatrixPosition(camera.matrixWorld);
  _rayD.set(ndcX / fx, ndcY / fy, -1)
    .applyMatrix4(new THREE.Matrix4().extractRotation(camera.matrixWorld))
    .normalize();
  return _rayD;
}

// 反算：屏幕点 → 棱 CC′ 上的参数 t
function screenToT(px, py, r) {
  var w = r.width, h = r.height;
  var aspect = w / h;
  if (!isFinite(aspect) || aspect < 0.35 || aspect > 3.0) return null;  // 畸形视口拦截

  var d = rayDirFromScreen(px, py, w, h);
  _segU.subVectors(V.Cp, V.C);                    // u = C′ − C
  _rayW.subVectors(_rayO, V.C);                   // w = 相机位置 − C

  var uu = _segU.dot(_segU), ud = _segU.dot(d), dd = d.dot(d);
  var uw = _rayW.dot(_segU), dw = _rayW.dot(d);
  var det = uu * (-dd) - (-ud) * ud;              // = −uu·dd + ud²
  if (!isFinite(det) || Math.abs(det) < 1e-9) return null;   // 棱与视线平行 → 退化

  var t = ((-dd) * uw + ud * dw) / det;           // ★ 符号极易写错，改动后必须重跑验算
  if (!isFinite(t)) return null;
  return Math.max(0, Math.min(1, t));             // 夹取到 [0,1]，拖出范围要贴住端点
}
```

### 精度（504 采样点 × 6 视角 × 4 视口）

| 方法 | 最大误差 |
|---|---|
| 屏幕线段投影（**不要用**） | 2.875e-2 |
| 射线最近点（**用这个**） | **2.887e-15** |

以上是历史特定配置的实验结果，未保留原始测试数据，不作为所有相机与视口的保证。当前可复现验算见 `tests/math.mjs`。

### 三重退化保护（缺一个就会跳变）
1. `det → 0`（棱几乎与视线平行）→ 返回 `null`，**不要**返回乱跳的 t
2. `aspect < 0.35` 或 `> 3.0`（面板展开/折叠过渡态）→ 返回 `null`
3. t 一律 clip 到 `[0,1]`

---

## 4. 手势三路分流（顺序即优先级）

```js
var gesture = null;      // null | 'rotate' | 'pan' | 'pinch' | 'dragP'
var ptrs = new Map();    // pointerId → {x, y}
var dragP = null, tapInfo = null;
```

### pointerdown
```js
if (ptrs.size === 1) {
  var r = canvas.getBoundingClientRect();
  var hot = pickVertex(e.clientX - r.left, e.clientY - r.top, r.width, r.height, TOL_P);

  // ① 最高优先级：按住动点
  if (hot === 'P' && e.button !== 2 && !e.shiftKey) {
    gesture = 'dragP';
    tapInfo = null;
    // ★ heldKey：记下"按下时抓住的是谁"，松手时直接复用，不二次命中
    dragP = { r: r, startT: state.t, lastT: state.t, movedEnough: false, heldKey: 'P' };
    setPHot(true);
    canvas.style.cursor = 'grabbing';
    return;
  }
  // ② 平移 / 旋转
  gesture = (e.button === 2 || e.shiftKey) ? 'pan' : 'rotate';
  tapInfo = { x: e.clientX, y: e.clientY, t: performance.now(),
              moved: false, type: e.pointerType, key: hot };   // ★ 同样记 key
  canvas.style.cursor = (gesture === 'pan') ? 'move' : 'grabbing';

} else if (ptrs.size === 2) {
  // ③ 双指
  gesture = 'pinch';
  tapInfo = null;          // 双指一定不是点选
  dragP = null;
  pinchStart = pinchGeom();
  camStartDist = cam.dist;
  targetStart.copy(target);
}
```

### pointermove（分支顺序不可乱）
```js
// 未按下时的悬停探测：鼠标端唯一的"此处可拖"暗示
if (!ptrs.has(e.pointerId)) {
  if (e.pointerType === 'mouse' && !gesture) {
    var rr = canvas.getBoundingClientRect();
    var hk = pickVertex(e.clientX - rr.left, e.clientY - rr.top, rr.width, rr.height, TOL_P);
    setPHot(hk === 'P');
    canvas.style.cursor = 'grab';
  }
  return;
}

if (gesture === 'dragP') {          // ★ 必须排在 pinch/pan/rotate 之前
  var t = screenToT(e.clientX - dragP.r.left, e.clientY - dragP.r.top, dragP.r);
  if (t !== null) {
    if (Math.abs(t - dragP.startT) > 0.02) dragP.movedEnough = true;  // t 空间阈值
    setT(t, true);
    dragP.lastT = t;
  }
  return;
}
// 以下是 pinch / pan / rotate
```

### pointerup
```js
function endPointer(e) {
  var wasSingle = (ptrs.size === 1);
  var wasDragP  = (gesture === 'dragP');
  ptrs.delete(e.pointerId);

  if (wasDragP) {
    if (dragP && !dragP.movedEnough) doTapKey(dragP.heldKey);   // ★ 复用，不重新判定
    dragP = null;
    setPHot(false);
    if (ptrs.size === 0) { gesture = null; canvas.style.cursor = 'grab'; }
    return;
  }

  // 点选：单指 + 几乎没动 + 按下够短
  if (wasSingle && gesture === 'rotate' && tapInfo && !tapInfo.moved &&
      performance.now() - tapInfo.t < 700) {
    if (tapInfo.key) doTapKey(tapInfo.key);                  // ★ 优先复用按下时的判定
    else doTap(e.clientX, e.clientY, tapInfo.type);          // 有位移时按松手位置重判
  }

  if (ptrs.size === 0) { gesture = null; tapInfo = null; pinchStart = null; canvas.style.cursor = 'grab'; }
  else if (ptrs.size === 1) {
    // 双指退回单指：重置基准并标记已移动，防止误触发点选
    var rest = ptrs.values().next().value;
    gesture = 'rotate';
    tapInfo = { x: rest.x, y: rest.y, t: performance.now(), moved: true, type: 'touch' };
  }
}
```

### 旋转的位移阈值
- 位移 **> 9px** 才认定是拖拽
- **越过阈值时必须补上"起点→当前"的完整位移**，否则前 9px 白拖，手感发涩
- 未越阈值时**不施加旋转**，否则轻点顶点画面会跳

### 点选状态切换（统一入口）
```js
function doTapKey(key) {
  if (!key) return;
  var i = selKeys.indexOf(key);
  if (i >= 0) selKeys.splice(i, 1);   // 再点已选 = 取消这一个（toggle）
  else        selKeys.push(key);      // 点新顶点 = 追加，旧高亮保持
  applyPickStyles();
}
```

---

## 5. 标签：同步、避让、命中区

### 为什么需要避让
侧向平视时上底面与视线近乎共面，`A′`–`B′` 投影间距实测仅 **11.6px**，任何字号都会叠字。

### syncLabels 要点
```js
function syncLabels() {
  if (!state.labels) { pLabelRect = null; return; }   // 关标签时清空，防止幽灵命中区

  var pts = [];
  labelEls.forEach(function (o) {
    var pos = o.getPos();
    var p = pos.clone().project(camera);
    if (p.z > 1) { o.el.classList.add('hide'); return; }
    o.el.classList.remove('hide');

    var x = (p.x * 0.5 + 0.5) * rect.width;
    var y = (-p.y * 0.5 + 0.5) * rect.height;

    // 沿"背离模型中心"方向外推
    var dx = x - rect.width / 2, dy = y - rect.height / 2;
    var len = Math.hypot(dx, dy) || 1;
    var off = labelSize * 1.35;

    pts.push({
      el: o.el,
      key: o.key,                    // ★★★ 必须带上！漏了会导致 pLabelRect 恒为 null
      bx: x + dx / len * off, by: y + dy / len * off,   // 基准位置
      x:  x + dx / len * off, y:  y + dy / len * off    // 实际位置（避让会改）
    });
  });

  // 松弛迭代：把过近的标签沿连线方向推开
  var minD = labelSize * 1.05 + 18;   // ★ 阈值要按"标签实际宽度"取，不能只按字号
  for (var iter = 0; iter < 12; iter++) {
    for (var i = 0; i < pts.length; i++) {
      for (var j = i + 1; j < pts.length; j++) {
        var ax = pts[i].x - pts[j].x, ay = pts[i].y - pts[j].y;
        var d = Math.hypot(ax, ay);
        if (d < minD && d > 0.01) {
          var push = (minD - d) / 2;
          ax /= d; ay /= d;
          pts[i].x += ax * push; pts[i].y += ay * push;
          pts[j].x -= ax * push; pts[j].y -= ay * push;
        }
      }
    }
  }

  // 限制漂移半径并落地
  var lim = labelSize * 1.35 * 2.2;
  pts.forEach(function (o) {
    var dx = o.x - o.bx, dy = o.y - o.by, d = Math.hypot(dx, dy);
    if (d > lim) { o.x = o.bx + dx / d * lim; o.y = o.by + dy / d * lim; }

    o.el.style.transform = 'translate(-50%,-50%) translate(' + o.x + 'px,' + o.y + 'px)';

    o.hit = {   // 命中矩形
      x0: o.x - o.el.offsetWidth  / 2, x1: o.x + o.el.offsetWidth  / 2,
      y0: o.y - o.el.offsetHeight / 2, y1: o.y + o.el.offsetHeight / 2
    };
    if (o.key === 'P') pLabelRect = o.hit;    // ★ 供 pickVertex 用
  });
}
```

**避让阈值教训**：最小间距必须按标签**实际宽度**取 `labelSize × 1.05 + 18`。
第一版按字号取 `× 1.15`，最坏情况只改善到 25.3px，仍小于 22px 字号下约 38px 的标签宽度。

**实测**（1200×720）：最坏视角 11.6px → 41.1px ✅；默认视角 55.3px 与俯视 70.0px 保持不变（无需避让时不位移）。

### 每帧调用顺序
```js
function loop() {
  requestAnimationFrame(loop);
  if (gesture === 'dragP' && pMesh) {          // 拖动时球体脉动，明确"抓住了"
    pPulse += 0.16;
    var s = 1.35 + Math.sin(pPulse) * 0.13;
    pMesh.scale.setScalar(isSel('P') ? s * 1.7 : s);
  }
  renderer.render(scene, camera);
  syncLabels();                                 // 必须在 render 之后
}
```

---

## 6. 几何与材料构建

```js
var COL = { /* 见 references/visual-theme.md */ };

function tube(a, b, r, color) {
  var geo = new THREE.TubeGeometry(new THREE.LineCurve3(a.clone(), b.clone()), 1, r, 6, false);
  return new THREE.Mesh(geo, new THREE.MeshBasicMaterial({ color: color }));
}

function glassMat(color, opacity) {
  return new THREE.MeshBasicMaterial({
    color: color, transparent: true, opacity: opacity,
    side: THREE.DoubleSide, depthWrite: false
  });
}
function triMesh(p1, p2, p3, color, opacity) {
  var geo = new THREE.BufferGeometry().setFromPoints([p1, p2, p3]);
  geo.setIndex([0, 1, 2]); geo.computeVertexNormals();
  return new THREE.Mesh(geo, glassMat(color, opacity));
}
function polyMesh(pts, color, opacity) {   // 凸多边形扇形三角化
  var geo = new THREE.BufferGeometry().setFromPoints(pts);
  var idx = [];
  for (var i = 1; i < pts.length - 1; i++) idx.push(0, i, i + 1);
  geo.setIndex(idx); geo.computeVertexNormals();
  return new THREE.Mesh(geo, glassMat(color, opacity));
}
```

**顶点小球必须独立成组**（`gVerts`），不能挂在"几何体实体"开关下——否则隐藏实体后顶点就点不到了。

**光晕对象池**：`ringPool` 按需增长、多余隐藏。绝不能每帧新建几何体（拖滑块会卡死）。

---

## 7. 常用可视化组件

| 组件 | 做法 |
|---|---|
| **平面** | 三点确定，`triMesh(p1,p2,p3,color,opacity)`，透明 0.30~0.40、`DoubleSide`、`depthWrite:false`。两平面的**公共棱单独加粗**强调 |
| **线面角** | 从直线端点 A 向平面作垂足 `H = A − ((A−P)·n̂)n̂`，画 A→H 垂线 + P→H 射影，`∠APH` 即所求角。比只画角标直观得多 |
| **二面角** | `acos(|n1·n2| / (|n1||n2|))`，动点驱动时实时刷新；满足临界条件（如垂直）时读数区变色 + 出标记 |
| **夹角可视化** | 如"侧棱与底面 60°"：画 A → A′(底面投影) → A′ 直角三角形 |

---

## 8. 动点重建机制

动点 `t` 变化时需要刷新所有依赖它的对象（动点位置、两个平面、棱锥、线面角）。

**用"重建 group + dispose 旧几何"的方式，不要试图原地改 BufferGeometry**：

```js
function rebuild(group, builder) {
  while (group.children.length) {
    var c = group.children.pop();
    if (c.geometry) c.geometry.dispose();
    if (c.material) c.material.dispose();
  }
  builder(group);
}

function setT(t, fromUser) {
  state.t = t;
  var sT = document.getElementById('sT');
  if (sT) sT.value = t;              // ★ 滑块与拖拽双向同步，共用这一个入口
  buildDynamic();                    // 重建动态几何
  refreshReadout();                  // 刷新读数
}
```

**滑块与拖拽必须共用同一个 `setT`**，不要各写一套。否则"跳到中点"按钮触发时两边会失配。

---

## 9. 读数格式化

```js
function fmt(v) {
  var s = v.toFixed(2).replace(/\.?0+$/, '');
  return s === '' ? '0' : s;        // ★ "0.00" 会被替换成空串，必须兜底
}
```

## 题目读数配置

`assets/template.html` 的【A】包含 `READOUT`：`angle(P)` 返回角度或 `null`，`critical(angle)` 返回是否提示临界条件，`coordinate(position)` 将模型坐标转换为教学坐标数组。换题时修改这些回调；静态模型把 `MOVER.enabled` 设为 false，不需要角度时把 `READOUT.angle` 与 `READOUT.critical` 设为 null。`P` 是引擎内部动点保留键，显示名由 `LABEL_NAME.P` 与 `MOVER.label` 配置。

比例按 `P=lerp(from,to,t)` 定义：`P到起点 : P到终点 = t : (1-t)`。不能把视觉上较长的投影段误当成实际长度。普通顶点名及坐标通过 DOM 的 `textContent` 渲染。
