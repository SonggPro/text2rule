"""
数据加载模块
"""

import json
import logging
from typing import Dict, Any, List
from core.utils import load_jsonl_file

logger = logging.getLogger(__name__)

class DataLoader:
    """数据加载器类"""
    
    @staticmethod
    def load_generated_functions(file_path: str) -> List[Dict[str, Any]]:
        """从JSONL文件加载任务（代码、属性等）"""
        return load_jsonl_file(file_path)
    
    @staticmethod
    def load_patient_data(file_path: str, id_key: str, note_key: str) -> Dict[str, List[str]]:
        """从文件加载所有患者病历并按ID分组"""
        data = {}
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                for line in file:
                    try:
                        record = json.loads(line.strip())
                        patient_id = str(record.get(id_key))
                        note = record.get(note_key)
                        if patient_id and note:
                            if patient_id not in data:
                                data[patient_id] = []
                            data[patient_id].append(note)
                    except (json.JSONDecodeError, AttributeError):
                        continue
        except FileNotFoundError:
            logger.error(f"Patient data file not found at {file_path}")
        return data
    
    @staticmethod
    def load_task_config(task_type: str) -> Dict[str, Any]:
        """加载任务特定配置"""
        from config.settings import ExecutionConfig
        return ExecutionConfig.TASK_SPECIFIC_CONFIGS.get(task_type, {})
    
    @staticmethod
    def validate_task_data(task: Dict[str, Any]) -> bool:
        """验证任务数据是否有效"""
        required_fields = ["python_code", "properties"]
        for field in required_fields:
            if not task.get(field):
                logger.warning(f"Task missing required field: {field}")
                return False
        return True
    
    @staticmethod
    def filter_tasks_by_ids(tasks: List[Dict[str, Any]], include_ids: List[str]) -> List[Dict[str, Any]]:
        """根据ID过滤任务"""
        if not include_ids:
            return tasks
        
        filtered_tasks = []
        for task in tasks:
            task_id = str(task.get('task_index', ''))
            if task_id in include_ids:
                filtered_tasks.append(task)
        
        logger.info(f"Filtered {len(filtered_tasks)} tasks from {len(tasks)} total tasks")
        return filtered_tasks 