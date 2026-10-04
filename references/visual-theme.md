# 默认视觉规范

二维与三维默认沿用已认可示例的暗色设计。用户明确要求其他设计时可调整，但需重新核对可读性。结构与尺寸见 [page-spec.md](page-spec.md)；精确可运行 CSS 以示例 `开发资料/源码/style.css` 为参考。

## 色板

| Token | 值 | 用途 |
|---|---|---|
| --bg | #0D1117 | 页面背景 |
| --surface | #161B22 | 面板与卡片 |
| --surface-2 / --surface-3 | #1C232C / #232B36 | 内容块、按钮激活 |
| --line / --line-soft | #2A3441 / #212A34 | 主/弱分隔 |
| --ink / --ink-2 / --ink-3 | #E6EDF3 / #A9B6C4 / #8B99A8 | 正文、次级、说明 |
| --brand / --brand-lt | #6BA8E8 / #17293E | 主结构、蓝容器 |
| --accent / --accent-lt | #FF7A45 / #2E1A11 | 动点/选择/答案、橙容器 |
| --violet / --violet-lt | #A692E8 / #1E1B2E | 辅助构造、紫容器 |
| --green / --green-lt | #8FBF5A / #1A2413 | 可选体积或特定几何提示 |

主视口背景：

```css
#stage {
  background:radial-gradient(ellipse at 50% 42%,
    #1B232E 0%,#131A22 62%,#0B0F14 100%);
}
```

WebGL使用 `alpha:true`，`renderer.setClearColor(0x131A22,0)`，让CSS渐变可见。不能沿用历史不透明clear alpha=1，否则会盖住渐变。

## 3D 对象

- 亮蓝 `0x6BA8E8` 表示主体/主平面，橙 `0xFF7A45` 表示动点/相关线，紫 `0xA692E8` 表示辅助投影，边线默认亮蓝白 `0xB9C9DD`。
- 默认主要辅助平面控制在蓝/橙/紫三类语义。绿适合额外体积对象或条件提示，按需打开；不能仅为凑颜色而改变题目含义。
- 直线用 TubeGeometry 或共享单位tube变换，不依赖 WebGL 原生 linewidth。
- 示例球面/棱台主体面默认 opacity=0.08，辅助面大约0.07–0.19；它们是该模型的选择，可按新题线面密度微调。不要恢复旧模板0.22–0.54的较高不透明度默认，导致多面遮住棱线。
- 透明面使用合适的 `DoubleSide`/`FrontSide` 与 `depthWrite:false`；相交面需要检查绘制顺序和可读性，不用增加不必要的后处理。
- 几何线半径、顶点大小与模型比例相关，不能把外接球绝对半径照抄到很小的棱台。

界面沿用“透明度”滑条文案，但示例的数值直接绑定材质 `opacity`（不透明度），8%对应0.08，不能反转成0.92。新题复用时保持这一视觉和数值关系，说明它控制哪一类面。

## DOM 标签

```css
#labels{pointer-events:none}
#labels .lab{
  position:absolute;top:0;left:0;
  font:600 var(--lab-size,22px)/1.25 Georgia,serif;
  color:#BBD7F5;background:#161B22;
  border:1px solid #39546F;border-radius:8px;
  padding:2px 9px;white-space:nowrap;
  will-change:transform;box-shadow:0 2px 5px #0005;
}
#labels .lab.orange{color:#FFB392;border-color:#76513D}
#labels .lab.violet{color:#C4B6F2;border-color:#564A75}
#labels .lab.sel{
  color:#20130D;background:#FF7A45;border-color:#FFB392;
  box-shadow:0 0 0 3px #FF7A4530;
}
```

边长标签用15px，手机13px；胶囊不依赖模糊滤镜或外部字体。标签的 transform 由投影定位唯一控制，CSS 动画不能覆盖它。默认不需要呼吸动画；拖动反馈可以改光晕/光标/读数状态，而不持续增加渲染帧。

## 卡片与状态

面板、题卡、推导、说明与读数以深色分层及细边线区分，主要圆角10–13px。推导卡间距14px。答案与结果卡可用橙色深底，但普通正文不要全都变成高饱和强调色。

色彩关系必须在画布对象、标签、图例、开关dot和读数之间一致。显隐用状态而不是颜色猜测；关键条件可以同时使用文字与颜色。

选中高亮采用橙底深色文字，白字对橙底对比度不足。细指针才启用hover，触屏用active；键盘 focus-visible 使用清楚描边。

## 可读性检查

正文和说明文字对实际背景默认至少4.5:1，较大文字可按其实际字号/字重使用3:1阈值。颜色、透明背景或选中样式改变后重新测量，不凭屏幕感觉判断。

```js
function luminance(hex){
  const rgb=hex.replace('#','').match(/../g).map(s=>parseInt(s,16)/255)
    .map(v=>v<=.04045?v/12.92:((v+.055)/1.055)**2.4);
  return rgb[0]*.2126+rgb[1]*.7152+rgb[2]*.0722;
}
function contrast(a,b){const x=luminance(a),y=luminance(b);
  return (Math.max(x,y)+.05)/(Math.min(x,y)+.05);}
```

上述函数只适用于不透明颜色；有alpha时需先合成实际背景。图形边界与文字对比度是不同检查，不把“文字通过AA”当作所有细线都清晰。
