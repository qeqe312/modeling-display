# 贡献指南

请先描述问题、复现步骤和预期行为。安全问题按 [SECURITY.md](SECURITY.md) 报告。

仓库是唯一维护源，不直接修改已部署的 skill 副本。改动应保持暗色主题、鼠标/触摸交互及 `file://` 离线打开能力。

开发需要 Python 3.10+、Node.js 18+ 和 Chromium/Chrome。只运行测试需要安装 `requirements-dev.txt`，使用你自己的 Python 绝对路径，不需要安装 GPU 库。浏览器通过 `GEO3D_BROWSER` 环境变量选择，也可使用 Playwright 的 Chromium。

提交前运行：

```bash
"/absolute/path/to/python" -m unittest discover -s tests -p "test_*.py" -v
node tests/math.mjs
"/absolute/path/to/python" tests/browser_check.py
```

浏览器用例包含断网加载、比例与角度、鼠标及触摸拖动、相机锁定、点选、抽屉、安全文本和四面体换题。测试通过不代替 iPad/Safari 等真实设备验证；PR 请列明实际测试环境。

新增数学题应增加独立推导或数值验算，并验证读数名与数值含义一致。新交互应覆盖取消事件及原有行为。第三方库改动需要同步校验值、来源与许可证，禁止未经核验直接替换压缩文件。
