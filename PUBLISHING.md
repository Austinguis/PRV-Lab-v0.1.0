# PRV-Lab 发布与维护指南

本文件供维护者使用，可以与代码一起上传到 GitHub。项目使用说明见 [README.md](README.md) 和 [README_zh.md](README_zh.md)。

目标仓库：<https://github.com/Austinguis/PRV-Lab-v0.1.0>

Python 包名为 `prv-lab`，初始版本号为 `0.1.0`。仓库名称可以包含版本号，不要求 Python 包名与仓库名完全一致。

## 1. 核对发布信息

- `pyproject.toml` 的 Homepage 应为 `https://github.com/Austinguis/PRV-Lab-v0.1.0`，Issues 应为该地址加 `/issues`。
- `CITATION.cff` 的 `repository-code` 应为同一仓库地址。
- 核对 `pyproject.toml`、`src/prv_lab/__init__.py` 和 `CITATION.cff` 中的版本是否一致。
- 核对 `CITATION.cff` 的作者与发布日期，仅填写真实、准确的信息。
- 保留 `LICENSE` 中已有的版权声明；新增贡献者信息应与实际贡献和授权一致。
- README 应区分已经实现的功能、需要可选依赖的功能和路线图计划。

## 2. 本地验证

在包含 `pyproject.toml` 的项目根目录中打开 PowerShell，执行：

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install -e ".[dev]"
.\.venv\Scripts\python.exe -m pytest
.\.venv\Scripts\python.exe -m ruff check .
.\.venv\Scripts\python.exe -m build
```

这些命令无需激活脚本。macOS / Linux 可使用 `.venv/bin/python` 替换上述 Python 路径。

检查未通过时先修复再发布。若说明中包含真实 PRV 后端的验证结果，应额外安装 `.[prv]` 并实际运行对应实验，保留参数、依赖版本和输出。默认适配器测试使用模拟后端，不能替代真实后端实验。

## 3. 上传代码

### 方法 A：通过 GitHub 网页上传

1. 登录 GitHub，打开目标仓库，进入代码页面。
2. 空仓库选择上传已有文件的入口；已有文件的仓库选择 **Add file → Upload files**。
3. 上传项目根目录内的文件和目录，使 `README.md`、`pyproject.toml`、`src/`、`tests/` 等直接位于仓库根目录。
4. 一并上传 `.github/`、`.gitignore`、`.editorconfig`、许可证、引用文件和其他项目文档。
5. 排除 `.venv/`、`venv/`、`build/`、`dist/`、`*.egg-info/`、缓存、`results/` 及本地私有文件。网页上传不会自动遵守 `.gitignore`。
6. 核对待提交文件、路径和已有文件的改动，填写提交说明，然后提交。

提交说明示例：`Prepare PRV-Lab v0.1.0 for public release`。

### 方法 B：通过 Git 维护，适合后续更新

在一个尚未包含同名目录的位置执行：

```bash
git clone https://github.com/Austinguis/PRV-Lab-v0.1.0.git
cd PRV-Lab-v0.1.0
```

将准备好的项目内容复制到克隆目录，保留克隆产生的 `.git` 目录。若仓库已有其他内容，先逐项对照合并。然后执行：

```bash
git status
git add .
git diff --cached --stat
git diff --cached
```

检查暂存内容正确后，再执行：

```bash
git commit -m "Prepare PRV-Lab v0.1.0 for public release"
git push -u origin HEAD
```

Git 的认证与 Edge 网页登录属于不同流程；按 Git 的提示完成认证。若远端出现新提交，先拉取并合并后再推送，不使用强制推送覆盖远端历史。

## 4. 检查 GitHub Actions

- 打开仓库 **Actions** 页面，检查对应提交的 CI 结果。
- 当前 CI 配置检查 Python 3.10、3.11 和 3.12 的测试与代码规范。
- 上传工作流文件后，以实际运行结果判断是否通过，不将“配置了 CI”描述为“CI 已通过”。

## 5. 创建正式版本

代码和文档验证完成后：

1. 更新 `CHANGELOG.md`，记录实际变更。
2. 确认包版本、引用版本和发布日期准确。
3. 在 GitHub 创建对应版本的 Release，例如 `v0.1.0`，并将标签指向已验证的提交。
4. 发布说明写明已实现功能、安装方式、验证范围及已知限制。

仓库中的 `release.yml` 在推送 `v*` 标签或手动触发时构建 wheel 和源码分发包，并将它们作为 Actions artifacts 保存。该工作流不会自动创建 GitHub Release，也不会自动发布到 PyPI。需要 Release 附件时，可下载并核对构建产物后手动附加。

## 6. 后续维护

- 如实填写仓库简介，使用与项目相关的主题标签。
- 在文档中保留机制假设、误差界和实验协议。
- 及时处理可复现的问题，保持代码、测试、文档和路线图同步。
- 只公布实际得到的测试、基准结果和使用情况。
