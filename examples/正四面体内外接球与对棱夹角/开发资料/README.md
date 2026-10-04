# 开发资料

本目录保留用户指定的 skill 示例的可读源码、原题、构建入口和验证证据。

```text
源码/
  layout.html   完整题干、四项推导与显示设置
  style.css     共享暗色样式、电脑侧栏与平板抽屉
  model.js      归一化数学坐标、内外球、对棱、切点与图层
  engine.js     相机、Pointer Events、标签、焦点与按需渲染
题目/
  原题.png      用户提供的原始截图
  题意确认.md   完整文字及第（1）项幂次确认
build_demo.py   相对路径重建单文件成品
check_math.mjs  独立底面水平坐标 / 行列式 / 面法向量验算
check_browser.py 断网 file://、鼠标和可信触摸交互检查
check_rotation.py 与前两个示例对照旋转方向和灵敏度
inspect_demo.py 电脑、平板横竖屏、手机截图与测量
使用说明.md    同步复制到成品
正四面体内外接球与对棱夹角.html  可重建的工作 HTML
验证记录/      JSON 报告、验证说明与截图
```

工作 HTML 的 Three.js 路径尚未打包，使用成品中的 HTML 打开演示。`model.js` 与 `engine.js` 按顺序合为同一 script；不要单独加载两文件。公共构建工具及固定依赖位于仓库 scripts/ 与 assets/vendor/，不依赖个人电脑路径。

在仓库根目录，使用当前 Python/Node 环境运行 REFERENCE.md 中的命令。浏览器默认使用 Playwright Chromium；可设置 `GEO3D_BROWSER` 或兼容别名 `BROWSER_EXECUTABLE_PATH`。构建会更新本示例的工作 HTML 和成品；数学及浏览器验证会更新对应报告，截图入口更新截图与 SHA-256。

这是固定顶点题，无动点或运动参数；拖动调整相机，点击固定顶点切换高亮。
