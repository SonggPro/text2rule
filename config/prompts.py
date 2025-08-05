"""
提示词配置模块
"""

from typing import Dict, Any


class PromptConfig:
    """提示词配置类"""
    
    # 参数提取相关提示词
    EXTRACTION_PROMPTS = {
        "param_extraction_system": "You are an expert in medical information extraction. Your task is to extract relevant facts from an electronic medical record (EMR). When dealing with time-related judgments, your reasoning must be based on the time documented within the EMR. if theres no fact related to the properties,using other facts in EMR to calculate it,if still cant get, return 0.01",
        "param_extraction_system_cn": "你是一名医学信息抽取专家，你的任务是从电子病历（EMR）中抽取相关事实。在涉及时间相关判断时，你的推理必须基于病历中记录的时间。若病历中对同一事实提及多次，需返回最符合要求的那一项，通常为最后出现的项。你可以调用工具来进行抽取，并且事实的抽取结果返回为True/False",
        "param_extraction_desc": "From the provided electronic medical record (EMR) excerpts, extract the necessary properties.",
        "param_extraction_desc_cn": """你是一名医学信息抽取专家，请从用户提供的电子病历段落中抽取与属性properties中事实的逻辑值。需要严格确诊才可以返回True，而不是简单地字段匹配，其它情况均应该为False，其它类型也类似。当病历中对同一事实提及多次或有时间先后时，取最后的结果。"""
    }
    
    # 单位转换提示词
    CONVERSION_PROMPTS = {
        "unit_conversion": "you are an expert in unit conversion,u need to convert {key}:{original_value} {original_unit} to {target_unit}，your output format must be {{\"value\": \"converted value\", \"unit\": \"target unit\"}}in json format at last. important: converted value must be a number,not a string，not a character"
    }
    
    @classmethod
    def get_extraction_prompt(cls, prompt_key: str) -> str:
        """获取参数提取提示词"""
        return cls.EXTRACTION_PROMPTS.get(prompt_key, "")
    
    @classmethod
    def get_conversion_prompt(cls, prompt_key: str) -> str:
        """获取单位转换提示词"""
        return cls.CONVERSION_PROMPTS.get(prompt_key, "") 