# 贡献指南

感谢您对 Text2Rule 项目的关注！我们欢迎所有形式的贡献，包括但不限于：

- 🐛 Bug 报告
- 💡 功能建议
- 📝 文档改进
- 🔧 代码贡献
- 🧪 测试用例
- 🌟 示例和教程

## 开发环境设置

### 1. Fork 和 Clone

```bash
# Fork 项目到您的 GitHub 账户
# 然后克隆您的 fork
git clone https://github.com/your-username/text2rule.git
cd text2rule

# 添加上游仓库
git remote add upstream https://github.com/original-username/text2rule.git
```

### 2. 创建虚拟环境

```bash
# 使用 conda
conda create -n text2rule python=3.8
conda activate text2rule

# 或使用 venv
python -m venv text2rule-env
source text2rule-env/bin/activate  # Linux/Mac
# text2rule-env\Scripts\activate  # Windows
```

### 3. 安装依赖

```bash
pip install -r requirements.txt
```

## 开发流程

### 1. 创建分支

```bash
# 从主分支创建新分支
git checkout -b feature/your-feature-name
# 或
git checkout -b fix/your-bug-fix
```

### 2. 开发代码

- 遵循项目的代码风格
- 添加必要的注释和文档
- 确保代码通过所有测试

### 3. 提交代码

```bash
# 添加更改
git add .

# 提交更改（使用清晰的提交信息）
git commit -m "feat: add new medical calculation function"
git commit -m "fix: resolve parameter extraction issue"
git commit -m "docs: update API documentation"
```

### 4. 推送和创建 Pull Request

```bash
git push origin feature/your-feature-name
```

然后在 GitHub 上创建 Pull Request。

## 代码规范

### Python 代码风格

- 遵循 [PEP 8](https://www.python.org/dev/peps/pep-0008/) 规范
- 使用 4 个空格缩进
- 行长度不超过 120 字符
- 使用有意义的变量和函数名

### 提交信息格式

使用 [Conventional Commits](https://www.conventionalcommits.org/) 格式：

```
<type>[optional scope]: <description>

[optional body]

[optional footer(s)]
```

类型包括：
- `feat`: 新功能
- `fix`: Bug 修复
- `docs`: 文档更改
- `style`: 代码格式更改
- `refactor`: 代码重构
- `test`: 测试相关
- `chore`: 构建过程或辅助工具的变动

### 示例

```
feat(api): add support for new medical indicators

- Add function generator for diabetes indicators
- Support multiple unit conversions
- Include comprehensive test cases

Closes #123
```

## 测试指南

### 运行测试

```bash
# 运行所有测试
python -m pytest

# 运行特定测试文件
python -m pytest tests/test_function_generator.py

# 运行带覆盖率的测试
python -m pytest --cov=framework
```

### 添加新测试

- 为新功能添加相应的测试用例
- 确保测试覆盖率达到 80% 以上
- 使用描述性的测试名称

## 文档贡献

### 更新文档

- 更新 README.md 以反映新功能
- 添加 API 文档
- 提供使用示例和教程

### 文档格式

- 使用 Markdown 格式
- 包含代码示例
- 添加必要的截图或图表

## 问题报告

### Bug 报告

在报告 Bug 时，请包含以下信息：

1. **环境信息**：
   - 操作系统版本
   - Python 版本
   - 依赖包版本

2. **重现步骤**：
   - 详细的操作步骤
   - 输入数据示例
   - 期望结果和实际结果

3. **错误信息**：
   - 完整的错误堆栈跟踪
   - 相关日志信息

### 功能建议

在提出功能建议时，请说明：

1. **问题描述**：当前功能的局限性
2. **解决方案**：您建议的改进方案
3. **使用场景**：新功能的应用场景
4. **实现建议**：可选的实现思路

## 审查流程

### Pull Request 审查

1. **自动检查**：确保所有 CI 检查通过
2. **代码审查**：至少需要一名维护者审查
3. **测试覆盖**：确保新代码有足够的测试覆盖
4. **文档更新**：确保相关文档已更新

### 审查标准

- 代码质量和可读性
- 功能完整性和正确性
- 测试覆盖率和质量
- 文档完整性和准确性
- 性能影响评估

## 发布流程

### 版本管理

项目使用 [Semantic Versioning](https://semver.org/)：

- `MAJOR.MINOR.PATCH`
- 例如：`1.0.0`、`1.1.0`、`1.1.1`

### 发布步骤

1. 更新版本号
2. 更新 CHANGELOG.md
3. 创建发布标签
4. 发布到 PyPI（如果适用）

## 社区行为准则

### 行为准则

我们致力于为每个人提供友好、安全和欢迎的环境。请：

- 尊重所有贡献者
- 使用包容性语言
- 接受建设性批评
- 关注社区利益
- 展示对其他社区成员的同情

### 不当行为

以下行为是不被接受的：

- 使用性暗示的语言或图像
- 恶意攻击、侮辱或贬损性评论
- 骚扰或跟踪
- 发布他人的私人信息
- 其他可能被认为不当的行为

## 联系方式

如果您有任何问题或需要帮助：

- 创建 [GitHub Issue](https://github.com/your-username/text2rule/issues)
- 发送邮件到：your-email@example.com
- 加入我们的讨论组

## 致谢

感谢所有为项目做出贡献的开发者！您的贡献使 Text2Rule 变得更好。

---

**注意**：本指南可能会根据项目发展需要更新。请定期查看最新版本。 