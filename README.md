# Text2Rule - 医疗质控函数生成和执行工具

Text2Rule是一个基于大语言模型的医疗质控函数自动生成和执行工具。它能够根据医疗质控指标描述自动生成Python函数，并在患者病历数据上执行这些函数来评估质控指标。

## 项目架构

```
text2rule/
├── config/                     # 配置管理
│   ├── models.py              # 模型配置
│   ├── tasks.py               # 任务配置
│   ├── prompts.py             # 提示词配置
│   └── paths.py               # 路径配置
├── core/                      # 核心功能
│   ├── base.py                # 基础类
│   ├── llm_client.py          # LLM客户端
│   └── data_processor.py      # 数据处理
├── generators/                # 函数生成模块
│   ├── agent_team.py          # Agent团队
│   ├── function_generator.py  # 函数生成器
│   └── code_parser.py         # 代码解析
├── executors/                 # 函数执行模块
│   ├── parameter_extractor.py # 参数提取
│   ├── function_executor.py   # 函数执行器
│   └── unit_converter.py      # 单位转换
├── utils/                     # 工具模块
│   ├── file_utils.py          # 文件操作
│   ├── json_utils.py          # JSON处理
│   └── validation.py          # 数据验证
├── data/                      # 数据目录
│   ├── generated_functions/   # 生成的函数
│   ├── patient_data/          # 患者数据
│   └── indicators/            # 指标数据
├── results/                   # 结果目录
│   └── execution_results/     # 执行结果
├── logs/                      # 日志目录
├── tests/                     # 测试目录
├── main.py                    # 主入口
└── requirements.txt           # 依赖
```

## 功能特性

- **多模型支持**: 支持GPT-4o-mini、Qwen、Claude等多种大语言模型
- **多任务类型**: 支持医疗计算(medcalc)、质控指标(indicator)等任务类型
- **Agent协作**: 使用多Agent协作生成高质量的Python函数
- **参数提取**: 自动从病历中提取相关参数
- **单位转换**: 支持医疗单位的自动转换
- **模块化设计**: 清晰的模块划分，易于扩展和维护

## 安装

1. 克隆项目
```bash
git clone <repository-url>
cd text2rule
```

2. 安装依赖
```bash
pip install -r requirements.txt
```

3. 配置环境变量
```bash
cp env.example .env
# 编辑 .env 文件，填入你的API密钥
```

## 使用方法

### 命令行使用

1. **完整流程**（生成函数并执行）
```bash
python main.py --model gpt-4o-mini --task-type indicator --api-key YOUR_API_KEY --base-url YOUR_BASE_URL
```

2. **仅生成函数**
```bash
python main.py --mode generate --model gpt-4o-mini --task-type indicator --api-key YOUR_API_KEY --base-url YOUR_BASE_URL
```

3. **仅执行函数**
```bash
python main.py --mode execute --model gpt-4o-mini --task-type indicator --api-key YOUR_API_KEY --base-url YOUR_BASE_URL
```

4. **指定特定ID**
```bash
python main.py --include-ids "肺癌_手术指征符合率（核心指标）" "脑出血（ICH）质控指标_手术适应症符合率"
```

### 参数说明

- `--model`: 使用的模型名称 (gpt-4o-mini, qwen, claude-sonnet, gpt-4.1-mini)
- `--task-type`: 任务类型 (medcalc, cmqcic, indicator)
- `--mode`: 运行模式 (generate, execute, pipeline)
- `--api-key`: API密钥
- `--base-url`: API基础URL
- `--include-ids`: 指定要处理的ID列表

### 编程使用

```python
import asyncio
from main import Text2Rule

# 创建Text2Rule实例
text2rule = Text2Rule(model_name="gpt-4o-mini", task_type="indicator")

# 运行完整流程
success = await text2rule.run_pipeline(
    api_key="your_api_key",
    base_url="your_base_url"
)

if success:
    print("流程执行成功")
else:
    print("流程执行失败")
```

## 配置说明

### 模型配置

在 `config/models.py` 中配置支持的模型：

```python
MODELS = {
    "gpt-4o-mini": {
        "model": "gpt-4o-mini-2024-07-18",
        "api_key": "",
        "base_url": "",
        "extraction_model": "gpt-4o-mini-2024-07-18",
        "conversion_model": "gpt-4o-mini-2024-07-18"
    },
    # 其他模型配置...
}
```

### 任务配置

在 `config/tasks.py` 中配置任务类型：

```python
TASK_SPECIFIC_CONFIGS = {
    "indicator": {
        "patient_data_file": 'data/patient_data/data.jsonl',
        "patient_id_key": "unique_id",
        "patient_note_key": "patient note",
        "indicator_file": 'data/indicators/indicator.json'
    },
    # 其他任务配置...
}
```

## 数据格式

### 患者数据格式

```json
{
    "unique_id": "肺癌_手术指征符合率（核心指标）",
    "patient note": "患者病历内容..."
}
```

### 生成的函数格式

```json
{
    "task_index": "肺癌_手术指征符合率（核心指标）",
    "python_code": "def check_lung_cancer_surgery(...): ...",
    "properties": {
        "row": "properties = {...}"
    },
    "need_unit": {
        "parameter_name": "target_unit"
    }
}
```

## 开发指南

### 添加新模型

1. 在 `config/models.py` 中添加模型配置
2. 在 `utils/validation.py` 中更新验证逻辑
3. 测试新模型的功能

### 添加新任务类型

1. 在 `config/tasks.py` 中添加任务配置
2. 在 `core/data_processor.py` 中添加数据加载逻辑
3. 在 `utils/validation.py` 中更新验证逻辑

### 运行测试

```bash
python -m unittest tests/test_config.py
```

## 注意事项

1. **API密钥安全**: 请妥善保管API密钥，不要提交到版本控制系统
2. **数据隐私**: 确保患者数据的安全性和隐私保护
3. **模型限制**: 注意不同模型的API调用限制和成本
4. **错误处理**: 系统包含完善的错误处理和日志记录

## 许可证

本项目采用 MIT 许可证，详见 LICENSE 文件。

## 贡献

欢迎提交Issue和Pull Request来改进项目。

## 联系方式

如有问题，请通过Issue或邮件联系项目维护者。 