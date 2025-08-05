"""
路径配置模块
"""

import os
from typing import Dict, Any


class PathConfig:
    """路径配置类"""
    
    # 基础路径
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    # 数据目录
    DATA_DIR = os.path.join(BASE_DIR, "data")
    GENERATED_FUNCTIONS_DIR = os.path.join(DATA_DIR, "generated_functions")
    PATIENT_DATA_DIR = os.path.join(DATA_DIR, "patient_data")
    INDICATORS_DIR = os.path.join(DATA_DIR, "indicators")
    
    # 结果目录
    RESULTS_DIR = os.path.join(BASE_DIR, "results")
    EXECUTION_RESULTS_DIR = os.path.join(RESULTS_DIR, "execution_results")
    
    # 日志目录
    LOGS_DIR = os.path.join(BASE_DIR, "logs")
    
    # 测试目录
    TESTS_DIR = os.path.join(BASE_DIR, "tests")
    
    @classmethod
    def ensure_directories(cls):
        """确保所有必要的目录存在"""
        directories = [
            cls.DATA_DIR,
            cls.GENERATED_FUNCTIONS_DIR,
            cls.PATIENT_DATA_DIR,
            cls.INDICATORS_DIR,
            cls.RESULTS_DIR,
            cls.EXECUTION_RESULTS_DIR,
            cls.LOGS_DIR,
            cls.TESTS_DIR
        ]
        
        for directory in directories:
            os.makedirs(directory, exist_ok=True)
    
    @classmethod
    def get_file_path(cls, file_type: str, filename: str) -> str:
        """获取文件路径"""
        if file_type == "generated_functions":
            return os.path.join(cls.GENERATED_FUNCTIONS_DIR, filename)
        elif file_type == "patient_data":
            return os.path.join(cls.PATIENT_DATA_DIR, filename)
        elif file_type == "indicators":
            return os.path.join(cls.INDICATORS_DIR, filename)
        elif file_type == "execution_results":
            return os.path.join(cls.EXECUTION_RESULTS_DIR, filename)
        elif file_type == "logs":
            return os.path.join(cls.LOGS_DIR, filename)
        else:
            return os.path.join(cls.DATA_DIR, filename)
    
    @classmethod
    def get_output_file_path(cls, task_type: str, model_name: str, file_type: str = "generated_functions") -> str:
        """获取输出文件路径"""
        if file_type == "generated_functions":
            filename = f"{task_type}_{model_name}_0721_none.jsonl"
            return os.path.join(cls.GENERATED_FUNCTIONS_DIR, filename)
        elif file_type == "execution_results":
            filename = f"{task_type}_{model_name}_results.jsonl"
            return os.path.join(cls.EXECUTION_RESULTS_DIR, filename)
        elif file_type == "logs":
            filename = f"{task_type}_{model_name}_logs.json"
            return os.path.join(cls.LOGS_DIR, filename)
        else:
            raise ValueError(f"不支持的文件类型: {file_type}")
    
    @classmethod
    def get_all_paths(cls) -> Dict[str, str]:
        """获取所有路径配置"""
        return {
            "base_dir": cls.BASE_DIR,
            "data_dir": cls.DATA_DIR,
            "generated_functions_dir": cls.GENERATED_FUNCTIONS_DIR,
            "patient_data_dir": cls.PATIENT_DATA_DIR,
            "indicators_dir": cls.INDICATORS_DIR,
            "results_dir": cls.RESULTS_DIR,
            "execution_results_dir": cls.EXECUTION_RESULTS_DIR,
            "logs_dir": cls.LOGS_DIR,
            "tests_dir": cls.TESTS_DIR
        } 