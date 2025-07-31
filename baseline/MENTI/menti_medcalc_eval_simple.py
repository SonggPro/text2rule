#!/usr/bin/env python3
"""
优化的MENTI MedCalc-Bench评估脚本
性能优化：缓存embedding、简化流程、并行处理
"""

import re
import os
import json
import tqdm
import argparse
import pandas as pd
import sys
import numpy as np
from typing import List, Dict, Any
from openai import OpenAI
from concurrent.futures import ThreadPoolExecutor, as_completed
import time

# 添加当前目录到路径
sys.path.append('.')


class SimpleLLM:
    """简化的LLM类，只使用OpenAI API"""
    
    def __init__(self, model: str = 'gpt-4o-mini'):
        self.model = model
        self.client = OpenAI()
    
    def generate(self, input_text: str) -> str:
        """生成回答"""
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": input_text}]
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"API调用错误: {e}")
            return f"ERROR: {str(e)}"


class SimpleEmbedding:
    """优化的Embedding类，支持缓存"""
    
    def __init__(self, model: str = 'openai'):
        self.client = OpenAI()
        self.cache = {}  # 简单的内存缓存
    
    def encode(self, texts, **kwargs):
        """生成embedding，支持缓存"""
        if isinstance(texts, str):
            texts = [texts]
        
        # 检查缓存
        uncached_texts = []
        uncached_indices = []
        cached_embeddings = []
        
        for i, text in enumerate(texts):
            if text in self.cache:
                cached_embeddings.append(self.cache[text])
            else:
                uncached_texts.append(text)
                uncached_indices.append(i)
        
        # 批量获取未缓存的embeddings
        if uncached_texts:
            try:
                response = self.client.embeddings.create(
                    model="text-embedding-3-small",
                    input=uncached_texts
                )
                
                # 更新缓存
                for i, embedding in enumerate(response.data):
                    text = uncached_texts[i]
                    self.cache[text] = embedding.embedding
                    cached_embeddings.append(embedding.embedding)
                    
            except Exception as e:
                print(f"Embedding API错误: {e}")
                # 返回随机embedding作为fallback
                import random
                for text in uncached_texts:
                    random_embedding = [random.random() for _ in range(1536)]
                    self.cache[text] = random_embedding
                    cached_embeddings.append(random_embedding)
        
        # 重新排序结果
        result = [None] * len(texts)
        for i, embedding in enumerate(cached_embeddings):
            if i < len(uncached_indices):
                result[uncached_indices[i]] = embedding
            else:
                # 从缓存中获取
                for j, text in enumerate(texts):
                    if text in self.cache and result[j] is None:
                        result[j] = self.cache[text]
        
        if len(texts) == 1:
            return result[0]
        return result


class SimplePrompts:
    """简化的提示类"""
    
    def __init__(self):
        self.preliminary_diagnosis_prompt = """请对以下患者记录进行初步分析，提取关键信息：

患者记录：
{patient_note}

请分析：
1. 患者的主要症状和体征
2. 相关的实验室检查结果
3. 需要计算的关键参数
4. 可能的诊断方向

请用简洁的语言总结："""

        self.metatool_classify_prompt = '''You are a toolkit selection model. Below is a toolkit list and their descriptions, and you need to select the appropriate toolkit based on the user query. Your answer should be wrapped by ```json and ```

toolkit list: ["unit", "scale"]
"unit": This is a unit toolkit that contains a variety of medical unit conversion tools. When you need to perform unit conversions, you will need to select this tookit.
"scale": This is a medical calculator toolkit, which is used for assessing and quantifying specific health conditions of individuals in the medical field. When you need to analyze a patient's health condition, or when a user has made a query regarding health status, you will need to select this toolkit.

Requirements:
1. You can only select one toolkit, and it must be from the toolkit list provided.
2. You need to output a JSON file.
3. Your answer should be wrapped by ```json and ```

Please follow this output format:
```json
{
    "chosen_toolkit_name": "toolkit you choose"
}
```

Begin!

user query: INSERT_QUERY_HERE'''

        self.metatool_dispatch_prompt = '''You are a dispatching model. Your task is to choose the most suitable tool from the tool list based on User Demand and the Task Scenario, which will then be provided to the user for use.

Tool List: INSERT_TOOLLIST_HERE
Detailed information of each tool: INSERT_TOOLINST_HERE

Requirements:
1. You need to conduct a detailed, step-by-step analysis.
2. You must choose a tool from the Tool List.
3. The Final Answer is a JSON file, and the JSON file must be wrapped by ```json and ```
4. The tool you choose in the JSON file must be one of the items in the Tool List.

Here is a example of the Final Answer:
```json
{
    "chosen_tool_name": "the tool you choose"
}
```

Begin!

User Demand: INSERT_DEMAND_HERE
Task Scenario: INSERT_SCE_HERE
Step By Step Analysis:'''


class OptimizedMetaTool:
    """优化的MetaTool类，减少API调用"""
    
    def __init__(self, query: str, scenario: str = ""):
        self.query = query
        self.scenario = scenario
        self.llm = SimpleLLM()
        self.embedding = SimpleEmbedding()
        self.prompts = SimplePrompts()
        
        # 加载工具定义和预计算embedding
        self.load_tools()
        self.precompute_tool_embeddings()
    
    def load_tools(self):
        """加载工具定义"""
        try:
            with open("./CalcQA/tool_scale.json", "r", encoding="utf-8") as f:
                self.scale_tools = json.load(f)
            with open("./CalcQA/tool_unit.json", "r", encoding="utf-8") as f:
                self.unit_tools = json.load(f)
        except FileNotFoundError:
            print("警告：找不到工具定义文件，使用默认工具")
            self.scale_tools = []
            self.unit_tools = []
    
    def precompute_tool_embeddings(self):
        """预计算所有工具的embedding"""
        print("预计算工具embedding...")
        
        # 预计算scale工具embedding
        if self.scale_tools:
            scale_descriptions = []
            for tool in self.scale_tools:
                desc = f"{tool['function_name']}\n\n{tool['tool_name']}\n\n{tool['docstring']}"
                scale_descriptions.append(desc)
            self.scale_embeddings = self.embedding.encode(scale_descriptions)
        
        # 预计算unit工具embedding
        if self.unit_tools:
            unit_descriptions = []
            for tool in self.unit_tools:
                desc = f"{tool['function_name']}\n\n{tool['tool_name']}\n\n{tool['docstring']}"
                unit_descriptions.append(desc)
            self.unit_embeddings = self.embedding.encode(unit_descriptions)
        
        print("工具embedding预计算完成")
    
    def classify(self) -> str:
        """1. 工具分类 - 选择工具包（scale/unit）"""
        classify_prompt = self.prompts.metatool_classify_prompt.replace("INSERT_QUERY_HERE", self.query)
        
        try:
            response = self.llm.generate(classify_prompt)
            json_match = re.findall(r'```json(.*?)```', response, flags=re.DOTALL)
            if json_match:
                result = json.loads(json_match[0].strip())
                return result.get("chosen_toolkit_name", "scale")
        except:
            pass
        
        return "scale"  # 默认返回scale
    
    def retrieve(self, toolkit: str) -> List[int]:
        """2. 工具检索 - 使用预计算的embedding"""
        if toolkit == "scale":
            tools = self.scale_tools
            tool_embeddings = getattr(self, 'scale_embeddings', [])
        else:
            tools = self.unit_tools
            tool_embeddings = getattr(self, 'unit_embeddings', [])
        
        if not tools or not tool_embeddings:
            return []
        
        # 计算查询与工具的相似度
        query_embedding = self.embedding.encode(self.query)
        scores = []
        
        for tool_embedding in tool_embeddings:
            similarity = self.cosine_similarity(query_embedding, tool_embedding)
            scores.append(similarity)
        
        # 返回排序后的索引
        ranked_indices = np.argsort(scores)[::-1]
        return ranked_indices.tolist()
    
    def cosine_similarity(self, embed_a, embed_b):
        """计算余弦相似度"""
        dot_product = np.dot(embed_a, embed_b)
        cosine = dot_product / (np.linalg.norm(embed_a) * np.linalg.norm(embed_b))
        return cosine
    
    def dispatch(self, toolkit: str, top_indices: List[int]) -> tuple[int, str]:
        """3. 工具分发 - 从检索结果中选择最合适的工具"""
        if toolkit == "scale":
            tools = self.scale_tools
        else:
            tools = self.unit_tools
        
        if not tools or not top_indices:
            return 0, "general_calculator"
        
        # 构建候选工具列表
        candidate_tools = []
        candidate_descriptions = ""
        
        for i in top_indices[:5]:  # 取前5个候选
            if i < len(tools):
                tool = tools[i]
                candidate_tools.append(tool["tool_name"])
                candidate_descriptions += f"{tool['tool_name']}: {tool['docstring']}\n\n"
        
        if not candidate_tools:
            return 0, tools[0]["tool_name"] if tools else "general_calculator"
        
        # 使用LLM选择最合适的工具
        dispatch_prompt = self.prompts.metatool_dispatch_prompt.replace(
            'INSERT_TOOLLIST_HERE', str(candidate_tools)
        ).replace(
            'INSERT_TOOLINST_HERE', candidate_descriptions
        ).replace(
            'INSERT_DEMAND_HERE', self.query
        ).replace(
            'INSERT_SCE_HERE', self.scenario
        )
        
        try:
            response = self.llm.generate(dispatch_prompt)
            json_match = re.findall(r'```json(.*?)```', response, flags=re.DOTALL)
            if json_match:
                result = json.loads(json_match[0].strip())
                chosen_tool = result.get("chosen_tool_name", "").lower()
                
                # 找到对应的工具索引
                for i in top_indices[:5]:
                    if i < len(tools) and tools[i]["tool_name"].lower() == chosen_tool:
                        return i, tools[i]["tool_name"]
        except:
            pass
        
        # 默认返回第一个候选工具
        first_index = top_indices[0] if top_indices else 0
        if first_index < len(tools):
            return first_index, tools[first_index]["tool_name"]
        return 0, "general_calculator"
    
    def execute(self) -> tuple[str, int, str]:
        """执行优化的MENTI流程"""
        # 1. 工具分类
        toolkit = self.classify()
        
        # 2. 工具检索（使用预计算的embedding）
        ranked_indices = self.retrieve(toolkit)
        
        # 3. 工具分发
        tool_index, tool_name = self.dispatch(toolkit, ranked_indices)
        
        return toolkit, tool_index, tool_name


class SimpleConfiguration:
    """简化的Configuration类，负责参数提取和计算执行"""
    
    def __init__(self, toolkit: str, tool_index: int, patient_note: str = ""):
        self.toolkit = toolkit
        self.tool_index = tool_index
        self.patient_note = patient_note
        self.llm = SimpleLLM()
        
        # 加载工具
        self.load_tools()
    
    def load_tools(self):
        """加载工具定义"""
        try:
            if self.toolkit == "scale":
                with open("./CalcQA/tool_scale.json", "r", encoding="utf-8") as f:
                    self.tools = json.load(f)
            else:
                with open("./CalcQA/tool_unit.json", "r", encoding="utf-8") as f:
                    self.tools = json.load(f)
        except FileNotFoundError:
            self.tools = []
    
    def extract_parameters(self, question: str) -> Dict[str, Any]:
        """参数提取 - 从患者记录中提取计算参数"""
        if self.tool_index >= len(self.tools):
            return {}
        
        tool = self.tools[self.tool_index]
        
        extract_prompt = f"""你是一个医疗计算助手。请从患者记录中提取计算所需的参数。

患者记录：
{self.patient_note}

计算问题：
{question}

选定的工具：{tool["tool_name"]}
工具描述：{tool["description"]}
工具参数说明：{tool["docstring"]}

请仔细分析患者记录，提取计算所需的参数。请按照以下JSON格式回答：
```json
{{
    "extracted_params": {{
        "param1": value1,
        "param2": value2,
        ...
    }},
    "calculation_result": "计算结果",
    "explanation": "计算步骤和解释"
}}
```

注意：
- 确保参数类型正确（int, float, bool等）
- 如果无法提取某些参数，请使用合理的默认值
- 计算结果应该是数值，不包含单位
"""
        
        try:
            response = self.llm.generate(extract_prompt)
            json_match = re.findall(r'```json(.*?)```', response, flags=re.DOTALL)
            if json_match:
                result = json.loads(json_match[0].strip())
                return {
                    "params": result.get("extracted_params", {}),
                    "result": result.get("calculation_result", ""),
                    "explanation": result.get("explanation", "")
                }
        except:
            pass
        
        return {"params": {}, "result": "无法提取参数", "explanation": "参数提取失败"}
    
    def execute(self, question: str) -> tuple[str, str]:
        """计算执行 - 执行选定的工具"""
        result = self.extract_parameters(question)
        return result["result"], result["explanation"]


class MentiMedCalcEvaluator:
    def __init__(self, llm_model: str = 'gpt-4o-mini', embedding_model: str = 'openai'):
        """
        初始化MENTI MedCalc评估器
        """
        self.llm_model_name = llm_model
        self.embedding_model_name = embedding_model
        
        # 初始化模型
        self.llm = SimpleLLM(llm_model)
        self.embedding = SimpleEmbedding(embedding_model)
        self.prompts = SimplePrompts()
        
        # 加载MedCalc-Bench数据集
        self.dataset_path = "./MedCalc-Bench-main/dataset/test_data.csv"
        self.df = pd.read_csv(self.dataset_path)
        
        # 创建输出目录
        os.makedirs("menti_outputs", exist_ok=True)
        
    def filter_by_calculator_ids(self, calculator_ids: List[str]) -> pd.DataFrame:
        """
        根据Calculator ID列表过滤数据集
        """
        calculator_ids = [str(cid) for cid in calculator_ids]
        
        filtered_df = self.df[self.df['Calculator ID'].astype(str).isin(calculator_ids)].copy()
        
        print(f"原始数据集大小: {len(self.df)}")
        print(f"过滤后数据集大小: {len(filtered_df)}")
        print(f"包含的Calculator ID: {sorted(calculator_ids)}")
        
        id_counts = filtered_df['Calculator ID'].value_counts().sort_index()
        print("\n各Calculator ID的实例数量:")
        for cid, count in id_counts.items():
            print(f"  Calculator ID {cid}: {count} 个实例")
        
        return filtered_df
        
    def extract_answer(self, answer: str, calculator_id: int) -> tuple[str, str]:
        """
        从LLM回答中提取答案和解释
        """
        calculator_id = int(calculator_id)
        
        # 尝试提取JSON格式的答案
        extracted_answer = re.findall(r'[Aa]nswer":\s*(.*?)\}', answer)
        matches = re.findall(r'"step_by_step_thinking":\s*"([^"]+)"\s*,\s*"[Aa]nswer"', answer)
        
        if matches:
            explanation = matches[-1]
        else:
            explanation = "No Explanation"
        
        if len(extracted_answer) == 0:
            extracted_answer = "Not Found"
        else:
            extracted_answer = extracted_answer[-1].strip().strip('"')
            if extracted_answer in ["str(short_and_direct_answer_of_the_question)", 
                                  "str(value which is the answer to the question)", 
                                  "X.XX"]:
                extracted_answer = "Not Found"
        
        # 处理特殊格式的答案
        if calculator_id in [13, 68]:  # 日期格式
            match = re.search(r"^(0?[1-9]|1[0-2])\/(0?[1-9]|[12][0-9]|3[01])\/(\d{4})", extracted_answer)
            if match:
                month = int(match.group(1))
                day = int(match.group(2))
                year = match.group(3)
                answer = f"{month:02}/{day:02}/{year}"
            else:
                answer = "N/A"
        elif calculator_id in [69]:  # 周和天格式
            match = re.search(r"\(?[\"\']?(\d+)\s*(weeks?)?[\"\']?,?\s*[\"\']?(\d+)\s*(days?)?[\"\']?\s*\)?", extracted_answer)
            if match:
                weeks = match.group(1)
                days = match.group(3)
                answer = f"({weeks}, {days})"
            else:
                answer = "N/A"
        else:
            answer = extracted_answer
            
        return answer, explanation
    
    def check_correctness(self, answer: str, ground_truth: str, calculator_id: int, 
                         upper_limit: float, lower_limit: float) -> bool:
        """
        检查答案是否正确
        """
        try:
            if answer == "Not Found" or answer == "N/A":
                return False
                
            # 对于数值答案，检查是否在允许范围内
            if isinstance(ground_truth, (int, float)) or str(ground_truth).replace('.', '').replace('-', '').isdigit():
                try:
                    answer_float = float(answer)
                    ground_truth_float = float(ground_truth)
                    return lower_limit <= answer_float <= upper_limit
                except:
                    return str(answer).strip() == str(ground_truth).strip()
            else:
                # 对于非数值答案，直接比较
                return str(answer).strip() == str(ground_truth).strip()
        except:
            return False
    
    def create_final_prompt(self, patient_note: str, question: str, tool_name: str, 
                           tool_result: str, tool_explanation: str) -> str:
        """
        创建最终的计算提示
        """
        prompt = f"""你是一个医疗计算助手。MENTI系统已经为你选择了合适的计算工具并执行了计算。

患者记录：
{patient_note}

计算任务：
{question}

MENTI选择的工具：{tool_name}

工具执行结果：
- 计算结果：{tool_result}
- 计算解释：{tool_explanation}

请基于工具的执行结果，按照以下格式回答：
```json
{{
    "step_by_step_thinking": "你的详细分析步骤，包括对工具结果的解释",
    "answer": "最终的计算结果（使用工具的计算结果，只包含数值，不包含单位）"
}}
```

请确保：
1. 仔细分析工具的执行结果
2. 验证工具计算的合理性
3. 提供清晰的步骤说明
4. 只返回JSON格式的答案
5. 如果工具结果合理，直接使用；如果不合理，请说明原因
"""
        return prompt
    
    def evaluate_single_instance(self, row: pd.Series) -> Dict[str, Any]:
        """
        评估单个实例 - 优化版本
        """
        patient_note = row["Patient Note"]
        question = row["Question"]
        calculator_id = str(row["Calculator ID"])
        note_id = str(row["Note ID"])
        
        try:
            # 1. 初步诊断
            diagnose_result = self.llm.generate(f"{self.prompts.preliminary_diagnosis_prompt}\n\n{patient_note}")
            
            # 2. 使用优化的MetaTool进行工具选择
            metatool = OptimizedMetaTool(question, diagnose_result)
            toolkit, tool_index, tool_name = metatool.execute()
            
            # 3. 使用Configuration进行参数提取和计算
            configuration = SimpleConfiguration(toolkit, tool_index, patient_note)
            tool_result, tool_explanation = configuration.execute(question)
            
            # 4. 生成最终答案
            final_prompt = self.create_final_prompt(patient_note, question, tool_name, tool_result, tool_explanation)
            final_answer = self.llm.generate(final_prompt)
            
            # 5. 提取答案和解释
            answer_value, explanation = self.extract_answer(final_answer, int(calculator_id))
            
            # 6. 检查正确性
            correctness = self.check_correctness(
                answer_value, 
                row["Ground Truth Answer"], 
                calculator_id, 
                row["Upper Limit"], 
                row["Lower Limit"]
            )
            
            status = "Correct" if correctness else "Incorrect"
            
            return {
                "Row Number": int(row["Row Number"]),
                "Calculator Name": row["Calculator Name"],
                "Calculator ID": calculator_id,
                "Category": row["Category"],
                "Note ID": note_id,
                "Patient Note": patient_note,
                "Question": question,
                "LLM Answer": answer_value,
                "LLM Explanation": explanation,
                "Ground Truth Answer": row["Ground Truth Answer"],
                "Ground Truth Explanation": row["Ground Truth Explanation"],
                "Result": status,
                "MENTI Diagnosis": diagnose_result,
                "MENTI Toolkit": toolkit,
                "MENTI Selected Tool": tool_name,
                "MENTI Tool Result": tool_result,
                "MENTI Tool Explanation": tool_explanation,
                "MENTI Final Prompt": final_prompt,
                "MENTI Final Answer": final_answer
            }
            
        except Exception as e:
            return {
                "Row Number": int(row["Row Number"]),
                "Calculator Name": row["Calculator Name"],
                "Calculator ID": calculator_id,
                "Category": row["Category"],
                "Note ID": note_id,
                "Patient Note": patient_note,
                "Question": question,
                "LLM Answer": str(e),
                "LLM Explanation": str(e),
                "Ground Truth Answer": row["Ground Truth Answer"],
                "Ground Truth Explanation": row["Ground Truth Explanation"],
                "Result": "Error",
                "MENTI Diagnosis": "Error",
                "MENTI Toolkit": "Error",
                "MENTI Selected Tool": "Error",
                "MENTI Tool Result": "Error",
                "MENTI Tool Explanation": "Error",
                "MENTI Final Prompt": "Error",
                "MENTI Final Answer": "Error"
            }
    
    def run_evaluation(self, start_index: int = 0, end_index: int = None, 
                      calculator_ids: List[str] = None, parallel: bool = False) -> str:
        """
        运行评估
        """
        # 如果指定了calculator_ids，先过滤数据集
        if calculator_ids:
            self.df = self.filter_by_calculator_ids(calculator_ids)
        
        if end_index is None:
            end_index = len(self.df)
        
        # 生成输出文件名
        if calculator_ids:
            calc_ids_str = "_".join(sorted(calculator_ids))
            output_path = f"menti_outputs/tool_menti_gpt-4o-mini_openai_calcids.jsonl"
        else:
            output_path = f"menti_outputs/tool_menti_gpt-4o-mini_openai_calcids.jsonl"
        
        # 检查是否已有部分结果
        existing_results = set()
        if os.path.exists(output_path):
            with open(output_path, 'r', encoding='utf-8') as f:
                for line in f:
                    try:
                        result = json.loads(line.strip())
                        existing_results.add((result["Calculator ID"], result["Note ID"]))
                    except:
                        continue
        
        print(f"开始评估 {start_index} 到 {end_index} 的实例...")
        print(f"已有结果数量: {len(existing_results)}")
        print(f"并行处理: {parallel}")
        
        start_time = time.time()
        
        if parallel:
            # 并行处理
            with ThreadPoolExecutor(max_workers=3) as executor:
                futures = []
                for index in range(start_index, end_index):
                    row = self.df.iloc[index]
                    calculator_id = str(row["Calculator ID"])
                    note_id = str(row["Note ID"])
                    
                    # 跳过已处理的结果
                    if (calculator_id, note_id) in existing_results:
                        continue
                    
                    future = executor.submit(self.evaluate_single_instance, row)
                    futures.append((index, future))
                
                # 收集结果
                for index, future in tqdm.tqdm(futures, desc="并行评估"):
                    try:
                        result = future.result()
                        with open(output_path, 'a', encoding='utf-8') as f:
                            f.write(json.dumps(result, ensure_ascii=False) + '\n')
                    except Exception as e:
                        print(f"实例 {index} 评估失败: {e}")
        else:
            # 串行处理
            for index in tqdm.tqdm(range(start_index, end_index)):
                row = self.df.iloc[index]
                calculator_id = str(row["Calculator ID"])
                note_id = str(row["Note ID"])
                
                # 跳过已处理的结果
                if (calculator_id, note_id) in existing_results:
                    continue
                
                # 评估单个实例
                result = self.evaluate_single_instance(row)
                
                # 保存结果
                with open(output_path, 'a', encoding='utf-8') as f:
                    f.write(json.dumps(result, ensure_ascii=False) + '\n')
        
        end_time = time.time()
        print(f"评估完成！耗时: {end_time - start_time:.2f}秒")
        print(f"结果保存在: {output_path}")
        return output_path
    
    def compute_statistics(self, output_path: str) -> Dict[str, Any]:
        """
        计算统计结果
        """
        results = []
        with open(output_path, 'r', encoding='utf-8') as f:
            for line in f:
                results.append(json.loads(line.strip()))
        
        # 计算总体准确率
        total = len(results)
        correct = sum(1 for r in results if r["Result"] == "Correct")
        overall_accuracy = correct / total if total > 0 else 0
        
        # 按类别计算准确率
        category_stats = {}
        for result in results:
            category = result["Category"]
            if category not in category_stats:
                category_stats[category] = {"total": 0, "correct": 0}
            category_stats[category]["total"] += 1
            if result["Result"] == "Correct":
                category_stats[category]["correct"] += 1
        
        # 按Calculator ID计算准确率
        calculator_stats = {}
        for result in results:
            calc_id = result["Calculator ID"]
            if calc_id not in calculator_stats:
                calculator_stats[calc_id] = {"total": 0, "correct": 0}
            calculator_stats[calc_id]["total"] += 1
            if result["Result"] == "Correct":
                calculator_stats[calc_id]["correct"] += 1
        
        # 计算每个类别的准确率
        for category in category_stats:
            stats = category_stats[category]
            stats["accuracy"] = stats["correct"] / stats["total"] if stats["total"] > 0 else 0
        
        # 计算每个Calculator ID的准确率
        for calc_id in calculator_stats:
            stats = calculator_stats[calc_id]
            stats["accuracy"] = stats["correct"] / stats["total"] if stats["total"] > 0 else 0
        
        # 保存统计结果
        stats_result = {
            "overall": {
                "total": total,
                "correct": correct,
                "accuracy": overall_accuracy
            },
            "by_category": category_stats,
            "by_calculator_id": calculator_stats
        }
        
        stats_path = output_path.replace('.jsonl', '_stats.json')
        with open(stats_path, 'w', encoding='utf-8') as f:
            json.dump(stats_result, f, ensure_ascii=False, indent=2)
        
        print(f"统计结果保存在: {stats_path}")
        print(f"总体准确率: {overall_accuracy:.4f} ({correct}/{total})")
        
        # 打印Calculator ID级别的统计
        print("\n各Calculator ID的准确率:")
        for calc_id in sorted(calculator_stats.keys(), key=int):
            stats = calculator_stats[calc_id]
            print(f"  Calculator ID {calc_id}: {stats['accuracy']:.4f} ({stats['correct']}/{stats['total']})")
        
        return stats_result


def main():
    parser = argparse.ArgumentParser(description='优化的MENTI MedCalc-Bench评估器')
    parser.add_argument('--llm_model', type=str, default='gpt-4o-mini', 
                       help='LLM模型名称')
    parser.add_argument('--embedding_model', type=str, default='openai',
                       help='Embedding模型名称 (openai)')
    parser.add_argument('--start_index', type=int, default=0,
                       help='开始评估的索引')
    parser.add_argument('--end_index', type=int, default=None,
                       help='结束评估的索引 (None表示到末尾)')
    parser.add_argument('--calculator_ids', type=str, nargs='+',
                       help='指定要评估的Calculator ID列表')
    parser.add_argument('--compute_stats', action='store_true',
                       help='是否计算统计结果')
    parser.add_argument('--parallel', action='store_true',
                       help='是否使用并行处理')
    
    args = parser.parse_args()
    
    # 创建评估器
    evaluator = MentiMedCalcEvaluator(
        llm_model=args.llm_model,
        embedding_model=args.embedding_model
    )
    
    # 运行评估
    output_path = evaluator.run_evaluation(
        start_index=args.start_index, 
        end_index=args.end_index,
        calculator_ids=args.calculator_ids,
        parallel=args.parallel
    )
    
    # 计算统计结果
    if args.compute_stats:
        evaluator.compute_statistics(output_path)


if __name__ == "__main__":
    main() 