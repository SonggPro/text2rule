"""
Agent团队模块
"""

import asyncio
from typing import Dict, Any, List
from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.teams import RoundRobinGroupChat
from autogen_agentchat.conditions import TextMentionTermination
from autogen_core import CancellationToken

from core import LLMClient


class AgentTeam:
    """Agent团队类"""
    
    def __init__(self, llm_client: LLMClient, task_type: str):
        """
        初始化Agent团队
        
        Args:
            llm_client: LLM客户端
            task_type: 任务类型
        """
        self.llm_client = llm_client
        self.task_type = task_type
        self.autogen_client = llm_client.get_autogen_client()
        self.agents = self._create_agents()
        self.group_chat = self._create_group_chat()
    
    def _create_agents(self) -> List[AssistantAgent]:
        """创建Agent列表"""
        from config import PromptConfig
        
        # 获取任务类型的Agent系统消息
        agent_messages = PromptConfig.get_all_agent_messages(self.task_type)
        
        agents = []
        for agent_type, system_message in agent_messages.items():
            agent = AssistantAgent(
                name=agent_type,
                system_message=system_message,
                llm_config={"config_list": [self.autogen_client]},
                human_input_mode="NEVER"
            )
            agents.append(agent)
        
        return agents
    
    def _create_group_chat(self) -> RoundRobinGroupChat:
        """创建群聊"""
        return RoundRobinGroupChat(
            agents=self.agents,
            termination_condition=TextMentionTermination("APPROVE")
        )
    
    async def generate_function(self, task_description: str) -> Dict[str, Any]:
        """生成函数"""
        try:
            # 发送任务给第一个Agent
            await self.group_chat.a_send(
                message=f"请分析以下医疗质控指标并生成相应的Python函数：\n\n{task_description}",
                sender=self.agents[0]
            )
            
            # 获取最终结果
            final_message = self.group_chat.messages[-1]["content"]
            
            return {
                "task_description": task_description,
                "raw_message": final_message,
                "status": "success"
            }
            
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
            result = await self.generate_function(description)
            results.append(result)
            
            # 避免请求过于频繁
            await asyncio.sleep(1)
        
        return results 