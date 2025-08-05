"""
参数提取器模块
"""

import json
from typing import Dict, Any, List, Optional

from config import PromptConfig
from core import LLMClient


class ParameterExtractor:
    """参数提取器类"""
    
    def __init__(self, llm_client: LLMClient):
        """
        初始化参数提取器
        
        Args:
            llm_client: LLM客户端
        """
        self.llm_client = llm_client
    
    def extract_parameters(self, properties: Dict[str, Any], patient_note: str) -> Dict[str, Any]:
        """从病历中提取参数"""
        return self.llm_client.extract_parameters(properties, patient_note)
    
    def extract_parameters_with_units(self, properties: Dict[str, Any], patient_note: str, 
                                    need_unit: Dict[str, str]) -> Dict[str, Any]:
        """从病历中提取参数并处理单位"""
        # 提取参数
        extracted_params = self.extract_parameters(properties, patient_note)
        
        # 处理单位转换
        for key, value in extracted_params.items():
            if key in need_unit and isinstance(value, list) and value:
                item = value[0]
                val, unit = item.get("value"), item.get("unit", "").strip()
                target_unit = need_unit[key].strip()
                
                # 如果单位不同，进行转换
                if unit.lower() != target_unit.lower() and val is not None and target_unit:
                    new_val, _ = self.llm_client.convert_unit(key, val, unit, target_unit)
                    extracted_params[key] = float(new_val)
                else:
                    extracted_params[key] = float(val) if val is not None else None
        
        return extracted_params
    
    def batch_extract(self, properties: Dict[str, Any], patient_notes: List[str]) -> List[Dict[str, Any]]:
        """批量提取参数"""
        results = []
        
        for i, note in enumerate(patient_notes):
            try:
                extracted_params = self.extract_parameters(properties, note)
                results.append({
                    "patient_index": i,
                    "patient_note": note,
                    "extracted_parameters": extracted_params,
                    "status": "success"
                })
            except Exception as e:
                results.append({
                    "patient_index": i,
                    "patient_note": note,
                    "error": str(e),
                    "status": "failed"
                })
        
        return results 