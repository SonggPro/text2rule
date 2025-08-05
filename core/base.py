"""
基础处理器模块
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
import logging
import time

from config import ModelConfig, TaskConfig, PathConfig


class BaseProcessor(ABC):
    """基础处理器抽象类"""
    
    def __init__(self, model_name: str, task_type: str, **kwargs):
        """
        初始化基础处理器
        
        Args:
            model_name: 模型名称
            task_type: 任务类型
            **kwargs: 其他参数
        """
        self.model_name = model_name
        self.task_type = task_type
        self.model_config = ModelConfig.get_model_config(model_name, **kwargs)
        self.task_config = TaskConfig.get_task_config(task_type)
        
        # 设置日志
        self.logger = self._setup_logger()
        
        # 确保目录存在
        PathConfig.ensure_directories()
    
    def _setup_logger(self) -> logging.Logger:
        """设置日志记录器"""
        logger = logging.getLogger(f"{self.__class__.__name__}_{self.model_name}_{self.task_type}")
        logger.setLevel(logging.INFO)
        
        # 避免重复添加处理器
        if not logger.handlers:
            # 文件处理器
            log_file = PathConfig.get_output_file_path(self.task_type, self.model_name, "logs")
            file_handler = logging.FileHandler(log_file, encoding='utf-8')
            file_handler.setLevel(logging.INFO)
            
            # 控制台处理器
            console_handler = logging.StreamHandler()
            console_handler.setLevel(logging.INFO)
            
            # 格式化器
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            file_handler.setFormatter(formatter)
            console_handler.setFormatter(formatter)
            
            logger.addHandler(file_handler)
            logger.addHandler(console_handler)
        
        return logger
    
    def validate_config(self) -> bool:
        """验证配置是否有效"""
        try:
            # 验证模型配置
            if not ModelConfig.validate_config(self.model_name):
                self.logger.error(f"模型配置无效: {self.model_name}")
                return False
            
            # 验证任务类型
            if not TaskConfig.validate_task_type(self.task_type):
                self.logger.error(f"不支持的任务类型: {self.task_type}")
                return False
            
            return True
        except Exception as e:
            self.logger.error(f"配置验证失败: {e}")
            return False
    
    def log_info(self, message: str):
        """记录信息日志"""
        self.logger.info(message)
    
    def log_error(self, message: str, exc_info: bool = False):
        """记录错误日志"""
        self.logger.error(message, exc_info=exc_info)
    
    def log_warning(self, message: str):
        """记录警告日志"""
        self.logger.warning(message)
    
    def get_execution_time(self, func):
        """装饰器：记录函数执行时间"""
        def wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = func(*args, **kwargs)
                end_time = time.time()
                self.log_info(f"{func.__name__} 执行时间: {end_time - start_time:.2f}秒")
                return result
            except Exception as e:
                end_time = time.time()
                self.log_error(f"{func.__name__} 执行失败，耗时: {end_time - start_time:.2f}秒", exc_info=True)
                raise
        return wrapper
    
    @abstractmethod
    def process(self, *args, **kwargs) -> Any:
        """处理主逻辑，子类必须实现"""
        pass
    
    def run(self, *args, **kwargs) -> Any:
        """运行处理器"""
        if not self.validate_config():
            raise ValueError("配置验证失败")
        
        self.log_info(f"开始执行 {self.__class__.__name__}")
        try:
            result = self.process(*args, **kwargs)
            self.log_info(f"{self.__class__.__name__} 执行完成")
            return result
        except Exception as e:
            self.log_error(f"{self.__class__.__name__} 执行失败: {e}", exc_info=True)
            raise 