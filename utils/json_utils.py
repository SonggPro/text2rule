"""
JSON工具模块
"""

import json
import re
from typing import Dict, Any, Optional


class JsonUtils:
    """JSON工具类"""
    
    @staticmethod
    def extract_json_from_text(text: str) -> Optional[Dict[str, Any]]:
        """从文本中提取JSON对象"""
        # 首先检查markdown包装的JSON
        match = re.search(r'```json\s*([\s\S]+?)\s*```', text, re.IGNORECASE)
        json_str = match.group(1) if match else text
        
        # 查找JSON对象
        match = re.search(r'\{[\s\S]*\}', json_str)
        if not match:
            return None
        
        try:
            return json.loads(match.group(0))
        except json.JSONDecodeError as e:
            print(f"JSON解析失败: {e}")
            return None
    
    @staticmethod
    def safe_json_loads(json_str: str, default: Any = None) -> Any:
        """安全的JSON解析"""
        try:
            return json.loads(json_str)
        except (json.JSONDecodeError, TypeError):
            return default
    
    @staticmethod
    def format_json(data: Dict[str, Any], indent: int = 2) -> str:
        """格式化JSON字符串"""
        return json.dumps(data, ensure_ascii=False, indent=indent)
    
    @staticmethod
    def merge_json_objects(obj1: Dict[str, Any], obj2: Dict[str, Any]) -> Dict[str, Any]:
        """合并两个JSON对象"""
        result = obj1.copy()
        result.update(obj2)
        return result
    
    @staticmethod
    def flatten_json(obj: Dict[str, Any], prefix: str = "") -> Dict[str, Any]:
        """扁平化JSON对象"""
        flattened = {}
        for key, value in obj.items():
            new_key = f"{prefix}.{key}" if prefix else key
            if isinstance(value, dict):
                flattened.update(JsonUtils.flatten_json(value, new_key))
            else:
                flattened[new_key] = value
        return flattened
    
    @staticmethod
    def validate_json_schema(data: Dict[str, Any], schema: Dict[str, Any]) -> bool:
        """验证JSON数据是否符合模式"""
        # 简单的模式验证实现
        for key, expected_type in schema.items():
            if key not in data:
                return False
            if not isinstance(data[key], expected_type):
                return False
        return True 