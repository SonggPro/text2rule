"""
基于Gradio的前端界面
"""

import gradio as gr
import json
import logging
from typing import Dict, Any, List
from config.settings import APIConfig, ExecutionConfig, PathConfig
from executor import MainExecutor

logger = logging.getLogger(__name__)

class GradioApp:
    """Gradio应用类"""
    
    def __init__(self):
        """初始化Gradio应用"""
        self.executor = None
        self.available_tasks = []
        
    def create_interface(self):
        """创建Gradio界面"""
        with gr.Blocks(title="医学指标计算系统", theme=gr.themes.Soft()) as interface:
            gr.Markdown("# 🏥 医学指标计算系统")
            gr.Markdown("基于LLM的医学指标自动计算和评估系统")
            
            with gr.Tab("🔧 系统配置"):
                self._create_config_tab()
            
            with gr.Tab("📊 任务执行"):
                self._create_execution_tab()
            
            with gr.Tab("🧪 单任务测试"):
                self._create_single_task_tab()
            
            with gr.Tab("📈 结果查看"):
                self._create_results_tab()
        
        return interface
    
    def _create_config_tab(self):
        """创建配置标签页"""
        with gr.Row():
            with gr.Column():
                gr.Markdown("### API配置")
                
                api_key = gr.Textbox(
                    label="API Key",
                    placeholder="请输入您的API Key",
                    type="password",
                    lines=1
                )
                
                base_url = gr.Textbox(
                    label="Base URL",
                    placeholder="请输入API Base URL",
                    lines=1
                )
                
                model_provider = gr.Radio(
                    choices=["OpenAI", "Qwen"],
                    label="模型提供商",
                    value="OpenAI"
                )
                
                test_connection_btn = gr.Button("🔗 测试连接", variant="primary")
                connection_status = gr.Textbox(label="连接状态", interactive=False)
            
            with gr.Column():
                gr.Markdown("### 任务配置")
                
                task_type = gr.Radio(
                    choices=["cmqcic", "medcalc"],
                    label="任务类型",
                    value="cmqcic"
                )
                
                include_ids = gr.Textbox(
                    label="指定任务ID（可选，用逗号分隔）",
                    placeholder="例如: task1,task2,task3",
                    lines=1
                )
                
                load_tasks_btn = gr.Button("📋 加载任务列表", variant="primary")
                task_count = gr.Textbox(label="可用任务数量", interactive=False)
        
        # 事件绑定
        test_connection_btn.click(
            fn=self._test_connection,
            inputs=[api_key, base_url, model_provider],
            outputs=connection_status
        )
        
        load_tasks_btn.click(
            fn=self._load_tasks,
            inputs=[api_key, base_url, model_provider, task_type],
            outputs=task_count
        )
    
    def _create_execution_tab(self):
        """创建执行标签页"""
        with gr.Row():
            with gr.Column():
                gr.Markdown("### 批量执行")
                
                start_execution_btn = gr.Button("🚀 开始执行", variant="primary", size="lg")
                execution_progress = gr.Textbox(
                    label="执行进度",
                    lines=10,
                    interactive=False
                )
            
            with gr.Column():
                gr.Markdown("### 执行状态")
                
                execution_status = gr.Textbox(
                    label="当前状态",
                    interactive=False
                )
                
                completed_tasks = gr.Textbox(
                    label="已完成任务",
                    interactive=False
                )
        
        # 事件绑定
        start_execution_btn.click(
            fn=self._start_execution,
            inputs=[],
            outputs=[execution_progress, execution_status, completed_tasks]
        )
    
    def _create_single_task_tab(self):
        """创建单任务测试标签页"""
        with gr.Row():
            with gr.Column():
                gr.Markdown("### 单任务测试")
                
                task_id = gr.Dropdown(
                    label="选择任务",
                    choices=[],
                    interactive=True
                )
                
                patient_note = gr.Textbox(
                    label="患者病历",
                    placeholder="请输入患者病历内容...",
                    lines=10
                )
                
                test_task_btn = gr.Button("🧪 测试任务", variant="primary")
            
            with gr.Column():
                gr.Markdown("### 测试结果")
                
                test_result = gr.JSON(
                    label="执行结果",
                    interactive=False
                )
        
        # 事件绑定
        test_task_btn.click(
            fn=self._test_single_task,
            inputs=[task_id, patient_note],
            outputs=test_result
        )
    
    def _create_results_tab(self):
        """创建结果查看标签页"""
        with gr.Row():
            with gr.Column():
                gr.Markdown("### 结果文件")
                
                results_file = gr.File(
                    label="选择结果文件",
                    file_types=[".jsonl"]
                )
                
                load_results_btn = gr.Button("📂 加载结果", variant="primary")
            
            with gr.Column():
                gr.Markdown("### 结果预览")
                
                results_preview = gr.JSON(
                    label="结果数据",
                    interactive=False
                )
        
        # 事件绑定
        load_results_btn.click(
            fn=self._load_results,
            inputs=[results_file],
            outputs=results_preview
        )
    
    def _test_connection(self, api_key: str, base_url: str, model_provider: str) -> str:
        """测试API连接"""
        try:
            if not api_key or not base_url:
                return "❌ 请提供API Key和Base URL"
            
            # 创建API配置
            if model_provider == "OpenAI":
                api_config = APIConfig.get_openai_config(api_key, base_url)
            else:
                api_config = APIConfig.get_qwen_config(api_key, base_url)
            
            # 创建执行器并测试连接
            execution_config = ExecutionConfig.get_config()
            self.executor = MainExecutor(api_config, execution_config)
            
            if self.executor.test_connection():
                return "✅ 连接成功！"
            else:
                return "❌ 连接失败，请检查配置"
                
        except Exception as e:
            return f"❌ 连接错误: {str(e)}"
    
    def _load_tasks(self, api_key: str, base_url: str, model_provider: str, task_type: str) -> str:
        """加载任务列表"""
        try:
            if not self.executor:
                return "❌ 请先测试连接"
            
            # 更新执行配置
            execution_config = ExecutionConfig.get_config(task_type)
            self.executor.execution_config = execution_config
            
            # 加载任务
            self.available_tasks = self.executor.get_available_tasks()
            
            return f"✅ 成功加载 {len(self.available_tasks)} 个任务"
            
        except Exception as e:
            return f"❌ 加载任务失败: {str(e)}"
    
    def _start_execution(self) -> tuple:
        """开始执行"""
        try:
            if not self.executor:
                return "❌ 请先配置并测试连接", "未开始", "0"
            
            # 这里应该实现实际的执行逻辑
            # 由于Gradio的限制，这里只是示例
            return "🚀 执行已开始...", "执行中", "0"
            
        except Exception as e:
            return f"❌ 执行失败: {str(e)}", "失败", "0"
    
    def _test_single_task(self, task_id: str, patient_note: str) -> Dict[str, Any]:
        """测试单个任务"""
        try:
            if not self.executor:
                return {"error": "请先配置并测试连接"}
            
            if not task_id or not patient_note:
                return {"error": "请选择任务并输入病历内容"}
            
            result = self.executor.execute_single_task(task_id, patient_note)
            return result
            
        except Exception as e:
            return {"error": f"执行失败: {str(e)}"}
    
    def _load_results(self, results_file) -> Dict[str, Any]:
        """加载结果文件"""
        try:
            if not results_file:
                return {"error": "请选择结果文件"}
            
            # 读取结果文件
            with open(results_file.name, 'r', encoding='utf-8') as f:
                results = []
                for line in f:
                    results.append(json.loads(line.strip()))
            
            return {"results": results[:10]}  # 只显示前10条
            
        except Exception as e:
            return {"error": f"加载结果失败: {str(e)}"}

def create_app():
    """创建Gradio应用"""
    app = GradioApp()
    return app.create_interface()

if __name__ == "__main__":
    interface = create_app()
    interface.launch(share=True, server_name="0.0.0.0", server_port=7860) 