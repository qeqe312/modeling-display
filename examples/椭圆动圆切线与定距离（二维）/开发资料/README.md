# 开发资料

本目录保留二维示例的可读源码、原题、构建入口、独立数学与浏览器检查、截图和报告。构建不依赖旧的 geo3d 目录、临时文件或其他题目的源码。

```text
源码/                 layout.html、style.css、app.js
题目/                 原题.png、题意确认.md
build_demo.py          从本例源码生成离线单文件及说明/许可证
check_math.mjs         独立重写数学，输出 math-report.json
browser_support.py    离线浏览器、可信输入及 Canvas 绘制观察共用工具
check_browser.py      最终成品的数学比对、实虚线、手势、设置与缓存检查
inspect_demo.py       四种视口的模型/讲解/设置/特殊半径截图
check_archive.py      重建一致性、报告哈希、截图、导读链接与打包收集检查
preview_server.py     可选本机预览服务，直接服务成品
验证记录/             报告、验证说明与截图
使用说明.md           成品说明的维护源
```

从仓库根目录运行，以下 `python` 指当前项目解释器；宿主要求绝对路径时使用自己的解释器路径。浏览器保持沙箱，`GEO3D_BROWSER` 可指定已有 Chrome/Chromium；省略时使用 Playwright 的 Chromium。

```bash
python "examples/椭圆动圆切线与定距离（二维）/开发资料/build_demo.py"
node "examples/椭圆动圆切线与定距离（二维）/开发资料/check_math.mjs"
python "examples/椭圆动圆切线与定距离（二维）/开发资料/check_browser.py"
python "examples/椭圆动圆切线与定距离（二维）/开发资料/inspect_demo.py"
python "examples/椭圆动圆切线与定距离（二维）/开发资料/check_archive.py"
# 可选：在本机打开 http://127.0.0.1:8766/
python "examples/椭圆动圆切线与定距离（二维）/开发资料/preview_server.py" --port 8766
```

开发环境需 Python 3.10+、Node 18+、Playwright 与 Chrome/Chromium，安装见仓库 `CONTRIBUTING.md`。网页本身不需要这些开发工具，只需现代 Canvas 浏览器。

构建支持 `--output <另一个成品目录>`，不会写回源码。它采用自带 Canvas 单文件外壳，不经过 Three.js 打包器；读取本例三份源码，检查内联块与外部资源边界，保留许可证。HTML 固定使用 UTF-8 与 LF，与仓库换行规则一致，避免不同系统重建后报告哈希变化。改编普通新题时只保留最终 HTML、说明和许可证；不要自动把新题也作为长期 example。

浏览器验证通过不代表实体 iPad、Safari、Firefox 已实测。变更后先重建，再检查最终成品；报告中的 SHA-256 用来确认截图和交互检查对应同一份 HTML。

`check_archive.py` 在全部报告生成后执行，会在系统临时目录独立重建并逐字节比对三份成品，再检查截图与仓库参考入口。它还只读调用仓库的部署收集器，确认二维资源能被打包；不会安装或部署 skill。构建器本身不依赖该检查或旧题目录。
