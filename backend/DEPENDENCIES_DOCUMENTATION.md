# 项目依赖文档

本文档详细列出了养生之道项目后端的所有依赖包，包括版本信息、用途说明以及安装建议。

## 依赖文件说明

项目使用以下几个依赖文件来组织不同环境和用途的依赖：

- **requirements.txt**: 完整的项目依赖，包括核心依赖、AI功能依赖、测试依赖等
- **requirements_core.txt**: 核心功能依赖，包含运行API服务的必要组件
- **requirements_minimal.txt**: 最小化依赖，仅包含最基本的服务组件
- **requirements_test.txt**: 测试相关依赖

## 依赖包详情

### 核心依赖 (Core Dependencies)

| 包名 | 版本 | 用途 | 所属文件 |
|------|------|------|----------|
| fastapi | 0.104.1 (主版本) / 0.105.0 (最小化版本) | Web框架，用于构建RESTful API | requirements.txt, requirements_core.txt, requirements_minimal.txt |
| uvicorn | 0.24.0 (带standard扩展) / 0.24.0.post1 | ASGI服务器，用于运行FastAPI应用 | requirements.txt, requirements_core.txt, requirements_minimal.txt |
| python-multipart | 0.0.6 | 处理表单数据，用于文件上传等功能 | requirements.txt, requirements_core.txt |
| sqlalchemy | 2.0.23 | ORM数据库操作框架 | requirements.txt, requirements_core.txt, requirements_minimal.txt |
| psycopg2-binary | 2.9.9 | PostgreSQL数据库驱动 | requirements.txt, requirements_core.txt |
| python-dotenv | 1.0.0 | 环境变量管理，从.env文件加载配置 | requirements.txt, requirements_core.txt, requirements_minimal.txt |
| python-jose[cryptography] | 3.3.0 | JWT令牌生成和验证，用于身份认证 | requirements.txt, requirements_core.txt |
| passlib[bcrypt] | 1.7.4 | 密码哈希和验证 | requirements.txt, requirements_core.txt |
| pydantic | 2.5.0 (主版本) / 2.6.4 (最小化版本) | 数据验证和设置管理 | requirements.txt, requirements_core.txt, requirements_minimal.txt |
| pydantic-settings | 2.1.0 | 增强的设置管理，替代pydantic的BaseSettings | requirements.txt, requirements_core.txt, requirements_minimal.txt |

### AI功能依赖 (AI Dependencies)

| 包名 | 版本 | 用途 | 所属文件 |
|------|------|------|----------|
| faiss-cpu | 1.9.0.post1 | 高效相似度搜索库，用于知识检索 | requirements.txt |
| sentence-transformers | 2.5.1 | 文本嵌入生成，用于文档向量化 | requirements.txt |
| numpy | 1.26.4 | 科学计算库，支持向量运算 | requirements.txt |
| python-magic | 0.4.27 | 文件类型检测，用于文档处理 | requirements.txt |
| PyPDF2 | 3.0.1 | PDF文件处理库 | requirements.txt |
| python-docx | 1.1.0 | Word文档处理库 | requirements.txt |

### 缓存和日志依赖 (Cache & Logging Dependencies)

| 包名 | 版本 | 用途 | 所属文件 |
|------|------|------|----------|
| aioredis | 2.0.1 | Redis异步客户端，用于缓存 | requirements.txt |
| python-json-logger | 2.0.7 | JSON格式日志记录 | requirements.txt |

### 测试依赖 (Testing Dependencies)

| 包名 | 版本 | 用途 | 所属文件 |
|------|------|------|----------|
| pytest | 7.4.3 | 测试框架 | requirements.txt, requirements_test.txt |
| pytest-cov | 4.1.0 | 测试覆盖率统计 | requirements.txt, requirements_test.txt |
| httpx | 0.25.2 | HTTP客户端，用于API测试 | requirements.txt, requirements_test.txt |

## 安装建议

### Python版本兼容性

项目当前推荐使用以下Python版本：
- 首选：Python 3.10 或 3.11
- 注意：Python 3.13可能需要调整部分依赖版本

### 安装步骤

1. **创建虚拟环境**
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # Linux/Mac
   .venv\Scripts\activate  # Windows
   ```

2. **安装依赖**
   
   - 完整依赖（开发和生产环境）：
     ```bash
     pip install -r requirements.txt
     ```
     
   - 仅核心依赖（基本生产环境）：
     ```bash
     pip install -r requirements_core.txt
     ```
     
   - 最小化依赖（快速测试）：
     ```bash
     pip install -r requirements_minimal.txt
     ```
     
   - 仅测试依赖：
     ```bash
     pip install -r requirements_test.txt
     ```

### 常见安装问题解决方案

1. **NumPy安装问题**
   - 确保使用Python 3.10+版本
   - 尝试更新pip：`pip install --upgrade pip`
   - 对于Python 3.13，建议使用NumPy 1.26.4或更高版本

2. **Pydantic-Core构建问题**
   - 如果遇到Rust编译错误，建议使用预编译的wheel包
   - 尝试安装更新版本的pydantic（如2.6.4+）

3. **FAISS安装问题**
   - 确保pip版本足够新
   - 对于不兼容的系统，可能需要从源码编译

## 版本升级建议

1. **定期更新依赖**
   - 建议每季度检查并更新依赖版本
   - 使用`pip list --outdated`检查过时的包

2. **安全更新**
   - 关注安全公告，及时更新有安全漏洞的包
   - 考虑使用依赖扫描工具如Safety或Bandit

3. **兼容性测试**
   - 更新依赖后必须运行完整的测试套件
   - 特别注意pydantic和sqlalchemy等核心库的版本兼容性

## 依赖管理最佳实践

1. **锁定版本**
   - 始终在requirements文件中指定具体版本号
   - 使用`pip freeze > requirements.txt`生成精确的依赖锁定

2. **虚拟环境**
   - 每个项目使用独立的虚拟环境
   - 不要在全局Python环境中安装项目依赖

3. **文档更新**
   - 添加新依赖时，同步更新此文档
   - 记录每个依赖的具体用途和版本变更原因

---

*最后更新时间：2025年6月*
*养生之道项目后端团队*