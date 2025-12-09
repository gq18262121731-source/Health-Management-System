# 安装与环境配置指南

## 系统要求

- **Python**: 3.7 或更高版本
- **操作系统**: Windows / Linux / macOS
- **内存**: 建议 4GB 以上

## 快速安装

### 1. 安装核心依赖（必需）

```bash
pip install numpy pandas scipy scikit-learn
```

或使用清华镜像源（国内用户推荐）：

```bash
pip install -i https://pypi.tuna.tsinghua.edu.cn/simple numpy pandas scipy scikit-learn
```

### 2. 验证安装

运行快速测试脚本：

```bash
cd health_assessment_system
python examples\quick_test.py
```

如果看到 "✓ All tests passed successfully!"，说明安装成功！

## 可选依赖

以下依赖用于高级功能，可根据需要选择性安装：

### 模糊逻辑支持
```bash
pip install scikit-fuzzy
```

### 隐马尔可夫模型
```bash
pip install hmmlearn
```

### 变点检测
```bash
pip install ruptures
```

### 时间序列预测
```bash
pip install prophet
```

### 数据可视化
```bash
pip install matplotlib seaborn
```

### 报告生成
```bash
pip install reportlab jinja2
```

## 常见问题

### Q1: pip 安装速度慢怎么办？

**A**: 使用国内镜像源：

```bash
# 临时使用
pip install -i https://pypi.tuna.tsinghua.edu.cn/simple <package_name>

# 永久配置
pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple
```

### Q2: 提示 "No module named 'pandas'" 怎么办？

**A**: 确保已安装核心依赖：

```bash
pip install pandas
```

### Q3: 安装 requirements.txt 时出现编码错误？

**A**: 这是因为文件包含中文注释。已修复，现在可以直接使用：

```bash
pip install -r requirements.txt
```

注意：使用 `-r` 参数，不是直接 `pip install requirements.txt`

### Q4: 看到 "WARNING: Ignoring invalid distribution -umpy"？

**A**: 这是 pip 的警告，不影响使用。如需清理：

```bash
# 找到 Python 的 site-packages 目录
# 删除以 ~ 或 - 开头的异常目录
```

### Q5: 系统可以在没有可选依赖的情况下运行吗？

**A**: 可以！系统会自动检测缺失的可选依赖，并使用简化版算法：

- 没有 `scikit-fuzzy`：使用简化的模糊逻辑
- 没有 `hmmlearn`：跳过 HMM 分析
- 没有 `ruptures`：使用统计方法进行变点检测

## 虚拟环境（推荐）

使用虚拟环境可以避免依赖冲突：

### Windows
```bash
# 创建虚拟环境
python -m venv venv

# 激活虚拟环境
venv\Scripts\activate

# 安装依赖
pip install numpy pandas scipy scikit-learn

# 退出虚拟环境
deactivate
```

### Linux/macOS
```bash
# 创建虚拟环境
python3 -m venv venv

# 激活虚拟环境
source venv/bin/activate

# 安装依赖
pip install numpy pandas scipy scikit-learn

# 退出虚拟环境
deactivate
```

## 验证安装

### 方法1: 运行快速测试
```bash
python examples\quick_test.py
```

### 方法2: Python 交互式测试
```python
# 启动 Python
python

# 导入模块
>>> from health_assessment_system import HealthAssessmentEngine
>>> engine = HealthAssessmentEngine()
>>> print("安装成功！")
```

### 方法3: 检查依赖版本
```bash
pip list | findstr "numpy pandas scipy scikit-learn"
```

应该看到：
```
numpy        1.24.3
pandas       2.3.3
scikit-learn 1.7.2
scipy        1.15.3
```

## 性能优化建议

### 1. 升级 pip
```bash
python -m pip install --upgrade pip
```

### 2. 使用更快的依赖解析器
```bash
pip install --use-feature=fast-deps numpy pandas scipy scikit-learn
```

### 3. 并行安装（Python 3.10+）
```bash
pip install --use-pep517 numpy pandas scipy scikit-learn
```

## 开发环境配置

如果需要修改代码，建议安装开发工具：

```bash
# 代码格式化
pip install black flake8

# 类型检查
pip install mypy

# 测试框架
pip install pytest pytest-cov

# Jupyter 支持
pip install jupyter notebook
```

## Docker 部署（可选）

创建 `Dockerfile`：

```dockerfile
FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "examples/quick_test.py"]
```

构建和运行：

```bash
docker build -t health-assessment .
docker run health-assessment
```

## 下一步

安装完成后，可以：

1. 查看 [README.md](README.md) 了解系统功能
2. 查看 [ARCHITECTURE.md](ARCHITECTURE.md) 了解系统架构
3. 运行 `examples/complete_demo.py` 查看完整演示
4. 开始集成到您的应用中

## 技术支持

如遇到安装问题：

1. 检查 Python 版本：`python --version`
2. 检查 pip 版本：`pip --version`
3. 查看错误日志
4. 尝试使用虚拟环境

---

**最后更新**: 2025-11-25  
**适用版本**: v1.0.0
