"""
函数生成器模块
"""

import asyncio
import time
from typing import Dict, Any, List, Optional

from config import TaskConfig, PathConfig
from core import LLMClient, DataProcessor
from .agent_team import AgentTeam
from .code_parser import CodeParser


class FunctionGenerator:
    """函数生成器类"""
    
    def __init__(self, model_name: str, task_type: str, **kwargs):
        """
        初始化函数生成器
        
        Args:
            model_name: 模型名称
            task_type: 任务类型
            **kwargs: 其他参数
        """
        self.model_name = model_name
        self.task_type = task_type
        
        # 初始化组件
        self.llm_client = LLMClient(model_name, task_type, **kwargs)
        self.data_processor = DataProcessor(model_name, task_type, **kwargs)
        self.agent_team = AgentTeam(self.llm_client, task_type)
        
        # 获取配置
        self.generation_config = TaskConfig.get_generation_config(task_type, model_name)
    
    async def generate_single_function(self, task_description: str) -> Dict[str, Any]:
        """生成单个函数"""
        try:
            # 使用Agent团队生成函数
            agent_result = await self.agent_team.generate_function(task_description)
            
            if agent_result.get("status") == "success":
                # 解析生成结果
                parsed_result = CodeParser.parse_generation_result(
                    agent_result["raw_message"], 
                    task_description
                )
                
                # 重构属性字符串
                if parsed_result.get("properties"):
                    refactor_result = CodeParser.refactor_properties_string(
                        str(parsed_result["properties"])
                    )
                    parsed_result["properties"] = refactor_result["properties_row"]
                    parsed_result["need_unit"] = refactor_result["need_unit"]
                
                # 添加元数据
                parsed_result.update({
                    "model_name": self.model_name,
                    "task_type": self.task_type,
                    "timestamp": time.time()
                })
                
                return parsed_result
            else:
                return agent_result
                
        except Exception as e:
            return {
                "task_description": task_description,
                "error": str(e),
                "status": "failed"
            }
    
    async def batch_generate(self, task_descriptions: List[str]) -> List[Dict[str, Any]]:
        """批量生成函数"""
        results = []
        
        for i, description in enumerate(task_descriptions):
            print(f"正在生成第 {i+1}/{len(task_descriptions)} 个函数...")
            result = await self.generate_single_function(description)
            results.append(result)
            
            # 保存结果
            if result.get("status") == "success":
                output_file = PathConfig.get_output_file_path(
                    self.task_type, self.model_name, "generated_functions"
                )
                self.data_processor.save_result(result, output_file)
            
            # 避免请求过于频繁
            await asyncio.sleep(1)
        
        return results
    
    def load_tasks(self) -> List[str]:
        """加载任务数据"""
        if self.task_type == "medcalc":
            return self._load_medcalc_tasks()
        elif self.task_type == "indicator":
            return self._load_indicator_tasks()
        else:
            return []
    
    def _load_medcalc_tasks(self) -> List[str]:
        """加载MedCalc任务"""
        # 这里可以添加MedCalc任务加载逻辑
        return []
    
    def _load_indicator_tasks(self) -> List[str]:
        """加载指标任务"""
        # 这里可以添加指标任务加载逻辑
        return []
    
    async def run(self) -> List[Dict[str, Any]]:
        """运行函数生成器"""
        # 加载任务
        tasks = self.load_tasks()
        if not tasks:
            print("没有找到任务数据")
            return []
        
        print(f"开始生成 {len(tasks)} 个函数...")
        
        # 批量生成
        results = await self.batch_generate(tasks)
        
        # 统计结果
        success_count = sum(1 for r in results if r.get("status") == "success")
        print(f"生成完成: {success_count}/{len(results)} 个函数生成成功")
        
        return results 