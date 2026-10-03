# 验算与自测规范

每个新题交付前需要独立数学验算，以及真实浏览器输入测试。现有示例通过回归不能证明新题正确；缺少工具时报告未验证项目，不声称通过。

## 仓库回归

需要 Python 3.10+、Node.js 18+ 和 Chrome/Chromium。使用当前环境的 Python 绝对路径安装 `requirements-dev.txt`。可设置 `GEO3D_BROWSER` 为浏览器可执行文件绝对路径，否则使用 Playwright 安装的 Chromium：

```bash
"/absolute/path/to/python" -m pip install -r requirements-dev.txt
"/absolute/path/to/python" -m playwright install chromium
"/absolute/path/to/python" -m unittest discover -s tests -p "test_*.py" -v
node tests/math.mjs
"/absolute/path/to/python" tests/browser_check.py
```

Linux CI 安装浏览器时加 `--with-deps`。浏览器保持沙箱；不要默认添加 `--no-sandbox`，在不支持沙箱的环境中应报告限制或换到合适环境。

## 数学验算

`tests/math.mjs` 独立构建示例坐标与向量，不加载页面实现。检查：侧棱角 60°、体积比 1:6、垂直条件 t=1/2、线面角正弦、t=0/0.25/0.5/0.75/1 的比例，以及射线反算在多视角/视口的往返、夹取及退化条件。相机 FOV **40°** 与页面一致；若页面修改相机，测试配置必须同步。

新题分别写独立推导与数值计算。定义清楚每个量，特别是体积的“整体”与“余下部分”；互补部分要验证和等于整体。测试失败时同时检查页面、期望值和验算实现，不预设页面永远正确。

## 浏览器交互与安全回归

`tests/browser_check.py` 通过 Playwright 鼠标输入和 Chromium CDP 触摸输入驱动浏览器；这些事件由浏览器生成。`dispatchEvent(new PointerEvent(...))` 可作为单元测试补充，但合成事件不能替代真实输入链路。

核心检查包括：

1. 断网打开打包示例及内联页面，无控制台异常。
2. 端点及 1/4、中点、3/4 的比例、角度与独立计算一致。
3. 点动点小球，选中；再次点击，取消。
4. 点标签与从标签拖动，t 改变且滑块同步。
5. 动点拖动时相机 azim/elev/dist 不变。
6. 普通顶点、多选累积及点空白保留高亮。
7. 空白拖动仍可旋转，滚轮可缩放，右键可平移。
8. 触屏动点拖动、双指缩放、pointercancel 不误触点选。
9. 平板竖屏抽屉、字号与显示开关。
10. 恶意标签按纯文本显示，不创建事件元素。
11. 模板换为四面体或静态题，保持 D 引擎不变可启动。
12. 两个库来源均失败时显示可读错误；正常模式没有测试句柄。

用 `file://.../页面.html#geo-debug` 开启 `window.__S` 与 `window.__GEO`。这些是可变测试接口，不是只读对象；常规打开不暴露。测试直接加载当前源文件并在临时目录打包，避免旧测试副本污染。

## 视觉与设备确认

交付前检查桌面 1600×1000、窄屏 780×1000、平板竖屏 820×1180 的模型完整性、标签重叠、文本对比度、读数和抽屉。自动化浏览器验证不能代替真实 iPad/Safari 或 Android 的硬件、系统文件打开方式和手势验证。
