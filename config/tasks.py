"""
任务配置模块
"""

from typing import Dict, Any, List


class TaskConfig:
    """任务配置类"""
    
    # 支持的任务类型
    TASK_TYPES = ["medcalc", "cmqcic", "indicator"]
    
    # 任务特定配置
    TASK_SPECIFIC_CONFIGS = {
        "medcalc": {
            "patient_data_file": 'data/patient_data/MedCalc_test_data.jsonl',
            "patient_id_key": "Calculator ID",
            "patient_note_key": "Patient Note",
            "output_type_filter": "decimal"
        },
        "cmqcic": {
            "patient_data_file": 'data/patient_data/data.jsonl',
            "patient_id_key": "unique_id",
            "patient_note_key": "patient note"
        },
        "indicator": {
            "patient_data_file": 'data/patient_data/data.jsonl',
            "patient_id_key": "unique_id",
            "patient_note_key": "patient note",
            "indicator_file": 'data/indicators/indicator.json'
        }
    }
    
    # 默认执行配置
    DEFAULT_EXECUTION_CONFIG = {
        "task_type": "cmqcic",
        "generated_functions_file": 'data/generated_functions/indicator_gpt-4o-mini_0721_none.jsonl',
        "results_output_file": "results/execution_results/mqcic_gpt-4o-mini_0721_1by1.jsonl",
        "include_ids": []
    }
    
    # 默认生成配置
    DEFAULT_GENERATION_CONFIG = {
        "task_type": "indicator",
        "selected_model": "gpt-4o-mini",
        "output_file_template": "data/generated_functions/{task_type}_{model_name}_0721_none.jsonl",
        "log_file": "logs/medcalc_all_logs.json"
    }
    
    @classmethod
    def get_task_config(cls, task_type: str) -> Dict[str, Any]:
        """获取任务特定配置"""
        if task_type not in cls.TASK_SPECIFIC_CONFIGS:
            raise ValueError(f"不支持的任务类型: {task_type}")
        
        return cls.TASK_SPECIFIC_CONFIGS[task_type].copy()
    
    @classmethod
    def get_execution_config(cls, task_type: str = None, **kwargs) -> Dict[str, Any]:
        """获取执行配置"""
        config = cls.DEFAULT_EXECUTION_CONFIG.copy()
        if task_type:
            config["task_type"] = task_type
        config.update(kwargs)
        return config
    
    @classmethod
    def get_generation_config(cls, task_type: str = None, model_name: str = None, **kwargs) -> Dict[str, Any]:
        """获取生成配置"""
        config = cls.DEFAULT_GENERATION_CONFIG.copy()
        if task_type:
            config["task_type"] = task_type
        if model_name:
            config["selected_model"] = model_name
        config.update(kwargs)
        return config
    
    @classmethod
    def get_supported_task_types(cls) -> List[str]:
        """获取支持的任务类型列表"""
        return cls.TASK_TYPES.copy()
    
    @classmethod
    def validate_task_type(cls, task_type: str) -> bool:
        """验证任务类型是否支持"""
        return task_type in cls.TASK_TYPES 