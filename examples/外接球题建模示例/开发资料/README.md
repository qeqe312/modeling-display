# 完整解题版开发资料

本目录维护外接球固定模型示例；其他题目的入口见[示例索引](https://github.com/qeqe312/modeling-display/blob/main/examples/README.md)（[本地](../../README.md)）。

首次参照或改编请先阅读[本题 REFERENCE.md](https://github.com/qeqe312/modeling-display/blob/main/examples/%E5%A4%96%E6%8E%A5%E7%90%83%E9%A2%98%E5%BB%BA%E6%A8%A1%E7%A4%BA%E4%BE%8B/REFERENCE.md)（[本地](../REFERENCE.md)），再按下方文件说明定位布局、数学模型、交互和验证脚本。

## 文件说明

- `源码/app.js`：数学模型、显示设置、触控交互、按需渲染。
- `源码/style.css`：页面排版、平板抽屉、标签及公式卡片样式。
- `源码/layout.html`：原题、完整推导、显示设置界面。
- `源码/外接球题建模示例.html`：构建脚本组装的页面源文件。
- `build_demo.py`：直接使用上述完整解题版源码，输出到成品文件夹。
- `check_browser.py`：最终成品的完整解题、显示设置、离线与可信输入检查，数量随覆盖范围变化。
- `check_math.mjs`：独立数学验算及文字对比度检查。
- `inspect_demo.py`：桌面、平板与手机截图检查。
- `验证记录/`：测试报告与截图。
- `preview_server.py` 与 `.运行时/`：本机预览服务及其运行文件。

构建过程使用本仓库的模板、离线打包工具和已校验的 Three.js；不再依赖已删除的分步展示版本。

## 重建与验证

先激活自己的 Python 环境并确保 `node` 可用。以下命令从仓库根目录运行，`python` 和 `node` 均使用当前环境，无需固定个人安装路径。

浏览器检查与截图需要先安装 Playwright 和它的 Chromium：

```powershell
python -m pip install playwright
python -m playwright install chromium
```

脚本默认使用 Playwright Chromium；也可通过 `GEO3D_BROWSER` 指定自己的 Chromium 系浏览器可执行文件。`BROWSER_EXECUTABLE_PATH` 为兼容别名，两个变量同时设置时以 `GEO3D_BROWSER` 为准。

修改源码后运行：

```powershell
python "examples/外接球题建模示例/开发资料/build_demo.py"
python "examples/外接球题建模示例/开发资料/check_browser.py"
node "examples/外接球题建模示例/开发资料/check_math.mjs"
```

重建会更新成品中的 HTML、使用说明、许可证及双文件版，默认不生成 ZIP 压缩包。临时打包目录在构建结束后自动清理。

截图复核按需运行：

```powershell
python "examples/外接球题建模示例/开发资料/inspect_demo.py"
```

`验证记录/` 保留已完成的历史检查。浏览器输入来自 Chrome 鼠标与可信 CDP 触摸输入，平板尺寸为视口模拟；不代表实体 iPad、Safari 或安卓硬件实测。
