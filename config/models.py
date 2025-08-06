"""
模型配置模块
"""

from typing import Dict, Any, Optional
import os
import dotenv

dotenv.load_dotenv()

API_KEY = os.getenv("API_KEY")
BASE_URL = os.getenv("BASE_URL")

class ModelConfig:
    """模型配置类"""
    
    # 支持的模型配置
    MODELS = {
        "gpt-4o-mini": {
            "model": "gpt-4o-mini-2024-07-18",
            "api_key": API_KEY,
            "base_url": BASE_URL,
            "extraction_model": "gpt-4o-mini-2024-07-18",
            "conversion_model": "gpt-4o-mini-2024-07-18"
        },
        "qwen": {
            "model": "qwen2.5-72b-instruct",
            "api_key": API_KEY,
            "base_url": BASE_URL,
            "extraction_model": "qwen2.5-72b-instruct",
            "conversion_model": "qwen2.5-72b-instruct",
            "model_info": {
                "vision": False,
                "function_calling": True,
                "json_output": True,
                "family": "qwen",
                "structured_output": True,
                "model": "qwen-2.5-72b-instruct"
            }
        },
        "claude-sonnet": {
            "model": "claude-3-7-sonnet-20250219",
            "api_key": API_KEY,
            "base_url": BASE_URL,
            "extraction_model": "claude-3-7-sonnet-20250219",
            "conversion_model": "claude-3-7-sonnet-20250219"
        },
        "gpt-4.1-mini": {
            "model": "gpt-4.1-mini-2025-04-14",
            "api_key": API_KEY,
            "base_url": BASE_URL,
            "extraction_model": "gpt-4.1-mini-2025-04-14",
            "conversion_model": "gpt-4.1-mini-2025-04-14"
        }
    }
    
    @classmethod
    def get_model_config(cls, model_name: str, api_key: Optional[str] = None, 
                        base_url: Optional[str] = None) -> Dict[str, Any]:
        """获取模型配置"""
        if model_name not in cls.MODELS:
            raise ValueError(f"不支持的模型: {model_name}")
        
        config = cls.MODELS[model_name].copy()
        
        # 优先使用传入的参数，其次使用环境变量
        if api_key:
            config["api_key"] = api_key
        elif not config["api_key"]:
            env_key = f"{model_name.upper()}_API_KEY"
            config["api_key"] = os.getenv(env_key, "")
            
        if base_url:
            config["base_url"] = base_url
        elif not config["base_url"]:
            env_url = f"{model_name.upper()}_BASE_URL"
            config["base_url"] = os.getenv(env_url, "")
        
        return config
    
    @classmethod
    def get_supported_models(cls) -> list:
        """获取支持的模型列表"""
        return list(cls.MODELS.keys())
    
    @classmethod
    def validate_config(cls, model_name: str) -> bool:
        """验证模型配置是否完整"""
        try:
            config = cls.get_model_config(model_name)
            return bool(config.get("api_key") and config.get("base_url"))
        except ValueError:
            return False 