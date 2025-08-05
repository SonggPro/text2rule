# 医学指标计算系统

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Gradio](https://img.shields.io/badge/Gradio-4.0+-orange.svg)](https://gradio.app/)

基于大语言模型（LLM）的自动化医学指标计算和评估系统。

## 🌟 特性

- 🤖 **智能信息提取**: 使用LLM从电子病历中自动提取医学信息
- 📊 **指标计算**: 自动计算各种医学质控指标
- 🖥️ **Web界面**: 基于Gradio的友好用户界面
- 🔧 **命令行工具**: 支持批量处理和自动化
- 🔄 **多模型支持**: 支持OpenAI和Qwen等多种LLM
- 📈 **结果可视化**: 直观的结果展示和分析
- 🛡️ **安全配置**: API密钥通过前端安全传入

## 🚀 快速开始

### 安装

```bash
# 克隆项目
git clone <repository-url>
cd text2rule

# 安装依赖
pip install -r requirements.txt
```

### 运行

#### Web界面模式（推荐）
```bash
python main.py --mode web
```
访问 `http://localhost:7860` 使用Web界面

#### 命令行模式
```bash
python main.py --mode cli \
    --api-key YOUR_API_KEY \
    --base-url YOUR_BASE_URL \
    --task-type cmqcic
```

## 📁 项目结构

```
text2rule/
├── config/                 # 配置管理
│   ├── __init__.py
│   └── settings.py        # 系统配置
├── core/                   # 核心功能
│   ├── __init__.py
│   ├── utils.py           # 工具函数
│   ├── llm_client.py      # LLM客户端
│   ├── data_loader.py     # 数据加载器
│   └── function_executor.py # 函数执行器
├── executor/               # 执行器
│   ├── __init__.py
│   └── main_executor.py   # 主执行器
├── web/                    # Web界面
│   ├── __init__.py
│   └── gradio_app.py      # Gradio应用
├── data/                   # 数据目录
│   ├── generated_functions/
│   └── patient_data/
├── results/                # 结果目录
├── logs/                   # 日志目录
├── docs/                   # 文档
│   ├── README.md
│   └── 操作指南.md
├── main.py                 # 主程序入口
└── requirements.txt        # 依赖列表
```

## 🔧 配置

### API配置

在Web界面中配置或通过命令行参数传入：

- **API Key**: 您的LLM服务API密钥
- **Base URL**: API服务地址
- **模型提供商**: OpenAI或Qwen

### 任务配置

支持两种任务类型：

- **CMCIC**: 医学质控指标计算
- **MedCalc**: 医学计算器任务

## 📊 使用示例

### Web界面使用

1. **系统配置**: 输入API配置并测试连接
2. **任务执行**: 选择任务类型并开始批量处理
3. **单任务测试**: 测试单个任务的执行效果
4. **结果查看**: 查看和分析执行结果

### 命令行使用

```bash
# 基本执行
python main.py --mode cli \
    --api-key sk-xxx \
    --base-url https://api.openai.com/v1 \
    --task-type cmqcic

# 指定任务
python main.py --mode cli \
    --api-key sk-xxx \
    --base-url https://api.openai.com/v1 \
    --task-type cmqcic \
    --include-ids task1 task2

# 自定义输出
python main.py --mode cli \
    --api-key sk-xxx \
    --base-url https://api.openai.com/v1 \
    --task-type cmqcic \
    --output-file results/custom.jsonl
```

## 📈 数据格式

### 输入数据格式

```json
{
    "unique_id": "患者ID",
    "patient note": "患者病历内容..."
}
```

### 输出结果格式

```json
{
    "id": "任务ID",
    "results": [
        {
            "extract_para": {"参数1": "值1"},
            "result": 0.85
        }
    ]
}
```

## 🛠️ 开发

### 添加新的LLM提供商

1. 在 `config/settings.py` 中添加配置
2. 在 `core/llm_client.py` 中实现客户端
3. 更新Web界面选项

### 添加新的任务类型

1. 在 `config/settings.py` 中添加任务配置
2. 准备相应的数据文件
3. 更新界面选项

## 📚 文档

- [操作指南](docs/操作指南.md) - 详细的使用说明
- [API文档](docs/api.md) - 开发API文档
- [故障排除](docs/troubleshooting.md) - 常见问题解决

## 🤝 贡献

欢迎提交Issue和Pull Request！

1. Fork项目
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 打开Pull Request

## 📄 许可证

本项目采用MIT许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 📞 联系方式

- 项目主页: [GitHub Repository]
- 问题反馈: [Issues]
- 邮箱: [your-email@example.com]

## 🙏 致谢

感谢所有为这个项目做出贡献的开发者和研究人员！ 