"""
函数执行模块
"""

import json
import re
import logging
from typing import Dict, Any, List, Callable
from core.llm_client import LLMClient
from core.utils import append_result_to_jsonl

logger = logging.getLogger(__name__)

class FunctionExecutor:
    """函数执行器类"""
    
    def __init__(self, llm_client: LLMClient):
        """初始化函数执行器"""
        self.llm_client = llm_client
    
    def execute_task(self, task: Dict[str, Any], patient_notes: List[str]) -> List[Dict]:
        """处理单个任务对患者病历列表"""
        function_code = task.get("python_code")
        properties_raw = task.get("properties", {}).get("row", "")

        if not function_code or not properties_raw:
            logger.warning(f"Skipping Task ID {task.get('task_index')} due to missing code or properties.")
            return []

        try:
            properties_str = re.sub(r"properties\s*=\s*", "", properties_raw)
            properties = json.loads(properties_str)
        except json.JSONDecodeError:
            logger.error(f"Error decoding properties for Task ID {task.get('task_index')}.")
            return []

        namespace = {}
        try:
            exec(function_code, namespace)
            func_name = next((name for name, obj in namespace.items() if callable(obj)), None)
            if not func_name:
                logger.error(f"No callable function found for Task ID {task.get('task_index')}.")
                return []
            generated_func = namespace[func_name]
        except Exception as e:
            logger.error(f"Error executing function code for Task ID {task.get('task_index')}: {e}")
            return []
            
        results = []
        need_unit = {k: re.sub(r'[:：\s]', '', v) for k, v in task.get("need_unit", {}).items()}

        for i, note in enumerate(patient_notes):
            logger.info(f"  - Processing patient note {i+1}/{len(patient_notes)}...")
            extracted_params = self.llm_client.extract_parameters(properties, note, need_unit)
            if not extracted_params:
                logger.warning("    ...failed to extract parameters, skipping execution.")
                continue
            try:
                result_val = generated_func(**extracted_params)
                results.append({'extract_para': extracted_params, 'result': result_val})
            except Exception as e:
                logger.error(f"    ...error calling generated function: {e}")
                results.append({'extract_para': extracted_params, 'error': str(e)})

        return results
    
    def execute_single_task(self, task: Dict[str, Any], patient_note: str) -> Dict[str, Any]:
        """执行单个任务对单个患者病历"""
        function_code = task.get("python_code")
        properties_raw = task.get("properties", {}).get("row", "")

        if not function_code or not properties_raw:
            return {"error": "Missing code or properties"}

        try:
            properties_str = re.sub(r"properties\s*=\s*", "", properties_raw)
            properties = json.loads(properties_str)
        except json.JSONDecodeError:
            return {"error": "Invalid properties format"}

        namespace = {}
        try:
            exec(function_code, namespace)
            func_name = next((name for name, obj in namespace.items() if callable(obj)), None)
            if not func_name:
                return {"error": "No callable function found"}
            generated_func = namespace[func_name]
        except Exception as e:
            return {"error": f"Function execution error: {e}"}
            
        need_unit = {k: re.sub(r'[:：\s]', '', v) for k, v in task.get("need_unit", {}).items()}
        
        extracted_params = self.llm_client.extract_parameters(properties, patient_note, need_unit)
        if not extracted_params:
            return {"error": "Failed to extract parameters"}
            
        try:
            result_val = generated_func(**extracted_params)
            return {
                'extract_para': extracted_params, 
                'result': result_val,
                'success': True
            }
        except Exception as e:
            return {
                'extract_para': extracted_params, 
                'error': str(e),
                'success': False
            }
    
    def save_results(self, task_id: str, results: List[Dict], output_file: str):
        """保存结果到输出文件"""
        if results:
            final_output = {"id": task_id, "results": results}
            append_result_to_jsonl(output_file, final_output)
            logger.info(f"Results for Task ID {task_id} saved to {output_file}") 