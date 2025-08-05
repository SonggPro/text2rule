"""
Text2Rule Demo - 完整的医疗文本到规则转换流程演示
"""

import asyncio
import json
import os
from typing import Dict, Any

from framework.generator import FunctionGenerator
from framework.executor import FunctionExecutor
from config import MODEL_CONFIGS


class Text2RuleDemo:
    """Text2Rule演示类"""
    
    def __init__(self, model_name: str = "gpt-4o-mini"):
        self.model_name = model_name
        self.generator = FunctionGenerator(model_name=model_name, task_type="indicator")
        self.executor = FunctionExecutor(model_name=model_name, task_type="indicator")
    
    async def run_complete_workflow(self, task_description: str, patient_notes: list) -> Dict[str, Any]:
        """运行完整的流程：生成函数 -> 执行函数"""
        
        print("=" * 60)
        print("Text2Rule 完整流程演示")
        print("=" * 60)
        
        # 步骤1: 生成函数
        print("\n步骤1: 生成医疗质控函数")
        print("-" * 40)
        print(f"任务描述: {task_description}")
        
        generation_result = await self.generator.generate_function(task_description)
        
        if generation_result.get("status") != "success":
            print(f"函数生成失败: {generation_result.get('error', '')}")
            return {"status": "failed", "error": "函数生成失败"}
        
        print("✅ 函数生成成功!")
        print(f"生成的函数代码:\n{generation_result.get('function_code', '')}")
        print(f"函数属性:\n{json.dumps(generation_result.get('properties', {}), indent=2, ensure_ascii=False)}")
        
        # 步骤2: 执行函数
        print("\n步骤2: 执行生成的函数")
        print("-" * 40)
        
        execution_results = []
        for i, patient_note in enumerate(patient_notes):
            print(f"\n处理病历 {i+1}/{len(patient_notes)}:")
            print(f"病历内容: {patient_note[:100]}...")
            
            # 提取参数
            extracted_params = self.executor.extract_parameters(
                generation_result.get("properties", {}), 
                patient_note
            )
            print(f"提取的参数: {extracted_params}")
            
            # 执行函数
            function_result = self.executor.execute_function(
                generation_result.get("function_code", ""),
                extracted_params
            )
            print(f"执行结果: {function_result}")
            
            execution_results.append({
                "patient_id": i,
                "patient_note": patient_note,
                "extracted_parameters": extracted_params,
                "function_result": function_result
            })
        
        # 步骤3: 保存结果
        print("\n步骤3: 保存结果")
        print("-" * 40)
        
        from framework.utils import ResultSaver
        ResultSaver.save_generated_function(generation_result, "indicator", self.model_name)
        
        for result in execution_results:
            ResultSaver.save_execution_result(result, "indicator", self.model_name)
        
        print("✅ 结果已保存到 output/ 目录")
        
        return {
            "status": "success",
            "generation_result": generation_result,
            "execution_results": execution_results
        }
    
    def run_simple_demo(self):
        """运行简单演示（不需要API调用）"""
        print("=" * 60)
        print("Text2Rule 简单演示")
        print("=" * 60)
        
        # 示例数据
        sample_task = "检查患者是否完成了血常规和尿常规检查"
        sample_function = """
def check_blood_urine_test(blood_test_completed, urine_test_completed):
    return blood_test_completed and urine_test_completed
"""
        sample_properties = {
            "blood_test_completed": {
                "type": "boolean",
                "description": "血常规检查是否完成"
            },
            "urine_test_completed": {
                "type": "boolean",
                "description": "尿常规检查是否完成"
            }
        }
        
        sample_patient_notes = [
            "患者已完成血常规检查，尿常规检查结果正常。",
            "患者血常规检查未完成，尿常规检查已完成。",
            "患者血常规和尿常规检查均未完成。"
        ]
        
        print(f"\n任务描述: {sample_task}")
        print(f"\n生成的函数:\n{sample_function}")
        print(f"\n函数属性:\n{json.dumps(sample_properties, indent=2, ensure_ascii=False)}")
        
        print("\n执行结果:")
        for i, note in enumerate(sample_patient_notes):
            # 模拟参数提取
            if "血常规" in note and "完成" in note:
                blood_test = True
            else:
                blood_test = False
                
            if "尿常规" in note and "完成" in note:
                urine_test = True
            else:
                urine_test = False
            
            # 执行函数
            result = blood_test and urine_test
            
            print(f"病历 {i+1}: {note}")
            print(f"  血常规: {blood_test}, 尿常规: {urine_test}")
            print(f"  结果: {result}")
            print()


def check_api_config():
    """检查API配置"""
    print("检查API配置...")
    
    if not MODEL_CONFIGS["gpt-4o-mini"]["api_key"]:
        print("❌ 未配置OpenAI API密钥")
        print("请在环境变量中设置 OPENAI_API_KEY")
        return False
    
    print("✅ API配置正确")
    return True


async def main():
    """主函数"""
    print("Text2Rule 医疗文本到规则转换框架")
    print("=" * 60)
    
    # 检查配置
    if not check_api_config():
        print("\n运行简单演示（不需要API）:")
        demo = Text2RuleDemo()
        demo.run_simple_demo()
        return
    
    # 创建演示实例
    demo = Text2RuleDemo()
    
    # 示例任务和病历
    task_description = "检查患者是否完成了血常规和尿常规检查"
    patient_notes = [
        "患者已完成血常规检查，尿常规检查结果正常。",
        "患者血常规检查未完成，尿常规检查已完成。",
        "患者血常规和尿常规检查均未完成。"
    ]
    
    # 运行完整流程
    result = await demo.run_complete_workflow(task_description, patient_notes)
    
    if result.get("status") == "success":
        print("\n🎉 演示完成！")
        print("生成的函数和执行结果已保存到 output/ 目录")
    else:
        print(f"\n❌ 演示失败: {result.get('error', '')}")


if __name__ == "__main__":
    asyncio.run(main()) 