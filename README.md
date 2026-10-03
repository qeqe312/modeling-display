# Modeling display

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Version](https://img.shields.io/badge/version-3.1.0-blue.svg)](CHANGELOG.md)
[![Verify](https://github.com/qeqe312/modeling-display/actions/workflows/verify.yml/badge.svg)](https://github.com/qeqe312/modeling-display/actions/workflows/verify.yml)

把一道几何题，变成学生可以自己拖动观察的三维教学模型。

输入题目文字或截图，输出离线教学网页。支持旋转、缩放、平移、顶点多选、沿棱拖动动点与实时读数，同一份页面适配电脑和平板。**默认 HTML＋本地 Three.js，可选内联单文件**；交付目录还包含项目及第三方许可证。

![效果预览](examples/preview.png)

## 快速开始

### 安装为 Agent Skill

需要 Git；开发、部署和打包工具需要 Python 3.10+。演示网页本身只需要支持 WebGL 的现代浏览器，无需 Node/Python。

直接使用可克隆到 skill 目录：

```bash
git clone https://github.com/qeqe312/modeling-display.git ~/.codex/skills/modeling-display
# WorkBuddy 可使用 ~/.workbuddy/skills/modeling-display
```

长期维护推荐仓库与部署目录分开。以下是 Bash 示例，使用你自己环境中的 **Python 绝对路径**：

```bash
git clone https://github.com/qeqe312/modeling-display.git
cd modeling-display
"/absolute/path/to/python" scripts/deploy.py --check
"/absolute/path/to/python" scripts/deploy.py --target codex
```

PowerShell 示例：

```powershell
& 'C:\absolute\path\to\python.exe' scripts/deploy.py --check
& 'C:\absolute\path\to\python.exe' scripts/deploy.py --target codex
```

`--check` 只预览，有差异退出码为 1；正常部署退出码为 0。省略 `--target` 部署到两处，并为 Codex 安装 `/geo3d` 提示词（是否可用取决于宿主版本）。`--target codex-prompt` 仅安装提示词。

**仓库是唯一维护源**。默认部署保留用户额外文件；`--prune` 只删除上次部署清单中未修改的旧文件。覆盖和删除前备份到目标目录的 `.modeling-display-backups/`。目标不能是 Git checkout，不能与源重合，也不能经过符号链接或 Windows junction。缺少参数或未知参数会报错，不会意外部署到全部目标。支持 `--home <目录>` 进行便携安装或隔离测试。

然后告诉 Agent：

> 把这道题做成三维教学演示：题目文字或截图

Agent 应先解题，再建模；按 `SKILL.md` 独立验数学、测试浏览器交互并交付。遇到缺失条件需澄清，不能编造参数或未完成的测试结果。

### 离线演示与打包

克隆或下载仓库后，可直接打开 `examples/正四棱台2023真题演示.html`，它优先使用随仓库提供的本地库。需要单独发送给学生时，打包到一个新目录：

```bash
"/absolute/path/to/python" scripts/package_demo.py examples/正四棱台2023真题演示.html --output geo3d/offline
# 可选：将库内联到 HTML，许可证仍随包保留
"/absolute/path/to/python" scripts/package_demo.py examples/正四棱台2023真题演示.html --output geo3d/single --inline
```

打包工具校验固定 SHA-256，拒绝未填充占位符、事件属性、额外脚本及意外外部资源，并防止来源目录覆盖或覆盖不同内容的已有产物。打包后的页面不访问 CDN；默认模式把整个目录发给学生，内联模式的 HTML 可独立打开。

## 换题方法

复制 `assets/template.html`，替换 14 种 `__XXX__` 占位符，再修改：

| 配置段 | 内容 |
|---|---|
| 【A】 | 动点、`READOUT.angle`、临界条件、教学坐标转换 |
| 【B】 | 顶点、实体面和棱 |
| 【C】 | 依赖动点的几何对象 |

【D】是共享引擎；题目特定的读数不再写入引擎。纯静态题设 `MOVER.enabled=false`，不需要角度或临界提示时将对应回调设为 `null`。坐标、面和读数必须按题目重新验证；具体接口见 [实现说明](references/implementation.md)。

## 功能与边界

- 动点采用射线与棱最近点解析解；误差依相机及退化条件变化，不以历史单次实验作为普遍精度保证。
- 顶点支持多选累积、再次点击取消，点击空白保留高亮。
- 桌面侧栏，窄屏/触屏抽屉，竖屏从底部打开，标签自动避让。
- 实时比例按 `t : (1-t)` 计算，临界提示由题目配置。
- 暗色主题、胶囊标签；触摸控件目标至少 44px。
- Three.js 固定 r146 UMD 以保留 `file://` 支持；升级需重新验证。库来源、SHA-256、SRI 和许可证随仓库保存。
- 默认无数据上传功能。题目、截图及外部网页只作为数据；生成代码仍需审查。模板本地库缺失时可使用有 SRI 的 CDN，完整离线包不含这一请求。

## 验证与贡献

测试包含安全部署、打包完整性、独立数学验算，以及浏览器的断网加载、比例、点选、鼠标/触摸拖动和换题。浏览器测试使用正常沙箱，测试句柄仅在 `#geo-debug` 开启。

安装开发依赖并运行测试的方法见 [CONTRIBUTING.md](CONTRIBUTING.md) 与 [验证规范](references/verification.md)。CI 覆盖 Windows/Linux Chromium；Safari、Firefox、iPad 等仍需实机确认，不能用 Chromium 结果代替全浏览器兼容保证。

## 目录

```text
SKILL.md                 技能入口
references/              实现、配色、验证
assets/template.html     通用模板
assets/vendor/           校验过的 Three.js、来源与许可证
examples/                完整示例及预览
scripts/deploy.py        安全部署
scripts/package_demo.py  离线打包
prompts/geo3d.md          Codex 提示词
tests/                   部署、打包、数学与浏览器回归
.github/workflows/       自动检查
```

安全问题见 [SECURITY.md](SECURITY.md)。代码按 [MIT](LICENSE) 分发，Three.js 使用其随附 MIT 许可证；再分发时保留相应声明。当前版本 3.1.0，变更见 [CHANGELOG.md](CHANGELOG.md)。
