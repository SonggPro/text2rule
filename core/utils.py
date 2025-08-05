"""
核心工具函数模块
"""

import json
import re
import logging
from typing import Dict, Any, Optional, List
from openai import OpenAI
from config.settings import PromptConfig

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def get_json_from_response(text: str) -> Optional[Dict]:
    """从字符串中提取JSON对象，优先检查markdown包装的JSON"""
    match = re.search(r'```json\s*([\s\S]+?)\s*```', text, re.IGNORECASE)
    json_str = match.group(1) if match else text
    
    match = re.search(r'\{[\s\S]*\}', json_str)
    if not match:
        return None

    try:
        return json.loads(match.group(0))
    except json.JSONDecodeError as e:
        logger.warning(f"Failed to parse JSON. Error: {e}. Content: '{match.group(0)}'")
        return None

def append_result_to_jsonl(file_path: str, data: Dict[str, Any]):
    """将字典作为新行追加到JSONL文件中"""
    try:
        with open(file_path, "a", encoding="utf-8") as file:
            json.dump(data, file, ensure_ascii=False)
            file.write('\n')
    except Exception as e:
        logger.error(f"Error writing to {file_path}: {e}")

def load_jsonl_file(file_path: str) -> List[Dict[str, Any]]:
    """加载JSONL文件"""
    data = []
    try:
        with open(file_path, "r", encoding='utf-8') as file:
            for i, line in enumerate(file):
                try:
                    data.append(json.loads(line.strip()))
                except json.JSONDecodeError:
                    logger.warning(f"Skipping invalid JSON on line {i+1} in {file_path}")
    except FileNotFoundError:
        logger.error(f"File not found: {file_path}")
    return data

def save_jsonl_file(file_path: str, data: List[Dict[str, Any]]):
    """保存数据到JSONL文件"""
    try:
        with open(file_path, "w", encoding="utf-8") as file:
            for item in data:
                json.dump(item, file, ensure_ascii=False)
                file.write('\n')
    except Exception as e:
        logger.error(f"Error saving to {file_path}: {e}")

def call_unit_conversion_llm(client: OpenAI, key: str, value: Any, from_unit: str, to_unit: str) -> tuple:
    """使用LLM进行单位转换，失败时返回原始值"""
    prompt = PromptConfig.get_prompt("unit_conversion").format(
        key=key, original_value=value, original_unit=from_unit, target_unit=to_unit
    )
    try:
        logger.info(f"Unit conversion prompt: {prompt}")
        response = client.chat.completions.create(
            model=client.model,  # 使用客户端配置的模型
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"}
        )
        logger.info(f'{value} {from_unit} to {to_unit}')
        logger.info(f"Unit conversion response: {response.choices[0].message.content}")
        
        result_json = get_json_from_response(response.choices[0].message.content)
        if result_json and "value" in result_json:
            return result_json["value"], result_json.get("unit", to_unit)
    except Exception as e:
        logger.error(f"Error during unit conversion for key '{key}': {e}")
    return value, from_unit

def validate_api_config(api_config: Dict[str, Any]) -> bool:
    """验证API配置是否有效"""
    required_fields = ["key", "base_url", "extraction_model", "conversion_model"]
    for field in required_fields:
        if not api_config.get(field):
            logger.error(f"Missing required field: {field}")
            return False
    return True

def sanitize_filename(filename: str) -> str:
    """清理文件名，移除不安全的字符"""
    return re.sub(r'[<>:"/\\|?*]', '_', filename) 