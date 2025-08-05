"""
验证工具模块
"""

import re
from typing import Dict, Any, List, Optional, Union


class Validation:
    """验证工具类"""
    
    @staticmethod
    def validate_model_name(model_name: str) -> bool:
        """验证模型名称"""
        valid_models = ["gpt-4o-mini", "qwen", "claude-sonnet", "gpt-4.1-mini"]
        return model_name in valid_models
    
    @staticmethod
    def validate_task_type(task_type: str) -> bool:
        """验证任务类型"""
        valid_types = ["medcalc", "cmqcic", "indicator"]
        return task_type in valid_types
    
    @staticmethod
    def validate_api_config(config: Dict[str, Any]) -> bool:
        """验证API配置"""
        required_keys = ["api_key", "base_url", "model"]
        return all(key in config and config[key] for key in required_keys)
    
    @staticmethod
    def validate_properties_schema(properties: Dict[str, Any]) -> bool:
        """验证属性模式"""
        for key, value in properties.items():
            if not isinstance(value, dict):
                return False
            
            required_fields = ["type", "description"]
            if not all(field in value for field in required_fields):
                return False
            
            valid_types = ["boolean", "string", "number", "array"]
            if value["type"] not in valid_types:
                return False
        
        return True
    
    @staticmethod
    def validate_function_code(code: str) -> bool:
        """验证函数代码"""
        try:
            compile(code, '<string>', 'exec')
            return True
        except SyntaxError:
            return False
    
    @staticmethod
    def validate_patient_note(note: str) -> bool:
        """验证患者病历"""
        if not isinstance(note, str):
            return False
        if len(note.strip()) == 0:
            return False
        return True
    
    @staticmethod
    def validate_file_path(file_path: str) -> bool:
        """验证文件路径"""
        import os
        return os.path.exists(file_path)
    
    @staticmethod
    def validate_json_structure(data: Dict[str, Any], required_keys: List[str]) -> bool:
        """验证JSON结构"""
        return all(key in data for key in required_keys)
    
    @staticmethod
    def validate_email(email: str) -> bool:
        """验证邮箱格式"""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email))
    
    @staticmethod
    def validate_url(url: str) -> bool:
        """验证URL格式"""
        pattern = r'^https?://(?:[-\w.])+(?:[:\d]+)?(?:/(?:[\w/_.])*(?:\?(?:[\w&=%.])*)?(?:#(?:[\w.])*)?)?$'
        return bool(re.match(pattern, url))
    
    @staticmethod
    def validate_numeric_range(value: Union[int, float], min_val: float, max_val: float) -> bool:
        """验证数值范围"""
        return min_val <= value <= max_val
    
    @staticmethod
    def validate_string_length(text: str, min_length: int = 0, max_length: int = None) -> bool:
        """验证字符串长度"""
        if not isinstance(text, str):
            return False
        if len(text) < min_length:
            return False
        if max_length and len(text) > max_length:
            return False
        return True 