# Text2Rule: 医疗文本到规则转换框架

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Status](https://img.shields.io/badge/Status-Research-orange.svg)]()

Text2Rule 是一个基于大语言模型的医疗文本到规则转换框架，能够将医疗质控指标的自然语言描述自动转换为可执行的Python函数和逻辑规则。

## 🎯 项目概述

本项目旨在解决医疗质控指标自动化处理的核心问题：如何将复杂的医疗质控指标从自然语言描述转换为可执行的计算机程序。通过结合大语言模型的推理能力和医疗领域知识，Text2Rule能够：

- **自动生成Python函数**：将医疗质控指标转换为可执行的Python代码
- **智能参数提取**：从电子病历中自动提取相关参数
- **多模型支持**：支持GPT-4、Qwen等多种大语言模型
- **医疗领域优化**：针对医疗质控场景进行专门优化

## ✨ 主要功能

### 1. 函数生成器 (Function Generator)
- 基于医疗质控指标描述自动生成Python函数
- 支持多种医疗计算场景（MedCalc、质控指标等）
- 自动生成函数参数和属性定义
- 多Agent协作生成高质量代码

### 2. 函数执行器 (Function Executor)
- 从电子病历中智能提取相关参数
- 支持单位转换和数值处理
- 批量执行生成的函数
- 结果验证和错误分析

### 3. 评估框架 (Evaluation Framework)
- 多维度性能评估
- 错误分析和对比
- 可视化结果展示
- 基准测试对比

## 🏗️ 项目结构

```
text2rule/
├── framework/                 # 核心框架
│   ├── function_generator.py  # 函数生成器
│   └── function_executor.py   # 函数执行器
├── dataset/                   # 数据集
│   ├── MedCalc_test_data.jsonl
│   ├── MedCalc_test_data.csv
│   └── indicator.json
├── evaluation/                # 评估结果
│   ├── final_results/         # 最终评估结果
│   ├── baseline_medcalc/      # 基线模型结果
│   └── *.pdf                  # 评估报告
├── baseline/                  # 基线模型
│   ├── MENTI/
│   └── MedCalc-Bench-main/
└── data.jsonl                 # 主数据集
```

## 🚀 快速开始

### 环境要求

- Python 3.8+
- OpenAI API Key 或 Qwen API Key

### 安装依赖

```bash
pip install openai autogen-agentchat pandas numpy matplotlib seaborn
```

### 配置API

在 `framework/function_generator.py` 和 `framework/function_executor.py` 中配置您的API密钥：

```python
MODEL_CONFIGS = {
    "gpt-4o-mini": {
        "model": "gpt-4o-mini",
        "api_key": "your-openai-key",
        "base_url": "your-openai-base-url",
    },
    "qwen": {
        "model": "qwen2.5-72b-instruct",
        "api_key": "your-qwen-key",
        "base_url": "your-qwen-base-url",
    }
}
```

### 运行示例

1. **生成函数**：
```bash
cd framework
python function_generator.py
```

2. **执行函数**：
```bash
python function_executor.py
```

## 📊 性能评估

项目包含完整的评估框架，支持：

- **准确性评估**：函数生成和执行的准确性
- **错误分析**：详细的错误类型和原因分析
- **对比实验**：与基线模型的性能对比
- **可视化报告**：自动生成评估图表和报告

## 🔬 研究贡献

本项目在以下方面做出了贡献：

1. **医疗质控自动化**：首次将大语言模型应用于医疗质控指标的自动化处理
2. **多Agent协作**：设计了专门的多Agent协作框架用于医疗函数生成
3. **医疗领域优化**：针对医疗场景的特殊需求进行了专门优化
4. **评估基准**：建立了医疗质控指标处理的评估基准

## 📝 使用场景

- **医院质控管理**：自动化处理医疗质控指标
- **临床决策支持**：基于电子病历的自动化决策
- **医疗研究**：大规模医疗数据分析
- **医疗AI开发**：为医疗AI系统提供规则引擎

## 🤝 贡献指南

我们欢迎社区贡献！请查看 [CONTRIBUTING.md](CONTRIBUTING.md) 了解如何参与项目开发。

### 贡献方式

1. Fork 本项目
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 🙏 致谢

- 感谢所有参与医疗质控标准制定的专家
- 感谢开源社区提供的优秀工具和框架
- 感谢所有为项目做出贡献的研究者和开发者

## 📞 联系我们

- 项目主页：https://github.com/your-username/text2rule
- 问题反馈：https://github.com/your-username/text2rule/issues
- 邮箱：your-email@example.com

---

**注意**：本项目仅供研究使用，不构成医疗建议。在实际医疗环境中使用前，请确保符合相关法规和标准。 