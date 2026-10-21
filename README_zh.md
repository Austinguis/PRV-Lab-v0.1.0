# PRV-Lab：差分隐私会计可复现实验工具

**生成隐私曲线、检查数值界，并保存可复现实验数据。**

[English](README.md) · [研究协议](docs/research-protocol.md) · [路线图](docs/roadmap.md) · [项目仓库](https://github.com/Austinguis/PRV-Lab-v0.1.0)

PRV-Lab 是一个 Python 研究工具，用于生成隐私曲线、检查数值计算返回的区间，并将实验参数、运行环境和结果一起导出。0.1.0 版本提供解析高斯基准，并可选接入 Microsoft 的 [PRV Accountant](https://github.com/microsoft/prv_accountant)。

## 当前功能

- 计算相同、独立重复组合的非子采样高斯机制的解析 `delta(epsilon)` 曲线。
- 通过 Python API 数值反解目标 delta 对应的 epsilon。
- 接入可选 PRV 后端，计算 Poisson 子采样高斯 DP-SGD 的隐私曲线和 epsilon 界，并保留下界、估计值和上界。
- 在有限网格上对比 PRV 后端与解析高斯基准。
- 导出 CSV 数据、PNG 图片和 JSON 运行元数据。
- 提供单元测试，以及用于测试和构建安装包的 GitHub Actions 工作流。

当前版本是研究工具的初始版本，没有提出新的隐私会计算法。解析高斯基准适用于非子采样机制，不能替代子采样 DP-SGD 的会计计算。

## 安装

需要 Python 3.10 或更新版本。使用克隆方式下载时需要 Git；也可以下载仓库 ZIP 并解压，在包含 `pyproject.toml` 的文件夹中打开终端，从创建虚拟环境的步骤开始执行。

### Windows PowerShell

```powershell
git clone https://github.com/Austinguis/PRV-Lab-v0.1.0.git
cd PRV-Lab-v0.1.0
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -e .
```

如果 PowerShell 不允许执行激活脚本，可以直接使用虚拟环境中的 Python，无需修改执行策略：

```powershell
.\.venv\Scripts\python.exe -m pip install -e .
.\.venv\Scripts\python.exe -m prv_lab.cli --help
```

采用这种方式时，将下文示例开头的 `prv-lab` 替换为 `.\.venv\Scripts\python.exe -m prv_lab.cli` 即可。

### macOS / Linux

```bash
git clone https://github.com/Austinguis/PRV-Lab-v0.1.0.git
cd PRV-Lab-v0.1.0
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e .
```

### 可选依赖

在项目根目录中，使用虚拟环境执行：

```bash
# 安装 PRV 后端，用于 DP-SGD 和验证命令。
python -m pip install -e ".[prv]"

# 安装测试、代码检查和安装包构建工具。
python -m pip install -e ".[dev]"
```

也可以执行 `python -m pip install -e ".[dev,prv]"`，同时安装两组依赖。默认安装即可使用解析高斯基准，不要求安装 PRV 后端。这里使用从仓库源码安装的方式，不预设项目已经发布到 PyPI。

## 快速开始

以下命令均为单行。激活虚拟环境后，可以直接粘贴到 PowerShell 或 Bash 兼容终端中执行。

### 1. 解析高斯隐私曲线

```bash
prv-lab gaussian-curve --noise-std 2.0 --sensitivity 1.0 --steps 100 --eps-max 5 --points 201 --output-dir results/gaussian-demo
```

输出文件：

- `gaussian_curve.csv`：epsilon 与解析 delta 值。
- `gaussian_curve.png`：隐私曲线图。
- `run_metadata.json`：参数、时间和运行环境信息。

对于重复组合次数 `k`、查询敏感度 `Delta` 和每步噪声标准差 `sigma`，解析基准采用：

$$
\mu = \frac{\sqrt{k}\,\Delta}{\sigma}, \qquad
\delta(\epsilon) = \Phi\!\left(\frac{\mu}{2}-\frac{\epsilon}{\mu}\right)
- e^{\epsilon}\Phi\!\left(-\frac{\mu}{2}-\frac{\epsilon}{\mu}\right).
$$

其中 `Phi` 为标准正态分布的累积分布函数。上述公式是解析表达式，程序使用浮点数进行数值计算。

也可以在 Python 中反解 epsilon：

```python
from prv_lab.curves import gaussian_epsilon

epsilon = gaussian_epsilon(
    delta=1e-5,
    noise_std=2.0,
    sensitivity=1.0,
    steps=100,
)
print(epsilon)
```

### 2. DP-SGD 隐私曲线

先安装可选 PRV 后端，再执行：

```bash
prv-lab dpsgd-curve --sampling-probability 0.01 --noise-multiplier 1.2 --steps 1000 --eps-max 8 --points 201 --eps-error 0.01 --delta-error 1e-8 --output-dir results/dpsgd-demo
```

输出 `dpsgd_curve.csv`、`dpsgd_curve.png` 和 `run_metadata.json`。CSV 保留后端返回的 delta 下界、估计值和上界。

### 3. 计算目标 delta 对应的 epsilon 界

```bash
prv-lab dpsgd-epsilon --sampling-probability 0.01 --noise-multiplier 1.2 --steps 1000 --delta 1e-5 --eps-error 0.01 --output-dir results/dpsgd-epsilon
```

输出 `dpsgd_epsilon.csv` 和 `run_metadata.json`，并在终端显示 epsilon 的下界、估计值和上界。

### 4. 对比 PRV 后端与解析高斯基准

```bash
prv-lab validate-gaussian --noise-std 2.0 --steps 100 --eps-max 5 --points 101 --output-dir results/gaussian-validation
```

该命令在两种实现间对比非子采样高斯机制。输出包括 `gaussian_validation.csv`、`gaussian_validation.png` 和 `run_metadata.json`，并记录解析值落在后端区间内的网格点数量。有限网格上的检查不能证明所有参数下的正确性。

## 开发与验证

在项目根目录中激活虚拟环境后执行：

```bash
python -m pip install -e ".[dev]"
python -m pytest
python -m ruff check .
python -m build
```

CI 工作流配置了 Python 3.10、3.11 和 3.12。默认测试环境不安装真实 PRV 后端；适配器测试使用模拟后端，另有测试检查缺少可选依赖时的提示信息。仅通过这些测试不能证明真实后端的数值行为已得到验证。

发布构建工作流可通过推送 `v*` 标签或手动触发来生成安装包，但不会自动发布到 PyPI，也不会自动创建 GitHub Release。维护者发布步骤见 [PUBLISHING.md](PUBLISHING.md)。

## 研究协议与适用范围

解释比较结果或撰写实验结论前，请阅读[研究协议](docs/research-protocol.md)。

- 对比不同会计方法时，应固定机制、邻接关系、采样模型、噪声尺度、组合次数和误差目标。
- 隐私保证应依据有效上界；估计值和上界是不同的量。
- 记录硬件、依赖版本、精度设置、误差容限和失败运行，以便复现实验。
- 将输出用于隐私保证之前，应核实完整分析中的机制假设与参数。

后续适配器和基准实验计划见[路线图](docs/roadmap.md)。计划中的功能不代表当前版本已经实现。

## 参与贡献与安全报告

提交修改前请阅读 [CONTRIBUTING.md](CONTRIBUTING.md)。普通问题和功能建议可提交到 [Issues](https://github.com/Austinguis/PRV-Lab-v0.1.0/issues)，请附最小复现、完整命令和运行环境。

涉及漏洞或可能导致隐私保证失效的数值问题，请遵循 [SECURITY.md](SECURITY.md)。公开报告中应移除凭据、私有数据和可识别个人身份的信息。

## 引用

可使用 [CITATION.cff](CITATION.cff) 引用软件，并注明实验使用的版本或提交。使用底层会计方法和库时，也应引用对应研究与实现。

## 许可证

PRV-Lab 采用 [MIT 许可证](LICENSE)。各项依赖保留其自身的许可证。

## 参考资料

- Gopi、Lee、Wutschitz，[Numerical Composition of Differential Privacy](https://arxiv.org/abs/2106.02848)，NeurIPS 2021。
- Microsoft [PRV Accountant](https://github.com/microsoft/prv_accountant)。
