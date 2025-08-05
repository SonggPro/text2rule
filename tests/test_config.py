"""
配置模块测试
"""

import unittest
from config import ModelConfig, TaskConfig, PromptConfig, PathConfig


class TestModelConfig(unittest.TestCase):
    """模型配置测试"""
    
    def test_get_model_config(self):
        """测试获取模型配置"""
        config = ModelConfig.get_model_config("gpt-4o-mini")
        self.assertIn("model", config)
        self.assertIn("api_key", config)
        self.assertIn("base_url", config)
    
    def test_invalid_model(self):
        """测试无效模型"""
        with self.assertRaises(ValueError):
            ModelConfig.get_model_config("invalid-model")
    
    def test_supported_models(self):
        """测试支持的模型列表"""
        models = ModelConfig.get_supported_models()
        self.assertIn("gpt-4o-mini", models)
        self.assertIn("qwen", models)


class TestTaskConfig(unittest.TestCase):
    """任务配置测试"""
    
    def test_get_task_config(self):
        """测试获取任务配置"""
        config = TaskConfig.get_task_config("indicator")
        self.assertIn("patient_data_file", config)
        self.assertIn("patient_id_key", config)
    
    def test_invalid_task_type(self):
        """测试无效任务类型"""
        with self.assertRaises(ValueError):
            TaskConfig.get_task_config("invalid-task")
    
    def test_execution_config(self):
        """测试执行配置"""
        config = TaskConfig.get_execution_config("indicator")
        self.assertIn("task_type", config)
        self.assertIn("generated_functions_file", config)


class TestPromptConfig(unittest.TestCase):
    """提示词配置测试"""
    
    def test_get_extraction_prompt(self):
        """测试获取提取提示词"""
        prompt = PromptConfig.get_extraction_prompt("param_extraction_system_cn")
        self.assertIsInstance(prompt, str)
        self.assertGreater(len(prompt), 0)
    
    def test_get_conversion_prompt(self):
        """测试获取转换提示词"""
        prompt = PromptConfig.get_conversion_prompt("unit_conversion")
        self.assertIsInstance(prompt, str)
        self.assertGreater(len(prompt), 0)


class TestPathConfig(unittest.TestCase):
    """路径配置测试"""
    
    def test_ensure_directories(self):
        """测试确保目录存在"""
        PathConfig.ensure_directories()
        # 这里可以添加目录存在性检查
    
    def test_get_file_path(self):
        """测试获取文件路径"""
        path = PathConfig.get_file_path("generated_functions", "test.jsonl")
        self.assertIn("generated_functions", path)
        self.assertIn("test.jsonl", path)


if __name__ == "__main__":
    unittest.main() 