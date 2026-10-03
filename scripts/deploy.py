#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
部署本仓库为 AI Agent Skill。

本仓库是【唯一真相源】；skill 目录只作为部署目标，保持干净（无 .git、无 GitHub 门面文件）。

    modeling-display/            ← 本仓库（Git，唯一真相源）
            │ scripts/deploy.py
            ├──→ ~/.workbuddy/skills/modeling-display/
            └──→ ~/.codex/skills/modeling-display/

改内容只改本仓库，然后跑这个脚本。不要直接改 skill 目录里的副本 —— 下次部署会被覆盖。

用法:
    python scripts/deploy.py                       # 部署到全部目标
    python scripts/deploy.py --check               # 只检查差异，不写入（有差异退出码 1）
    python scripts/deploy.py --target workbuddy    # 只部署某一个目标
"""
import io
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)

# 部署哪些（GitHub 门面文件 README/CHANGELOG/LICENSE/.gitignore 不进 skill 目录）
INCLUDE_FILES = ["SKILL.md"]
INCLUDE_DIRS = ["references", "assets", "examples"]

# 这些扩展名跳过（图片对 agent 无直接价值，还占体积）
SKIP_EXT = {".png", ".jpg", ".jpeg", ".gif", ".webp", ".ico"}

# 部署目标
TARGETS = {
    "workbuddy": os.path.join(os.path.expanduser("~"), ".workbuddy", "skills", "modeling-display"),
    "codex":     os.path.join(os.path.expanduser("~"), ".codex", "skills", "modeling-display"),
}

CHECK = "--check" in sys.argv
ONLY = None
if "--target" in sys.argv:
    i = sys.argv.index("--target")
    if i + 1 < len(sys.argv):
        ONLY = sys.argv[i + 1]


def deploy_file(rel, dest_root, changed):
    src = os.path.join(REPO, rel)
    dst = os.path.join(dest_root, rel)
    parent = os.path.dirname(dst)
    if parent and not os.path.isdir(parent):
        if not CHECK:
            os.makedirs(parent, exist_ok=True)

    new = io.open(src, encoding="utf-8").read()
    if os.path.exists(dst):
        if io.open(dst, encoding="utf-8").read() == new:
            return False
    if not CHECK:
        io.open(dst, "w", encoding="utf-8", newline="").write(new)
    changed.append(rel)
    return True


def collect():
    """返回要部署的相对路径列表"""
    rels = []
    for f in INCLUDE_FILES:
        if os.path.exists(os.path.join(REPO, f)):
            rels.append(f)
    for d in INCLUDE_DIRS:
        dpath = os.path.join(REPO, d)
        if not os.path.isdir(dpath):
            continue
        for name in sorted(os.listdir(dpath)):
            if not os.path.isfile(os.path.join(dpath, name)):
                continue
            if os.path.splitext(name)[1].lower() in SKIP_EXT:
                continue
            rels.append(os.path.join(d, name))
    return rels


def main():
    if not os.path.isdir(os.path.join(REPO, ".git")):
        print("✗ 未找到 .git —— 请从仓库的 scripts/ 目录运行本脚本。")
        print("  仓库根: %s" % REPO)
        sys.exit(2)

    rels = collect()
    if not rels:
        print("✗ 没有找到可部署的文件。")
        sys.exit(2)

    targets = TARGETS
    if ONLY:
        if ONLY not in TARGETS:
            print("✗ 未知目标 '%s'，可选: %s" % (ONLY, ", ".join(TARGETS)))
            sys.exit(2)
        targets = {ONLY: TARGETS[ONLY]}

    any_change = False
    for name, root in targets.items():
        changed = []
        for rel in rels:
            deploy_file(rel, root, changed)
        if changed:
            any_change = True
            verb = "需要部署" if CHECK else "已部署"
            print("[%s] %s %d 个文件 → %s" % (name, verb, len(changed), root))
            for c in changed:
                print("    - " + c.replace("\\", "/"))
        else:
            print("[%s] 已是最新 ✓  %s" % (name, root))

    if CHECK and any_change:
        print()
        print("有差异，运行 `python scripts/deploy.py` 同步。")
        sys.exit(1)


if __name__ == "__main__":
    main()
