# 配色与视觉规范

**本项目只用暗色主题。** 不做亮色版本，也不要"顺手加一个亮色开关"。

目标：**投屏/平板在教室灯光下看得清，且不同题目的页面观感统一。**

全部颜色用 CSS 变量集中管理。整块替换 `<style>` 时按 `</style>` 索引定位，**不要用文本精确匹配**——`<style>` 块内的实际空白常与预期不符，精确匹配会失败。

---

## 1. 暗色色板（唯一版本）

```css
:root {
  --bg:        #0D1117;   /* 页面最底层 */
  --surface:   #161B22;   /* 面板、卡片 */
  --surface-2: #1C232C;   /* 内容块、代码块 */
  --surface-3: #232B36;   /* 浮起元素（按钮 active） */
  --line:      #2A3441;   /* 主分隔线 */
  --line-soft: #212A34;   /* 弱分隔线 */

  --ink:       #E6EDF3;   /* 主文字 */
  --ink-2:     #A9B6C4;   /* 次级文字 */
  --ink-3:     #8B99A8;   /* 三级文字 / 分组标题（★ 不能更暗，见 §5） */

  --brand:     #6BA8E8;   /* 学术蓝：结构、主色（深底上必须提亮） */
  --brand-lt:  #17293E;   /* 蓝的深色容器 */
  --accent:    #FF7A45;   /* 动点橙：动点、强调、选中 */
  --accent-lt: #2E1A11;   /* 橙的深色容器 */
  --green:     #8FBF5A;   /* 第1问卡片 */
  --green-lt:  #1A2413;
  --violet:    #A692E8;   /* 第2问卡片（紫，避开蓝橙） */
  --violet-lt: #1E1B2E;

  /* 深底上"黑色投影"几乎不可见 → 改"内描边（顶部高光）+ 外投影" */
  --shadow-s:  0 1px 2px rgba(0,0,0,.40), inset 0 1px 0 rgba(255,255,255,.03);
  --shadow-m:  0 4px 16px rgba(0,0,0,.50), inset 0 1px 0 rgba(255,255,255,.04);
  --radius:    12px;

  --glow-accent: rgba(255,122,69,.30);
  --glow-brand:  rgba(107,168,232,.28);
}
```

**画布背景**（`#stage`）加一层很淡的径向渐变，让 3D 区域有"舞台"感，比纯色更聚焦：
```css
background: radial-gradient(ellipse at 50% 42%, #1B232E 0%, #131A22 62%, #0B0F14 100%);
```

---

## 2. 3D 对象配色

颜色与 UI 强调色**必须是同一套**（动点橙 = 强调橙），学生视觉上才能建立关联。

```js
var COL = {
  edge:   0xB9C9DD,   // 棱线：亮蓝白（深色线条在暗底上会彻底消失）
  solid:  0x4A5A70,   // 半透明实体面
  plane1: 0x5EA0E0,   // 平面1（蓝）
  plane2: 0xFF7A45,   // 平面2（橙，与动点同色系）
  q1:     0x8FBF5A,   // 第1问对象
  q3:     0xE86A6A,   // 线面角
  q3face: 0x9B8BE8,
  ang60:  0x8FBF5A,
  axes:   0x6BA8E8,
  p:      0xFF7A45    // 动点，与 --accent 一致
};
var SEL_COLOR = 0xFF7A45;   // 选中高亮
```

**`renderer.setClearColor(0x131A22, 1)`** —— 画布不透明，必须与 `#stage` 渐变同色系。

### 半透明面透明度

深底上的低透明度深色**直接看不见**，所以透明度要比常见的亮色版高：

| 对象 | 透明度 |
|---|---|
| 底面 | 0.46 |
| 顶面 | 0.54 |
| 侧面 | 0.22 |
| 平面1 / 平面2 | 0.38 / 0.34 |
| 棱锥 | 0.42 |

---

## 3. 顶点标签：**胶囊样式（已定，不要改）**

标签用**深色胶囊底 + 描边**，不用"纯描边文字"。理由：胶囊底能保证字母压在半透明平面、棱线、渐变背景上时都清晰可读；描边字在这些叠加场景下会发虚。

```css
#labels .lab {
  position: absolute;
  font-size: var(--lab-size, 22px);
  font-weight: 600;
  color: #BBD7F5;                          /* 亮蓝文字 */
  background: rgba(22,27,34,.88);          /* 深色胶囊底 */
  border: 1px solid rgba(107,168,232,.30);
  border-radius: 7px;
  padding: 1px 8px;
  line-height: 1.3;
  white-space: nowrap;
  will-change: transform;
  box-shadow: 0 2px 8px rgba(0,0,0,.55);
  backdrop-filter: blur(3px);
}
```

**动点标签**（橙色系，区别于静态顶点）：
```css
#labels .lab.p {
  color: #FFB392;
  background: rgba(38,24,17,.92);
  border-color: rgba(255,122,69,.55);
  box-shadow: 0 0 10px rgba(255,122,69,.20), 0 2px 8px rgba(0,0,0,.5);
}
/* 拖拽把柄：触摸端没有悬停态，靠这个暗示"可拖" */
#labels .lab.p::after { content:'⠿'; margin-left:6px; opacity:.6; font-size:.78em; }
```

**四种状态**：

| 状态 | 类名 | 表现 |
|---|---|---|
| 普通 | `.lab` | 深色胶囊 + 亮蓝字 |
| 动点 | `.lab.p` | 深色胶囊 + 亮橙字 + ⠿ 把柄 |
| 被选中 | `.lab.sel` | **橙底深色字（`#20130D`）** + 外发光 |
| 拖动中 | `.lab.p.hot` | 橙底深色字（`#20130D`） + 呼吸光环 |

**动效铁律**：呼吸/脉动动画**只能用 `box-shadow`，绝对不能碰 `transform`**——
`syncLabels` 每帧都在写 `el.style.transform`，CSS 动画一旦也动 transform 就会互相覆盖。

```css
@keyframes labPulse {
  0%,100% { box-shadow:0 0 0 4px rgba(255,122,69,.42), 0 0 16px rgba(255,122,69,.35); }
  50%     { box-shadow:0 0 0 11px rgba(255,122,69,.06), 0 0 20px rgba(255,122,69,.20); }
}
```

---

## 4. 配色原则

1. 背景用**冷黑**（`#0D1117`），不用纯黑——纯黑下卡片没有层次，且 OLED 上是"死黑"
2. **3D 元素颜色与 UI 强调色同一套**，动点橙 = 强调橙
3. 平面颜色**最多 3 个**：蓝（主）/ 橙（动）/ 紫（辅）。再多就分不清了
4. 棱线与实体面同色系，不抢平面的戏
5. 强调色在深底上必须**提亮**，否则发闷

**卡片质感**：`--radius: 12px` + 双层柔和投影（含 `inset` 顶部高光）+ 1px 边框。
不要用生硬的 `box-shadow: 0 2px 4px rgba(0,0,0,.3)`。

---

## 5. 改配色前后的两个强制检查

### ① 图例色点必须与 3D 配色同步
面板里 `<span class="dot" style="background:#...">` 常写字面量颜色。
改了 3D 配色却不改色点，**"颜色说明"就会撒谎**。两处必须一起改。

### ② 对比度核算（WCAG）
三级文字用于 11px 分组标题，字号小更需要达标。
`--ink-3` 曾用过 `#6E7D8D`，只有 **4.10**（对 surface）/ **3.76**（对 surface2），**低于 AA 的 4.5**；改成 `#8B99A8` 后为 **5.95 / 5.44** ✅。

```js
function hex(h){h=h.replace('#','');return [0,2,4].map(i=>parseInt(h.substr(i,2),16));}
function lum(c){const s=c.map(v=>{v/=255;return v<=0.03928?v/12.92:Math.pow((v+0.055)/1.055,2.4);});
  return 0.2126*s[0]+0.7152*s[1]+0.0722*s[2];}
function ratio(a,b){const l1=lum(hex(a)),l2=lum(hex(b));const hi=Math.max(l1,l2),lo=Math.min(l1,l2);
  return (hi+0.05)/(lo+0.05);}

// 逐组检查：
//   正文 ink / 次级 ink-2 / 三级 ink-3  ×  {surface, surface-2, bg}
//   强调色 × 各自的 -lt 容器（brand、accent、green、violet）
// 目标：全部 >= 4.5（AA）；正文最好 >= 7（AAA）
```

**当前基线**（改配色后应不低于此）：

| 组合 | 对比度 | 等级 |
|---|---|---|
| 正文 / surface | 14.64 | AAA |
| 正文 / bg | 16.02 | AAA |
| 次级 / surface | 8.38 | AAA |
| 三级 / surface | 5.95 | AA |
| 三级 / surface2 | 5.44 | AA |
| accent / surface | 6.69 | AA |
| green / green-lt | 7.48 | AAA |
| violet / violet-lt | 6.31 | AA |

---

## 6. 其他需要一并保持的暗色写法

| 元素 | 值 |
|---|---|
| 滚动条 | `#39434F`，hover `#4A5765`，`border: 3px solid var(--surface)` |
| 面板遮罩 | `rgba(0,0,0,.55)` |
| 抽屉投影 | `rgba(0,0,0,.65)` |
| 浮层底（提示条/读数区） | `rgba(22,27,34,.9x)` + `backdrop-filter: blur()` |
| 代码块/行内 code | `background: var(--surface-2)`，文字 `var(--accent)` |
| 难度标签 | `background:#3A1D1D; color:#E88B8B` |
| 临界状态读数区 | `background: rgba(46,26,17,.97)` + 橙外发光 |
| **高亮文字** | 橙底使用 `#20130D` 深色文字；白字对橙底的对比度不足，不要恢复成白字 |
