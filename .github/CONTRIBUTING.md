# 贡献指南

感谢您对钱包管理工具项目的关注！我们欢迎所有形式的贡献。

## 🚀 如何贡献

### 报告 Bug

如果您发现了一个 bug，请创建一个 issue 并包含以下信息：

- Bug 的详细描述
- 重现步骤
- 预期行为
- 您的环境信息（操作系统、Python 版本等）
- 如果可能，请提供截图或错误日志

### 请求新功能

如果您希望添加新功能，请：

1. 首先检查现有的 issues，看看是否已经有人提出了类似的功能
2. 创建一个新的 issue，详细描述您想要的功能
3. 解释为什么这个功能对项目有用

### 提交代码

1. Fork 这个仓库
2. 创建一个新的分支：`git checkout -b feature/your-feature-name`
3. 进行您的更改
4. 确保代码符合项目的编码标准
5. 提交您的更改：`git commit -m 'Add some feature'`
6. 推送到分支：`git push origin feature/your-feature-name`
7. 创建一个 Pull Request

## 📋 开发环境设置

1. 克隆仓库：
   ```bash
   git clone https://github.com/your-username/wallet-management-tools.git
   cd wallet-management-tools
   ```

2. 创建虚拟环境：
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/macOS
   # 或
   venv\Scripts\activate  # Windows
   ```

3. 安装依赖：
   ```bash
   pip install -r requirements.txt
   pip install -r requirements-dev.txt  # 开发依赖
   ```

## 🧪 测试

在提交代码之前，请确保：

1. 运行所有测试：
   ```bash
   pytest
   ```

2. 检查代码格式：
   ```bash
   black --check .
   flake8 .
   ```

3. 运行安全扫描：
   ```bash
   bandit -r .
   safety check
   ```

## 📝 编码标准

- 使用 Python 3.8+
- 遵循 PEP 8 编码风格
- 使用 Black 进行代码格式化
- 使用类型提示
- 为所有函数和类编写文档字符串
- 保持代码简洁和可读性

## 🔒 安全

如果您发现安全漏洞，请：

1. **不要**在公开的 issue 中报告
2. 发送邮件到 [在此处插入安全邮箱]
3. 我们将尽快回复并处理

## 📄 许可证

通过贡献代码，您同意您的贡献将在项目的许可证下发布。

## 🎉 致谢

感谢所有为这个项目做出贡献的人！

---

如果您有任何问题，请随时创建 issue 或联系项目维护者。 