"""
LLM客户端模块
"""

from typing import Dict, Any, List, Optional
import json
import re
from openai import OpenAI
from autogen_ext.models.openai import OpenAIChatCompletionClient

from config import ModelConfig, PromptConfig
from .base import BaseProcessor


class LLMClient(BaseProcessor):
    """LLM客户端类"""
    
    def __init__(self, model_name: str, task_type: str, **kwargs):
        super().__init__(model_name, task_type, **kwargs)
        self.openai_client = self._create_openai_client()
        self.autogen_client = self._create_autogen_client()
    
    def _create_openai_client(self) -> OpenAI:
        """创建OpenAI客户端"""
        return OpenAI(
            api_key=self.model_config["api_key"],
            base_url=self.model_config["base_url"]
        )
    
    def _create_autogen_client(self) -> OpenAIChatCompletionClient:
        """创建AutoGen客户端"""
        return OpenAIChatCompletionClient(
            model=self.model_config["model"],
            api_key=self.model_config["api_key"],
            base_url=self.model_config["base_url"]
        )
    
    def extract_parameters(self, properties: Dict[str, Any], patient_note: str) -> Dict[str, Any]:
        """从病历中提取参数"""
        try:
            tools = [{
                "type": "function",
                "function": {
                    "name": "parametersExtraction",
                    "description": PromptConfig.get_extraction_prompt("param_extraction_desc_cn"),
                    "parameters": {
                        "type": "object", 
                        "properties": properties, 
                        "required": list(properties.keys())
                    }
                }
            }]
            
            messages = [
                {"role": "system", "content": PromptConfig.get_extraction_prompt("param_extraction_system_cn")},
                {"role": "user", "content": patient_note}
            ]
            
            response = self.openai_client.chat.completions.create(
                model=self.model_config["extraction_model"],
                messages=messages,
                tools=tools,
                tool_choice="required"
            )
            
            params = json.loads(response.choices[0].message.tool_calls[0].function.arguments)
            
            # 处理嵌套的properties结构
            if params.get('properties', {}):
                params_properties = params.get('properties', {})
            else:
                params_properties = params
            
            # 后处理提取的参数
            processed_params = self._post_process_parameters(params_properties)
            
            self.log_info(f"参数提取成功，提取到 {len(processed_params)} 个参数")
            return processed_params
            
        except Exception as e:
            self.log_error(f"参数提取失败: {e}", exc_info=True)
            return {}
    
    def _post_process_parameters(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """后处理提取的参数"""
        processed_params = {}
        
        for key, value in params.items():
            # 处理字符串类型的布尔值
            if isinstance(value, str):
                if value.lower() in ["true", "false"]:
                    processed_params[key] = value.lower() == "true"
                else:
                    processed_params[key] = value
            # 处理空值
            elif value is None or value == "" or value == []:
                processed_params[key] = None
            else:
                processed_params[key] = value
        
        return processed_params
    
    def convert_unit(self, key: str, value: Any, from_unit: str, to_unit: str) -> tuple:
        """单位转换"""
        try:
            prompt = PromptConfig.get_conversion_prompt("unit_conversion").format(
                key=key, 
                original_value=value, 
                original_unit=from_unit, 
                target_unit=to_unit
            )
            
            response = self.openai_client.chat.completions.create(
                model=self.model_config["conversion_model"],
                messages=[{"role": "user", "content": prompt}],
                response_format={"type": "json_object"}
            )
            
            result_json = self._extract_json_from_response(response.choices[0].message.content)
            if result_json and "value" in result_json:
                converted_value = result_json["value"]
                converted_unit = result_json.get("unit", to_unit)
                
                self.log_info(f"单位转换成功: {value} {from_unit} -> {converted_value} {converted_unit}")
                return converted_value, converted_unit
                
        except Exception as e:
            self.log_error(f"单位转换失败: {e}", exc_info=True)
        
        return value, from_unit
    
    def _extract_json_from_response(self, text: str) -> Optional[Dict]:
        """从响应中提取JSON对象"""
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
            self.log_error(f"JSON解析失败: {e}")
            return None
    
    def chat_completion(self, messages: List[Dict[str, str]], **kwargs) -> str:
        """通用聊天完成"""
        try:
            response = self.openai_client.chat.completions.create(
                model=self.model_config["model"],
                messages=messages,
                **kwargs
            )
            return response.choices[0].message.content
        except Exception as e:
            self.log_error(f"聊天完成失败: {e}", exc_info=True)
            return ""
    
    def get_autogen_client(self) -> OpenAIChatCompletionClient:
        """获取AutoGen客户端"""
        return self.autogen_client
    
    def process(self, *args, **kwargs) -> Any:
        """实现抽象方法"""
        # 这个方法主要用于兼容BaseProcessor，实际使用时直接调用具体方法
        pass 