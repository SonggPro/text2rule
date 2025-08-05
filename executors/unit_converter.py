"""
单位转换器模块
"""

from typing import Dict, Any, Tuple, Optional, List

from core import LLMClient


class UnitConverter:
    """单位转换器类"""
    
    def __init__(self, llm_client: LLMClient):
        """
        初始化单位转换器
        
        Args:
            llm_client: LLM客户端
        """
        self.llm_client = llm_client
    
    def convert_unit(self, key: str, value: Any, from_unit: str, to_unit: str) -> Tuple[Any, str]:
        """转换单位"""
        return self.llm_client.convert_unit(key, value, from_unit, to_unit)
    
    def convert_parameters_units(self, parameters: Dict[str, Any], 
                               need_unit: Dict[str, str]) -> Dict[str, Any]:
        """转换参数的单位"""
        converted_params = parameters.copy()
        
        for key, value in converted_params.items():
            if key in need_unit and isinstance(value, list) and value:
                item = value[0]
                val, unit = item.get("value"), item.get("unit", "").strip()
                target_unit = need_unit[key].strip()
                
                # 如果单位不同，进行转换
                if unit.lower() != target_unit.lower() and val is not None and target_unit:
                    new_val, new_unit = self.convert_unit(key, val, unit, target_unit)
                    converted_params[key] = float(new_val)
                else:
                    converted_params[key] = float(val) if val is not None else None
        
        return converted_params
    
    def batch_convert(self, parameters_list: List[Dict[str, Any]], 
                     need_unit: Dict[str, str]) -> List[Dict[str, Any]]:
        """批量转换单位"""
        converted_list = []
        
        for params in parameters_list:
            converted_params = self.convert_parameters_units(params, need_unit)
            converted_list.append(converted_params)
        
        return converted_list 