"""
函数执行器模块
"""

import json
import re
from typing import Dict, Any, List, Optional

from config import TaskConfig, PathConfig
from core import LLMClient, DataProcessor, BaseProcessor
from .parameter_extractor import ParameterExtractor


class FunctionExecutor(BaseProcessor):
    """函数执行器类"""
    
    def __init__(self, model_name: str, task_type: str, **kwargs):
        super().__init__(model_name, task_type, **kwargs)
        
        # 初始化组件
        self.llm_client = LLMClient(model_name, task_type, **kwargs)
        self.data_processor = DataProcessor(model_name, task_type, **kwargs)
        self.parameter_extractor = ParameterExtractor(self.llm_client)
        
        # 获取配置
        self.execution_config = TaskConfig.get_execution_config(task_type)
    
    def execute_task(self, task: Dict[str, Any], patient_notes: List[str]) -> List[Dict[str, Any]]:
        """执行单个任务"""
        function_code = task.get("python_code")
        properties_raw = task.get("properties", {}).get("row", "")
        
        if not function_code or not properties_raw:
            self.log_warning(f"任务缺少函数代码或属性定义")
            return []
        
        try:
            # 解析属性
            properties_str = re.sub(r"properties\s*=\s*", "", properties_raw)
            properties = json.loads(properties_str)
        except json.JSONDecodeError:
            self.log_error(f"属性解析失败")
            return []
        
        # 执行函数
        namespace = {}
        try:
            exec(function_code, namespace)
            func_name = next((name for name, obj in namespace.items() if callable(obj)), None)
            if not func_name:
                self.log_error(f"未找到可调用的函数")
                return []
            generated_func = namespace[func_name]
        except Exception as e:
            self.log_error(f"函数代码执行失败: {e}")
            return []
        
        # 获取单位信息
        need_unit = {k: re.sub(r'[:：\s]', '', v) for k, v in task.get("need_unit", {}).items()}
        
        results = []
        for i, note in enumerate(patient_notes):
            self.log_info(f"处理第 {i+1}/{len(patient_notes)} 个病历...")
            
            try:
                # 提取参数
                extracted_params = self.parameter_extractor.extract_parameters_with_units(
                    properties, note, need_unit
                )
                
                if not extracted_params:
                    self.log_warning("参数提取失败，跳过执行")
                    continue
                
                # 执行函数
                result_val = generated_func(**extracted_params)
                results.append({
                    'extract_para': extracted_params, 
                    'result': result_val
                })
                
            except Exception as e:
                self.log_error(f"函数调用失败: {e}")
                results.append({
                    'extract_para': extracted_params if 'extracted_params' in locals() else {},
                    'error': str(e)
                })
        
        return results
    
    def load_generated_functions(self, file_path: Optional[str] = None) -> List[Dict[str, Any]]:
        """加载生成的函数"""
        if file_path is None:
            file_path = self.execution_config["generated_functions_file"]
        
        return self.data_processor.load_generated_functions(file_path)
    
    def load_patient_data(self, file_path: Optional[str] = None) -> Dict[str, List[str]]:
        """加载患者数据"""
        if file_path is None:
            file_path = self.task_config["patient_data_file"]
        
        return self.data_processor.load_patient_data(file_path)
    
    def process(self, include_ids: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        """处理主逻辑"""
        # 加载生成的函数
        all_tasks = self.load_generated_functions()
        if not all_tasks:
            self.log_error("无法加载生成的函数")
            return []
        
        # 加载患者数据
        patient_data_map = self.load_patient_data()
        if not patient_data_map:
            self.log_error("无法加载患者数据")
            return []
        
        all_results = []
        
        # 处理每个任务
        for task in all_tasks:
            task_id = str(task.get('task_index', 'unknown'))
            
            # 过滤特定ID
            if include_ids and task_id not in include_ids:
                continue
            
            self.log_info(f"处理任务 ID: {task_id}")
            
            patient_notes = patient_data_map.get(task_id)
            if not patient_notes:
                self.log_warning(f"未找到ID {task_id} 的患者数据，跳过")
                continue
            
            # 执行任务
            task_results = self.execute_task(task, patient_notes)
            
            # 保存结果
            if task_results:
                final_output = {"id": task_id, "results": task_results}
                output_file = self.execution_config["results_output_file"]
                self.data_processor.save_result(final_output, output_file)
                all_results.append(final_output)
                
                self.log_info(f"任务 {task_id} 的结果已保存")
        
        return all_results
    
    def run(self, include_ids: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        """运行函数执行器"""
        self.log_info("开始执行函数执行器")
        
        try:
            results = self.process(include_ids)
            self.log_info(f"执行完成，共处理 {len(results)} 个任务")
            return results
        except Exception as e:
            self.log_error(f"执行失败: {e}", exc_info=True)
            raise 