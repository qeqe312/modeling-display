# 开发资料

本目录维护正四棱台单动点示例。先读[参照导读](../REFERENCE.md)，再按下表定位源码；构建直接读取本例保留版本，不依赖其他题目或已淘汰版本。

| 文件 | 职责 |
|---|---|
| `源码/layout.html` | 完整原题、推导、答案与显示设置 |
| `源码/style.css` | 暗色布局、桌面侧栏、触屏抽屉与运动组件 |
| `源码/model.js` | 教学坐标、模型、setT、轨迹反解、读数、标签与缓存 |
| `源码/engine.js` | 球坐标相机、指针归属、动点锁定、抽屉与按需渲染 |
| `源码/app.js`、工作 HTML | 构建生成的合并结果；修改两份原始 JS 后重建 |
| `build_demo.py` | 按 model.js → engine.js 合并，用仓库工具生成已有单双文件成品 |
| `check_math.mjs` | 独立验算题设、体积比、垂直条件与线面角 |
| `check_browser.py` | 最终离线成品、鼠标/可信触摸、约束拖点与状态同步 |
| `inspect_demo.py` | 四种视口的模型、完整解题、设置及动点特殊位置截图 |
| `diagnose_drag.py` | 补充拖动诊断；不代替正式交互验收 |
| `验证记录/` | 报告、截图及实际验证范围 |
| `使用说明.md` | 成品说明的维护源 |
| `preview_server.py` | 可选本机预览；运行文件在忽略的 `.运行时/` |

从仓库根目录、当前 Python/Node 环境执行；开发环境与浏览器设置见 [CONTRIBUTING.md](../../../CONTRIBUTING.md)。使用者如需绝对解释器路径，自行替换命令前缀。

```bash
python "examples/正四棱台2023真题演示/开发资料/build_demo.py"
node "examples/正四棱台2023真题演示/开发资料/check_math.mjs"
python "examples/正四棱台2023真题演示/开发资料/check_browser.py"
python "examples/正四棱台2023真题演示/开发资料/inspect_demo.py"
```

浏览器默认使用 Playwright Chromium；支持 `GEO3D_BROWSER` 或兼容别名 `BROWSER_EXECUTABLE_PATH`，前者优先。构建会更新自身源码合并结果、工作 HTML、成品、说明与许可证，保留双文件版，默认不生成 ZIP。

数学和交互检查针对最终成品；截图与浏览器报告记录 HTML 哈希。可信触摸与平板视口模拟不代表实体 iPad/Safari 实测，未测项见验证说明。
