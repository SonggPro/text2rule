import asyncio
import json
import re
import csv
import time
import ast
from typing import List, Dict, Any, Optional

from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.teams import RoundRobinGroupChat
from autogen_agentchat.conditions import TextMentionTermination
from autogen_core import CancellationToken
from autogen_ext.models.openai import OpenAIChatCompletionClient

# --- 配置部分 ---

# API和模型配置
MODEL_CONFIGS = {
    "gpt-4o-mini": {
        "model": "gpt-4o-mini",
        "api_key": "", #openai key
        "base_url": "", #openai base url
    },
    "qwen": {
        "model": "qwen2.5-72b-instruct",
        "api_key": "", #key
        "base_url": "", #base url
        "model_info" : {
        "vision": False,
        "function_calling": True,
        "json_output": True,
        "family": "qwen",
        "structured_output": True,
        "model": "qwen-2.5-72b-instruct"
    }
    }
}


# 任务配置
TASK_CONFIG = {
    "task_type": "indicator",  # "medcalc" 或 "indicator"
    "selected_model": "gpt-4o-mini",
    "medcalc_file": "/dataset/test_data_yu.csv",
    "indicator_file": "/dataset/indicator.json",
    "output_file_template": "generate_function/{task_type}_{model_name}.jsonl",
    "log_file": "medcalc_all_logs.json"
}

# Agent 系统消息
SYSTEM_MESSAGES = {
    "medcalc": {
        "analyst":"""
            Your task is to analyze a medical quality control question using the Chain-of-Thought (CoT) method. First, you need to break down the process of solving this question, including how to perform calculations. Then, you should derive the formulas required for this solution process. Finally, list all the variables in these formulas, along with their descriptions and units.
            Please follow these steps:
            1. Carefully read the medical quality control question.
            2. Analyze the steps needed to solve the question, including how to calculate the required values.
            3. Based on the analysis, identify the formulas that are necessary for the solution.
            4. For each formula, list all the variables involved, provide a clear description of each variable, and specify its unit.
            5.the formula should use the latest version of the formula.

            First, in the <analysis> tag, detail the step - by - step process of solving the question. Then, in the <formulas> tag, list all the formulas. Finally, in the <variables> tag, list each variable, its description, and its unit in a tabular format.
            <analysis>
            [Describe the step - by - step solution process here]
            </analysis>
            <formulas>
            [List all the necessary formulas here]
            </formulas>
            <variables>
            | Variable | Description | Unit |
            | --- | --- | --- |
            | [Variable name 1] | [Description of variable 1] | [Unit of variable 1] |
            | [Variable name 2] | [Description of variable 2] | [Unit of variable 2] |
            |... |... |... |
            </variables>
            """,
        "coder": """You are a programming expert familiar with the medical field. Based on the logic and calculation formula and varaibles analyzed by your colleague:Analyst, create a 'Python function' and a `properties` dictionary to calculate the specified question.
            Requirements:

            1. The function's parameters must represent factual logical judgments or numerical values.if possible, write number type judgment logic code like 'if parameter > 20' in function rather than define a boolean type parameter.

            2. Provide a `properties` dictionary containing all parameters required by the function.

            3. Each parameter key in `properties` must include:
            - `description`: in English,
                - For numerical parameters, the description must follow the format: "<specific meaning of the number> + unit "
                - For boolean judgment parameters, the description must clearly state that the parameter returns True or False.
                - For string judgment parameters, the description must clearly state that the parameter returns a string representing a logical judgment.
            - `type`: must be one of "boolean", "string", or "number".
                - Use `"boolean"` for parameters representing true/false values.
                - Use `"string"` for logical judgments that are expressed as strings.
                - Use `"number"` for numerical parameters.
            - Lists or arrays are not allowed. If multiple values are needed, represent them as separate parameters.

            4. The number of parameters in the `properties` dictionary must exactly match the number and unit of formal parameters in the function.

            5. Output exactly two Python code blocks separated by a single newline (`\n`):
            - The first block contains the Python function code.
            - The second block contains the `properties` dictionary.

            Ensure all parameter descriptions follow the above rules precisely.
            """,
        "checker": """You are a code logic inspection expert. You need to perform two types of checks based on the code and parameters generated by the coder:a. Use natural language to logically inspect the function (verify whether the units and logic described in the parameter descriptions are correct).b. Check whether the function has syntax errors (such as mismatched parameter types or invalid function names).If error a occurs, return it to the analyst for re-analysis. If error b occurs, correct it yourself and recheck. output the two parts' correctness or error reason.If there are no issues, strictly output two Python code blocks:The first block is the Python function code.The second block is the properties dictionary.Separate the two blocks with a line containing \n.Finally, output APPROVE."""
    },
    "indicator": {
        "analyst": """你是一位医学领域的分析专家。你的任务是用“链式思维法（Chain-of-Thought, CoT）”分析一个医疗质量控制问题。请分解解决该问题的详细过程，包括所需的事实变量，并推导出解题过程中涉及的所有逻辑判断公式。最后，列出这些公式中的所有变量、每个变量的含义。判断类则不需要变量单位。严格按照给出的逻辑表达式来生成，并且对变量的说明要尽可能详细，便于抽取正确的事实。

            请按如下步骤操作：
            1. 仔细阅读医疗质量控制问题。
            2. 分析解决该问题所需的各个步骤，包括需要如何进行计算。
            3. 列出涉及的全部变量，并为每个变量提供清晰的说明和单位。

            首先，在<analysis>标签中详细描述逐步的解题过程。  
            然后，在<formulas>标签中列出所有必要的逻辑判断公式。  
            最后，在<variables>标签中以表格形式列出每个变量的名称、含义及单位。（判断类则不需要变量单位）

            <analysis>
            【在这里详细描述逐步解题过程】
            </analysis>
            <formulas>
            【在这里列出所有必要的逻辑判断】
            </formulas>
            <variables>
            | 变量 | 说明 |
            | --- | --- | 
            | 【变量1名称】 | 【变量1说明】|
            | 【变量2名称】 | 【变量2说明】|
            | ... | ... | 
            </variables>
""",
        "coder": """你是一位熟悉医学领域的编程专家。请根据用户给出的分析得到的逻辑、逻辑判断公式及变量，编写一个“Python函数”和一个 `properties` 字典，用于计算指定问题。多事实判断请拆分成多个需要抽取的项，并定义为多个独立参数。

            具体要求如下：

            1. 函数的参数必须表达为实际的逻辑判断值或数值参数。Python函数应当为检查结果，最后函数的返回值为True或False，表示这个病历是否符合了这个指标的检查要求。因病历中可能抽取不到对应的内容或数值，请不要编造，在函数中添加none值的正确逻辑处理。

            2. 提供一个包含该函数所有参数的 `properties` 字典。

            3. `properties` 字典中每个参数都必须包括：
            - `description`：
                - 对于布尔判断型参数，描述中必须明确该参数返回True或False的含义。
                - 对于数值型参数，描述必须为：“<数值具体含义> + 单位：” 的格式。
                - 对于字符串判断型参数，描述中必须明确该参数返回一个表示逻辑判断的字符串。
            - `type`，必须为 "boolean"、"string" 或 "number" 之一。
                - 表示真/假判断的参数用 `"boolean"`。
                - 表示逻辑判断字符串的参数用 `"string"`。
                - 数值型参数用 `"number"`。
            - 不允许列表或数组List。如需多个值，请定义为多个独立参数。

            4. `properties` 字典中的参数数量、名称及单位必须与函数参数严格一致。

            5. 输出格式为**两个Python代码块**，中间用**一个换行符（`\n`）**隔开：
            - 第一段代码为Python函数代码。
            - 第二段代码为`properties`字典。

            请确保所有参数的描述完全符合上述规范。
""",
        "checker": """你是一名代码逻辑检查专家。请针对coder生成的代码和参数，进行以下两类检查：

            a. 用自然语言逻辑检查函数（包括参数描述中涉及的单位和逻辑是否正确，是否和函数实现一致）；
            b. 检查函数是否存在语法错误（如参数类型不匹配、函数名非法等）。

            - 如果出现a类错误，请将其返回给analyst重新分析。
            - 如果出现b类错误，请你自行修正后重新检查。

            输出这两部分的正确性或报错原因。

            如无任何问题，**严格按如下格式**输出两个Python代码块：
            - 第一段代码为Python函数代码。
            - 第二段代码为properties字典。
            - properties字典中，number类型的参数的description中，必须有"单位："。用于正则抽取单位
            两段代码之间用仅包含`\n`的一行隔开。

            最后输出：APPROVE"""
    }
}


# --- 数据加载函数 ---

def read_unique_calculators(csv_filename: str) -> List[Dict[str, Any]]:
    """从CSV文件中读取唯一的计算器信息，并筛选Output Type为decimal。"""
    unique_calculators = []
    seen_calculator_ids = set()

    with open(csv_filename, mode='r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            calculator_id = row.get('Calculator ID')
            output_type = row.get('Output Type', '').strip().lower()
            if calculator_id and calculator_id not in seen_calculator_ids and output_type == 'decimal':
                seen_calculator_ids.add(calculator_id)
                unique_calculators.append(row)
    
    return unique_calculators


def load_medcalc_tasks(file_path: str) -> Optional[Dict[str, Any]]:
    """从CSV文件加载 'medcalc' 任务，只保留Output Type为decimal的任务。"""
    try:
            # 加载 one_shot_finalized_explanation.json
        with open("baseline_medcalc/one_shot_finalized_explanation.json", "r", encoding="utf-8") as f:
            explanation_dict = json.load(f)
        tasks, id_list = [], []
        calculators = read_unique_calculators(file_path)
        for item in calculators:
            #根据需要筛选ID
            # if int(item['Calculator ID']) not in [9, 59]  :
            #     continue
            calc_id = str(item['Calculator ID'])
            id_list.append(int(item['Calculator ID']))
            # 拼接到 prompt
            task_string = (
                f"calculator name is:{item['Calculator Name']},\n"
                f"question is:{item['Question']}.\n"
                f"strictly use the formula to solve the question, but dont use list as parameters for the function, change list to multiple parameters:\n"
            )
            tasks.append(task_string)
        
        return {"tasks": tasks, "id_list": id_list}
    except FileNotFoundError:
        print(f"Error: MedCalc file not found at {file_path}")
    except Exception as e:
        print(f"An error occurred while loading MedCalc tasks: {e}")
    return None


def load_indicator_tasks(file_path: str) -> Optional[Dict[str, Any]]:
    """从JSON文件加载 'indicator' 任务。"""
    # 直接在代码中定义允许的指标名称列表
    valid_names = []
    jsonl_path = "data.jsonl"
    unique_id2record = {}
    with open(jsonl_path, 'r', encoding='utf-8') as fd:
        for line in fd:
            item = json.loads(line)
            unique_id = item.get("unique_id")
            if unique_id not in unique_id2record.keys():
                unique_id2record[unique_id] = item
                continue  # 用unique_id做key，整条item做value

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            indicators_data = json.load(f)
        tasks = []
        names = []
        # 2. 在遍历 indicators_data.items() 时，查找对应的 example
        for name, details in indicators_data.items():
            # if name not in valid_names:
            #     continue
            print(name)
            rule = details.get("question_rule")
            fact = details.get("facts")
            logic_rule = details.get("logical_rules")

            # 获取 example
            example_record = unique_id2record.get(name, None)
            if example_record:
                example_str = f"\nexample: {json.dumps(example_record, ensure_ascii=False)}"
            else:
                example_str = "\nexample: 无"

            if rule:
                #processed_name = name.replace("率", "").replace("比例", "")
                tasks.append(
                    f"医疗指标问题为：{rule}, 涉及的事实有：{fact}, 检查涉及的判断逻辑是：{logic_rule}，"
                )
                names.append(name)
            else:
                print(f"Warning: 'question_rule' not found for indicator: {name}")

        # 这里改为直接返回name列表
        return {"tasks": tasks, "id_list": names} #list(indicators_data.keys())
    except FileNotFoundError:
        print(f"Error: Indicator file not found at {file_path}")
    except json.JSONDecodeError:
        print(f"Error: Could not decode JSON from {file_path}")
    except Exception as e:
        print(f"An error occurred while loading indicator tasks: {e}")
    return None

# --- Agent和团队设置 ---

def setup_agents(model_client: OpenAIChatCompletionClient, messages: Dict[str, str]) -> List[AssistantAgent]:
    """创建并配置Agents。"""
    analyst = AssistantAgent("Analyst", model_client=model_client, system_message=messages["analyst"])
    coder = AssistantAgent("Coder", model_client=model_client, system_message=messages["coder"])
    checker = AssistantAgent("Checker", model_client=model_client, system_message=messages["checker"])
    return [analyst, coder, checker]#


def refactor_properties_string(properties_string: str) -> Dict[str, Any]:
    """
    解析一个包含properties字典的字符串，重构带有单位的 'number' 类型，
    并提取 'need_unit' 字典。
    """
    need_unit_dict = {}

    # 优先匹配 "properties = { ... }" 格式，兼容多行
    match = re.search(r'properties\s*=\s*(\{.*\})', properties_string, re.DOTALL)
    if match:
        dict_str = match.group(1)
    else:
        # 如果没有，则直接寻找被大括号包裹的内容
        match = re.search(r'(\{.*\})', properties_string, re.DOTALL)
        dict_str = match.group(1) if match else properties_string

    try:
        # 使用 ast.literal_eval 安全地将字符串解析为 Python 字典
        properties_dict = ast.literal_eval(dict_str)
        if not isinstance(properties_dict, dict):
             raise ValueError("Parsed object is not a dictionary.")
    except (ValueError, SyntaxError) as e:
        print(f"Warning: ast.literal_eval failed ('{e}'). Falling back to raw string.")
        # 如果解析失败，返回原始字符串和空的 need_unit
        return {"properties_row": properties_string, "need_unit": {}}

    # 遍历字典，重构包含单位的 'number' 类型的属性
    for key, value in properties_dict.items():
        desc = value.get("description", "") if isinstance(value, dict) else ""
        unit = ""
        main_desc = desc
        # 英文 in ...
        if isinstance(value, dict) and value.get("type") == "number" and " in " in desc:
            m = re.search(r'(.+?) in (.+)', desc)
            if m:
                main_desc = m.group(1).strip()
                unit = m.group(2).split(',')[0].strip()
        # 中文“单位:”
        elif isinstance(value, dict) and value.get("type") == "number" and "单位:" or "单位：" in desc:
            m = re.search(r'(.+?)单位[:：]\s*([^，。；;\s]+)', desc)
            if m:
                main_desc = m.group(1).strip()
                unit = m.group(2).strip()
        # 记录需要单位转换的键和目标单位
        if unit:
            need_unit_dict[key] = unit
            # 构建新的、更详细的 'array' 结构来替代原来的 'number' 结构
            properties_dict[key] = {
                "type": "array",
                "description": main_desc,  # 去除单位部分
                "items": {
                    "type": "object",
                    "properties": {
                        "value": {"type": "number", "description": main_desc},
                        "unit": {"type": "string", "description": "exactly unit extracted from EMR."}
                    },
                    "required": ["value", "unit"]
                }
            }
    # 将修改后的字典转换回格式化的字符串
    new_row_str = f"properties = {json.dumps(properties_dict, ensure_ascii=False, indent=4)}"
    
    return {"properties_row": new_row_str, "need_unit": need_unit_dict}


# --- 结果处理函数 ---

def save_result(data: Dict[str, Any], output_file: str):
    """将单次任务的结果以JSONL格式追加到文件。"""
    try:
        with open(output_file, 'a', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False)
            f.write('\n')
    except Exception as e:
        print(f"Error writing result to {output_file}: {e}")

# --- 主流程 ---

async def main():
    """主执行函数"""
    # 1. 加载配置
    cfg = TASK_CONFIG
    task_type = cfg["task_type"]
    model_name = cfg["selected_model"]
    model_details = MODEL_CONFIGS[model_name]
    # 2. 加载任务
    if task_type == "medcalc":
        task_data = load_medcalc_tasks(cfg["medcalc_file"])
    elif task_type == "indicator":
        task_data = load_indicator_tasks(cfg["indicator_file"])
    else:
        print(f"Error: Unknown task type '{task_type}'")
        return

    if not task_data or not task_data.get("tasks"):
        print("Failed to load tasks. Exiting.")
        return
        
    tasks = task_data["tasks"]
    id_list = task_data["id_list"]

    print(f"Successfully loaded {len(tasks)} tasks for type '{task_type}'.")

    # 3. 设置模型和Agents
    model_client = OpenAIChatCompletionClient(**model_details)
    agent_messages = SYSTEM_MESSAGES[task_type]
    agents = setup_agents(model_client, agent_messages)
    
    # 4. 创建团队
    team = RoundRobinGroupChat(agents, termination_condition=TextMentionTermination("APPROVE"))
    
    # 5. 循环处理任务
    output_filename = cfg["output_file_template"].format(task_type=task_type, model_name=model_name)
    all_logs = []
    
    for i, task_description in enumerate(tasks):
        print(f"\n--- Processing Task {i+1}/{len(tasks)} (ID: {id_list[i]}) ---")
        print(f"Task: {task_description}")
        time.sleep(5)
        task_result_data = {
            "task_index": id_list[i],
            "task_description": task_description
        }
        
        try:
            # 运行Agent团队
            result = await team.run(task=task_description, cancellation_token=CancellationToken())
            print(result.messages)
            # 收集日志
            agent_logs = [{"role": msg.source, "content": msg.content} for msg in result.messages] if result.messages else []
            all_logs.append({"task_index": id_list[i], "task_description": task_description, "agent_logs": agent_logs})

            # 解析和重构结果
            checker_message = ""
            if result and result.messages:
                final_checker_msg = next((msg for msg in reversed(result.messages) if msg.source == "Checker" and "APPROVE" in msg.content), None)
                if final_checker_msg:
                    checker_message = final_checker_msg.content

            # 直接从 checker_message 中解析和重构
            code_blocks = re.findall(r"```python\s*(.*?)\s*```", checker_message, re.DOTALL)#r"```python\n(.*?)\n```"
            
            if len(code_blocks) >= 2:
                python_code = code_blocks[0].strip()
                properties_original_str = code_blocks[1].strip()
                
                # 调用新函数进行重构
                refactor_result = refactor_properties_string(properties_original_str)

                # 更新任务结果
                task_result_data["python_code"] = python_code
                task_result_data["properties"] = {"row": refactor_result["properties_row"]}
                task_result_data["need_unit"] = refactor_result["need_unit"]

            else:
                # 如果代码块不满足要求，记录错误
                error_msg = "Could not find two python code blocks in checker's response."
                print(f"Warning: {error_msg}")
                task_result_data["python_code"] = ""
                task_result_data["properties"] = {"error": error_msg}
                task_result_data["need_unit"] = {}

        except Exception as e:
            print(f"An error occurred while processing task {id_list[i]}: {e}")
            task_result_data.update({"error": str(e), "python_code": "", "properties": {}, "need_unit": {}})
        
        # 保存当次结果
        save_result(task_result_data, output_filename)
        print(f"--- Task {i+1} Result Saved to {output_filename} ---")
        
        # 可选：任务间延迟
        time.sleep(1) 

    # 6. 保存所有日志
    try:
        with open(cfg["log_file"], "w", encoding="utf-8") as f:
            json.dump(all_logs, f, ensure_ascii=False, indent=2)
        print(f"\nAll agent interaction logs saved to {cfg['log_file']}")
    except Exception as e:
        print(f"Error saving all logs: {e}")

    print(f"\nProcessing complete. All results appended to {output_filename}")


if __name__ == "__main__":
    asyncio.run(main()) 