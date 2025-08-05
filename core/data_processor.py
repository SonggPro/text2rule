"""
数据处理器模块
"""

import json
import csv
import os
from typing import Dict, Any, List, Optional
import ast
import re

from config import TaskConfig, PathConfig
from .base import BaseProcessor


class DataProcessor(BaseProcessor):
    """数据处理器类"""
    
    def __init__(self, model_name: str, task_type: str, **kwargs):
        super().__init__(model_name, task_type, **kwargs)
    
    def load_generated_functions(self, file_path: Optional[str] = None) -> List[Dict[str, Any]]:
        """加载生成的函数"""
        if file_path is None:
            file_path = PathConfig.get_output_file_path(self.task_type, self.model_name, "generated_functions")
        
        return self._load_jsonl_file(file_path)
    
    def load_patient_data(self, file_path: Optional[str] = None) -> Dict[str, List[str]]:
        """加载患者数据"""
        if file_path is None:
            file_path = self.task_config["patient_data_file"]
        
        data = {}
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                for line in file:
                    try:
                        record = json.loads(line.strip())
                        patient_id = str(record.get(self.task_config["patient_id_key"]))
                        note = record.get(self.task_config["patient_note_key"])
                        if patient_id and note:
                            if patient_id not in data:
                                data[patient_id] = []
                            data[patient_id].append(note)
                    except (json.JSONDecodeError, AttributeError):
                        continue
        except FileNotFoundError:
            self.log_error(f"患者数据文件未找到: {file_path}")
        
        self.log_info(f"加载了 {len(data)} 个患者的数据")
        return data
    
    def _load_jsonl_file(self, file_path: str) -> List[Dict[str, Any]]:
        """加载JSONL文件"""
        data = []
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                for line in f:
                    if line.strip():
                        data.append(json.loads(line))
        except FileNotFoundError:
            self.log_error(f"文件未找到: {file_path}")
        except json.JSONDecodeError as e:
            self.log_error(f"JSON解析错误: {e}")
        
        return data
    
    def save_result(self, data: Dict[str, Any], file_path: str):
        """保存结果到JSONL文件"""
        try:
            with open(file_path, "a", encoding="utf-8") as file:
                json.dump(data, file, ensure_ascii=False)
                file.write('\n')
            self.log_info(f"结果已保存到: {file_path}")
        except Exception as e:
            self.log_error(f"保存结果失败: {e}", exc_info=True)
    
    def process(self, *args, **kwargs) -> Any:
        """实现抽象方法"""
        pass 