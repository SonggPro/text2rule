"""
主入口模块
"""

import asyncio
import argparse
from typing import Optional

from config import ModelConfig, TaskConfig, PathConfig
from generators import FunctionGenerator
from executors import FunctionExecutor
from utils import Validation


class Text2Rule:
    """Text2Rule主类"""
    
    def __init__(self, model_name: str = "gpt-4o-mini", task_type: str = "indicator"):
        """
        初始化Text2Rule
        
        Args:
            model_name: 模型名称
            task_type: 任务类型
        """
        self.model_name = model_name
        self.task_type = task_type
        
        # 验证配置
        if not Validation.validate_model_name(model_name):
            raise ValueError(f"不支持的模型: {model_name}")
        
        if not Validation.validate_task_type(task_type):
            raise ValueError(f"不支持的任务类型: {task_type}")
        
        # 确保目录存在
        PathConfig.ensure_directories()
    
    async def generate_functions(self, api_key: Optional[str] = None, 
                               base_url: Optional[str] = None) -> bool:
        """生成函数"""
        try:
            print(f"开始生成函数，模型: {self.model_name}, 任务类型: {self.task_type}")
            
            # 创建函数生成器
            generator = FunctionGenerator(
                model_name=self.model_name,
                task_type=self.task_type,
                api_key=api_key,
                base_url=base_url
            )
            
            # 运行生成器
            results = await generator.run()
            
            success_count = sum(1 for r in results if r.get("status") == "success")
            print(f"函数生成完成: {success_count}/{len(results)} 个函数生成成功")
            
            return success_count > 0
            
        except Exception as e:
            print(f"函数生成失败: {e}")
            return False
    
    def execute_functions(self, api_key: Optional[str] = None, 
                         base_url: Optional[str] = None,
                         include_ids: Optional[list] = None) -> bool:
        """执行函数"""
        try:
            print(f"开始执行函数，模型: {self.model_name}, 任务类型: {self.task_type}")
            
            # 创建函数执行器
            executor = FunctionExecutor(
                model_name=self.model_name,
                task_type=self.task_type,
                api_key=api_key,
                base_url=base_url
            )
            
            # 运行执行器
            results = executor.run(include_ids=include_ids)
            
            print(f"函数执行完成: {len(results)} 个任务执行完成")
            return len(results) > 0
            
        except Exception as e:
            print(f"函数执行失败: {e}")
            return False
    
    async def run_pipeline(self, api_key: Optional[str] = None, 
                          base_url: Optional[str] = None,
                          include_ids: Optional[list] = None) -> bool:
        """运行完整流程"""
        print("开始运行Text2Rule完整流程...")
        
        # 第一步：生成函数
        print("\n=== 第一步：生成函数 ===")
        generation_success = await self.generate_functions(api_key, base_url)
        
        if not generation_success:
            print("函数生成失败，停止执行")
            return False
        
        # 第二步：执行函数
        print("\n=== 第二步：执行函数 ===")
        execution_success = self.execute_functions(api_key, base_url, include_ids)
        
        if not execution_success:
            print("函数执行失败")
            return False
        
        print("\n=== 流程完成 ===")
        return True


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="Text2Rule - 医疗质控函数生成和执行工具")
    
    parser.add_argument("--model", default="gpt-4o-mini", 
                       choices=["gpt-4o-mini", "qwen", "claude-sonnet", "gpt-4.1-mini"],
                       help="使用的模型名称")
    
    parser.add_argument("--task-type", default="indicator",
                       choices=["medcalc", "cmqcic", "indicator"],
                       help="任务类型")
    
    parser.add_argument("--mode", choices=["generate", "execute", "pipeline"], 
                       default="pipeline",
                       help="运行模式：generate(仅生成), execute(仅执行), pipeline(完整流程)")
    
    parser.add_argument("--api-key", help="API密钥")
    parser.add_argument("--base-url", help="API基础URL")
    parser.add_argument("--include-ids", nargs="*", help="指定要处理的ID列表")
    
    args = parser.parse_args()
    
    try:
        # 创建Text2Rule实例
        text2rule = Text2Rule(model_name=args.model, task_type=args.task_type)
        
        if args.mode == "generate":
            # 仅生成函数
            success = asyncio.run(text2rule.generate_functions(args.api_key, args.base_url))
        elif args.mode == "execute":
            # 仅执行函数
            success = text2rule.execute_functions(args.api_key, args.base_url, args.include_ids)
        else:
            # 完整流程
            success = asyncio.run(text2rule.run_pipeline(args.api_key, args.base_url, args.include_ids))
        
        if success:
            print("操作成功完成")
        else:
            print("操作失败")
            exit(1)
            
    except Exception as e:
        print(f"程序执行失败: {e}")
        exit(1)


if __name__ == "__main__":
    main() 