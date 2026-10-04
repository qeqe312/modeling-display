# 贡献指南

请先描述问题、复现步骤和预期行为。安全问题按 [SECURITY.md](SECURITY.md) 报告。

仓库是唯一维护源，不直接修改已部署的 skill 副本。改动应符合 [页面规范](references/page-spec.md)，保持完整解题与显示设置、暗色主题、鼠标/触摸交互及 `file://` 离线打开能力。

开发需要 Python 3.10+、Node.js 18+ 和 Chromium/Chrome，不需要 GPU 库。以下命令使用当前激活环境；宿主要求绝对解释器时替换命令前缀。浏览器通过 `GEO3D_BROWSER` 环境变量选择，否则使用 Playwright Chromium。

## 环境与基础回归

修改公共工具、依赖、安全边界或历史模板后运行：

```bash
python -m pip install -r requirements-dev.txt
python -m playwright install chromium
python -m unittest discover -s tests -p "test_*.py" -v
node tests/math.mjs
python tests/browser_check.py
```

上述浏览器入口覆盖历史模板回归，CI 在 Windows/Linux 执行同一组基础检查。当前五个示例的验收单独运行，入口见 [示例索引](examples/README.md)；已有报告不自动覆盖后来修改的成品。

## 按改动范围验证

| 改动 | 必要检查与资料更新 |
|---|---|
| 纯文档 | 本地链接、路径/命令、二维/三维适用范围、版本和索引一致性；文档所述行为需有对应实现 |
| 组装、打包、部署、第三方依赖或历史模板 | 基础回归；构建并检查受影响示例；依赖变更同步来源、校验与许可证 |
| 某题数学、图形或动点约束 | 重建该例，独立数学与最终成品浏览器检查；更新相关报告与状态截图 |
| 共用布局、主题、手势、标签或缓存 | 重建并验收所有受影响示例，覆盖桌面、平板横竖屏和窄屏，更新对应截图 |
| 新增长期示例 | 完整源码、原题、REFERENCE、构建、独立数学、可信输入、截图、环境与未测项；更新示例索引 |

当前示例按 `build_demo.py → check_math.mjs → check_browser.py → inspect_demo.py` 的顺序维护；只改部分内容时更新受影响证据。二维例再运行 `check_archive.py`，验证重建一致性、报告哈希、截图及参考入口。

新增长期 example 时提供成品、可读源码、相对路径构建入口、REFERENCE 导读、截图及可重跑验证报告；标准见 [参照指南](references/example-guide.md)。普通生成题目不作为仓库示例归档。

纯二维题参考 [二维实现说明](references/plane-geometry.md) 与椭圆二维例。该例使用原生 Canvas 外壳，依次运行其 `build_demo.py`、`check_math.mjs`、`check_browser.py`、`inspect_demo.py`；验证平面等单位变换、实虚线边界、指针约束与 cx/cy/scale 锁定，不运行三维相机检查。

三维例使用校验过的 Three.js 与仓库公共工具，保留球坐标相机；沿棱、圆弧和旋转参数的反解分别验证。播放中的动画与静止时按需渲染分开验收。各例命令、默认状态和报告位置以自身 `REFERENCE.md` 与开发资料说明为准。

新增数学题应增加独立推导或数值验算，并验证读数名与数值含义一致。新交互应覆盖取消事件及原有行为。第三方库改动需要同步校验值、来源与许可证，禁止未经核验直接替换压缩文件。

## 文档、交付与提交

共用要求按 [AGENTS.md](AGENTS.md) 的文档职责维护；规则变更同步 `SKILL.md`、提示词与相关规范。题目特有选择留在该例导读，历史版本的 CHANGELOG 保留当时行为。

普通题目只交付单文件、说明和许可证；长期示例使用 `examples/<题目名称>/{成品,开发资料}/`，保留已有双文件版。默认不生成 ZIP；发布文件不带日志、PID、缓存、临时目录或维护者个人环境路径。

提交前检查 `git diff --check`、改动清单与文档引用。报告注明最终成品版本/哈希、实际浏览器、输入证据、容差和未测平台；测试通过不代替 iPad/Safari 等实体设备验证。提交说明描述最终行为及实际运行的检查，按用户授权推送；安装 skill 与发布网站另行执行。

文本采用 UTF-8，换行遵循 `.gitattributes` 的 LF 约定，生成 HTML 时也固定 LF。SHA-256 针对最终保存的字节；需保证工作成品、Git 收录文件、重建结果及报告一致，不能让 Windows 默认换行转换使克隆后的验证失配。

CI 的 Linux 基线为 Ubuntu 22.04，使用其默认支持的 Chromium user namespace 沙箱。Ubuntu 23.10+ 的 AppArmor 配置可能限制独立下载的浏览器；本项目不自动关闭沙箱或修改宿主内核设置。
