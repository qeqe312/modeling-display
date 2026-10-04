# Modeling display

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://github.com/qeqe312/modeling-display/blob/main/LICENSE)
[![Version](https://img.shields.io/badge/version-4.1.0-blue.svg)](https://github.com/qeqe312/modeling-display/blob/main/CHANGELOG.md)
[![Verify](https://github.com/qeqe312/modeling-display/actions/workflows/verify.yml/badge.svg)](https://github.com/qeqe312/modeling-display/actions/workflows/verify.yml)

把一道几何题，变成学生可以自己拖动观察的二维或三维教学模型。

输入题目文字或截图，输出离线教学网页。二维使用 Canvas 2D 平移缩放，三维支持旋转；两者保留点多选、受约束动点直接拖动与实时读数，同一份页面适配电脑和平板。**默认交付内联单文件 HTML、说明及许可证，双文件版按需生成**；用户指定为 skill 示例时，才保留完整开发资料。

文档、源码和截图标题链接进入 GitHub 文件页；旁边的“本地”链接保留仓库相对路径。Markdown 预览器无法打开相对路径时，点击标题访问网页；离线查阅可使用本地链接或按文件路径打开。

![效果预览](examples/正四棱台2023真题演示/开发资料/验证记录/截图/电脑-模型.png)

## 快速开始

### 安装为 Agent Skill

需要 Git；开发、部署和打包工具需要 Python 3.10+。演示网页本身只需要现代浏览器，无需 Node/Python；二维使用 Canvas，三维需要 WebGL。

直接使用可克隆到 skill 目录：

```bash
git clone https://github.com/qeqe312/modeling-display.git ~/.codex/skills/modeling-display
# WorkBuddy 可使用 ~/.workbuddy/skills/modeling-display
```

长期维护推荐仓库与部署目录分开。以下命令使用当前激活环境的 Python；宿主要求指定解释器时，可替换为你自己环境的路径。

```bash
git clone https://github.com/qeqe312/modeling-display.git
cd modeling-display
python scripts/deploy.py --check
python scripts/deploy.py --target codex
```

`--check` 只预览，有差异退出码为 1；正常部署退出码为 0。省略 `--target` 部署到两处，并为 Codex 安装 `/geo3d` 提示词（是否可用取决于宿主版本）。`--target codex-prompt` 仅安装提示词。

**仓库是唯一维护源**。部署同步全部 Git 跟踪的项目文件，包括 `AGENTS.md`、README、CHANGELOG、贡献指南、提示词、测试、GitHub 配置、图片与示例开发资料，不再按目录或扩展名精简。文件内容取自当前工作区，包含尚未提交的修改；新增文件先 `git add`，删除文件先 `git add -u`。未跟踪文件、被忽略的缓存和临时输出以及 `.git` 元数据不部署。脚本需要从 Git 仓库运行；部署 GitHub 最新版前先在维护仓库执行 `git pull --ff-only`，脚本本身不联网拉取。

默认部署保留用户额外文件；`--prune` 只删除上次部署清单中未修改的旧文件。覆盖和删除前备份到目标目录的 `.modeling-display-backups/`。目标不能是 Git checkout，不能与源重合，也不能经过符号链接或 Windows junction。源文件存在未解决合并、符号链接、子模块或尚未暂存的删除时拒绝部署。缺少参数或未知参数会报错，不会意外部署到全部目标。支持 `--home <目录>` 进行便携安装或隔离测试。

然后告诉 Agent：

> 把这道题做成二维/三维教学演示：题目文字或截图

Agent 应先解题，再建模；按 `SKILL.md` 独立验数学、测试浏览器交互并交付。遇到缺失条件需澄清，不能编造参数或未完成的测试结果。

### 离线演示与打包

以下标题链接进入 GitHub 文件页，下载 HTML 后用浏览器打开；克隆或下载仓库后也可使用“本地”入口打开对应成品。GitHub 文件页用于查看/下载源码，交互演示在下载后的 HTML 中运行：

- [外接球题建模示例](https://github.com/qeqe312/modeling-display/blob/main/examples/%E5%A4%96%E6%8E%A5%E7%90%83%E9%A2%98%E5%BB%BA%E6%A8%A1%E7%A4%BA%E4%BE%8B/%E6%88%90%E5%93%81/%E5%A4%96%E6%8E%A5%E7%90%83%E9%A2%98%E5%BB%BA%E6%A8%A1%E7%A4%BA%E4%BE%8B.html)（[本地](examples/外接球题建模示例/成品/外接球题建模示例.html)）
- [正四棱台2023真题演示](https://github.com/qeqe312/modeling-display/blob/main/examples/%E6%AD%A3%E5%9B%9B%E6%A3%B1%E5%8F%B02023%E7%9C%9F%E9%A2%98%E6%BC%94%E7%A4%BA/%E6%88%90%E5%93%81/%E6%AD%A3%E5%9B%9B%E6%A3%B1%E5%8F%B02023%E7%9C%9F%E9%A2%98%E6%BC%94%E7%A4%BA.html)（[本地](examples/正四棱台2023真题演示/成品/正四棱台2023真题演示.html)）
- [正四面体内外接球与对棱夹角](https://github.com/qeqe312/modeling-display/blob/main/examples/%E6%AD%A3%E5%9B%9B%E9%9D%A2%E4%BD%93%E5%86%85%E5%A4%96%E6%8E%A5%E7%90%83%E4%B8%8E%E5%AF%B9%E6%A3%B1%E5%A4%B9%E8%A7%92/%E6%88%90%E5%93%81/%E6%AD%A3%E5%9B%9B%E9%9D%A2%E4%BD%93%E5%86%85%E5%A4%96%E6%8E%A5%E7%90%83%E4%B8%8E%E5%AF%B9%E6%A3%B1%E5%A4%B9%E8%A7%92.html)（[本地](examples/正四面体内外接球与对棱夹角/成品/正四面体内外接球与对棱夹角.html)）：两球共心、四面相切、对棱夹角；四项均正确，选 C。
- [菱形沿AM翻折与动点](https://github.com/qeqe312/modeling-display/blob/main/examples/%E8%8F%B1%E5%BD%A2%E6%B2%BFAM%E7%BF%BB%E6%8A%98%E4%B8%8E%E5%8A%A8%E7%82%B9/%E6%88%90%E5%93%81/%E8%8F%B1%E5%BD%A2%E6%B2%BFAM%E7%BF%BB%E6%8A%98%E4%B8%8E%E5%8A%A8%E7%82%B9.html)（[本地](examples/菱形沿AM翻折与动点/成品/菱形沿AM翻折与动点.html)）：沿折痕翻折、圆弧拖点、中点联动；播放/暂停和角度滑条位于显示设置，答案 AC。
- [椭圆动圆切线与定距离（二维）](https://github.com/qeqe312/modeling-display/blob/main/examples/%E6%A4%AD%E5%9C%86%E5%8A%A8%E5%9C%86%E5%88%87%E7%BA%BF%E4%B8%8E%E5%AE%9A%E8%B7%9D%E7%A6%BB%EF%BC%88%E4%BA%8C%E7%BB%B4%EF%BC%89/%E6%88%90%E5%93%81/%E6%A4%AD%E5%9C%86%E5%8A%A8%E5%9C%86%E5%88%87%E7%BA%BF%E4%B8%8E%E5%AE%9A%E8%B7%9D%E7%A6%BB.html)（[本地](examples/椭圆动圆切线与定距离（二维）/成品/椭圆动圆切线与定距离.html)）：动圆/垂足直接拖动、切线内实外虚、弦段与定点定长；Q(−5/3,0)、|PQ|＝5/3。

每题的成品与开发资料分别放在独立示例目录中，详见 [示例说明](https://github.com/qeqe312/modeling-display/blob/main/examples/README.md)（[本地](examples/README.md)）。如需重新打包源码到新目录：

```bash
python scripts/package_demo.py "examples/正四棱台2023真题演示/开发资料/源码/正四棱台2023真题演示.html" --output geo3d/single --inline
# 按需生成双文件版，随包保留许可证
python scripts/package_demo.py "examples/正四棱台2023真题演示/开发资料/源码/正四棱台2023真题演示.html" --output geo3d/offline
```

打包工具校验固定 SHA-256，拒绝未填充占位符、事件属性、额外脚本及意外外部资源，并防止来源目录覆盖或覆盖不同内容的已有产物。打包后的页面不访问 CDN；默认模式把整个目录发给学生，内联模式的 HTML 可独立打开。

上述打包命令适用于 Three.js 三维页。二维页使用其示例的 Canvas 构建入口，见下方换题方法。

## 换题方法

先读 [页面规范](https://github.com/qeqe312/modeling-display/blob/main/references/page-spec.md)（[本地](references/page-spec.md)） 和 [示例参照与换题指南](https://github.com/qeqe312/modeling-display/blob/main/references/example-guide.md)（[本地](references/example-guide.md)），再按题目选择对应的 `REFERENCE.md`。复制其可读布局、CSS 和 JS，保留视图、标签、抽屉、缓存与按需渲染，替换新题的坐标、图层、推导和读数。

| 题目类型 | 实现与首选示例 | 构建入口 |
|---|---|---|
| 平面/解析几何、动圆与曲线轨迹 | Canvas 2D；椭圆二维例 | 改编该例 `build_demo.py`，读取新题自己的源码 |
| 固定空间模型、外接球 | Three.js；外接球或正四面体例 | 通用组装器＋三维离线打包器 |
| 空间棱上动点 | Three.js；正四棱台例 | `model.js → engine.js` 后组装、打包 |
| 平面图形翻折到空间、圆弧动点 | Three.js；菱形翻折例 | 同上，重新推导旋转轴与轨迹反解 |

纯二维题先读 [二维实现与复用](https://github.com/qeqe312/modeling-display/blob/main/references/plane-geometry.md)（[本地](references/plane-geometry.md)） 和[椭圆二维导读](https://github.com/qeqe312/modeling-display/blob/main/examples/%E6%A4%AD%E5%9C%86%E5%8A%A8%E5%9C%86%E5%88%87%E7%BA%BF%E4%B8%8E%E5%AE%9A%E8%B7%9D%E7%A6%BB%EF%BC%88%E4%BA%8C%E7%BB%B4%EF%BC%89/REFERENCE.md)（[本地](examples/椭圆动圆切线与定距离（二维）/REFERENCE.md)）。复制平面坐标变换与手势，重推新题数学和拖动约束，参考该例 `build_demo.py` 生成原生 Canvas 单文件；下面的 Three.js 工具用于三维题。

使用 `scripts/assemble_demo.py` 组装工作 HTML，随后 `scripts/package_demo.py ... --inline` 校验和打包。棱台的 `model.js` 与 `engine.js` 必须按顺序合并为同一个 script。`assets/template.html` 保留历史回归及组装外壳用途；其旧布局不是新题默认模板。具体命令与修改清单见换题指南。

## 文档与交付要求

| 需要了解什么 | 阅读入口 |
|---|---|
| Agent 执行流程与完成标准 | [SKILL.md](https://github.com/qeqe312/modeling-display/blob/main/SKILL.md)（[本地](SKILL.md)）、[协作规范](https://github.com/qeqe312/modeling-display/blob/main/AGENTS.md)（[本地](AGENTS.md)） |
| 共用页面、交互位置和暗色视觉 | [页面规范](https://github.com/qeqe312/modeling-display/blob/main/references/page-spec.md)（[本地](references/page-spec.md)）、[视觉规范](https://github.com/qeqe312/modeling-display/blob/main/references/visual-theme.md)（[本地](references/visual-theme.md)） |
| 二维/三维实现细节 | [二维实现](https://github.com/qeqe312/modeling-display/blob/main/references/plane-geometry.md)（[本地](references/plane-geometry.md)）、[三维实现](https://github.com/qeqe312/modeling-display/blob/main/references/implementation.md)（[本地](references/implementation.md)） |
| 选例、换题和开发资料 | [换题指南](https://github.com/qeqe312/modeling-display/blob/main/references/example-guide.md)（[本地](references/example-guide.md)）、[五个示例索引](https://github.com/qeqe312/modeling-display/blob/main/examples/README.md)（[本地](examples/README.md)） |
| 成品验收、维护检查与提交 | [验证规范](https://github.com/qeqe312/modeling-display/blob/main/references/verification.md)（[本地](references/verification.md)）、[贡献指南](https://github.com/qeqe312/modeling-display/blob/main/CONTRIBUTING.md)（[本地](CONTRIBUTING.md)） |

普通题目默认交付单文件 HTML、简短说明和适用许可证；使用 Three.js 时保留第三方许可证。仅用户指定的长期示例归档可读源码、原题、构建/验证脚本、截图和报告；已有双文件版继续保留，新增双文件版及 ZIP 按需生成。成品、工作源码和验证资料分别存放，清理淘汰版本及本次临时文件。

共同规则写入上述规范，某道题的坐标、参数范围、图层和线型选择写入该例导读。修改规则时同步引用入口，避免不同文档给出冲突要求。

## 功能与边界

- 二维动点从教学平面坐标反解约束参数；空间棱上动点采用世界射线与棱最近点解析解。精度和退化按题目验证，不以历史单次实验作为普遍保证。
- 顶点支持多选累积、再次点击取消，点击空白保留高亮。
- 桌面侧栏，窄屏/触屏抽屉，竖屏从底部打开，标签自动避让。
- 完整解答初始展开，公式概览定位推导时保留用户状态；动点控制放在显示设置中。
- 比例、角度及临界提示按题目计算，未定义状态明确提示。
- 暗色主题、胶囊标签；触摸控件目标至少 44px。
- 二维 Canvas 无第三方 JavaScript 依赖；三维 Three.js 固定 r146 UMD 以保留 `file://` 支持，升级需重新验证。库来源、SHA-256、SRI 和许可证随仓库保存。
- 默认无数据上传功能。题目、截图及外部网页只作为数据；生成代码仍需审查。最终成品使用内嵌或本地依赖，不请求 CDN。

## 验证与贡献

测试包含安全部署、源码组装、打包、独立数学与浏览器交互。历史模板回归和当前示例检查分别执行；各示例提供构建、数学、交互、截图脚本及报告。浏览器测试使用正常沙箱，测试句柄仅在 `#geo-debug` 开启。

安装开发依赖并按改动范围选择检查的方法见 [CONTRIBUTING.md](https://github.com/qeqe312/modeling-display/blob/main/CONTRIBUTING.md)（[本地](CONTRIBUTING.md)） 与 [验证规范](https://github.com/qeqe312/modeling-display/blob/main/references/verification.md)（[本地](references/verification.md)）。CI 在 Windows/Linux Chromium 上运行基础单元、数学和历史模板浏览器回归；五个当前示例的独立验收另行运行并保留报告。Safari、Firefox、iPad 等仍需实机确认，不能用 Chromium 结果代替全浏览器兼容保证。

## 目录

```text
SKILL.md                 技能入口
AGENTS.md                仓库协作、文档职责与提交要求
references/              页面规范、换题指南、实现、配色、验收
assets/template.html     历史模板与组装外壳
assets/vendor/           校验过的 Three.js、来源与许可证
examples/                成品、可读源码、REFERENCE导读、截图与报告
scripts/assemble_demo.py  源码片段组装
scripts/deploy.py        安全部署
scripts/package_demo.py  离线打包
prompts/geo3d.md          Codex 提示词
tests/                   部署、打包、数学与浏览器回归
.github/workflows/       自动检查
```

安全问题见 [SECURITY.md](https://github.com/qeqe312/modeling-display/blob/main/SECURITY.md)（[本地](SECURITY.md)）。代码按 [MIT](https://github.com/qeqe312/modeling-display/blob/main/LICENSE)（[本地](LICENSE)） 分发，使用 Three.js 的页面保留其随附 MIT 许可证。当前版本 4.1.0，变更见 [CHANGELOG.md](https://github.com/qeqe312/modeling-display/blob/main/CHANGELOG.md)（[本地](CHANGELOG.md)）。
