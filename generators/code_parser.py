"""
代码解析器模块
"""

import json
import re
import ast
from typing import Dict, Any, Optional, Tuple


class CodeParser:
    """代码解析器类"""
    
    @staticmethod
    def parse_generation_result(message: str, task_description: str) -> Dict[str, Any]:
        """解析生成结果"""
        try:
            # 提取函数和属性
            function_code = CodeParser._extract_function_code(message)
            properties = CodeParser._extract_properties(message)
            
            return {
                "task_description": task_description,
                "function_code": function_code,
                "properties": properties,
                "raw_message": message,
                "status": "success"
            }
        except Exception as e:
            return {
                "task_description": task_description,
                "error": str(e),
                "raw_message": message,
                "status": "failed"
            }
    
    @staticmethod
    def _extract_function_code(message: str) -> str:
        """提取函数代码"""
        # 查找代码块
        if "```python" in message:
            start = message.find("```python") + 9
            end = message.find("```", start)
            if end != -1:
                return message[start:end].strip()
        
        # 查找def开头的函数
        lines = message.split('\n')
        function_lines = []
        in_function = False
        
        for line in lines:
            if line.strip().startswith('def '):
                in_function = True
            if in_function:
                function_lines.append(line)
            if in_function and line.strip() == '':
                break
        
        return '\n'.join(function_lines) if function_lines else ""
    
    @staticmethod
    def _extract_properties(message: str) -> Dict[str, Any]:
        """提取属性定义"""
        # 查找JSON格式的属性
        if "properties" in message.lower():
            # 尝试找到JSON块
            start = message.find('{')
            if start != -1:
                # 找到匹配的结束括号
                brace_count = 0
                end = start
                for i, char in enumerate(message[start:], start):
                    if char == '{':
                        brace_count += 1
                    elif char == '}':
                        brace_count -= 1
                        if brace_count == 0:
                            end = i + 1
                            break
                
                try:
                    json_str = message[start:end]
                    return json.loads(json_str)
                except json.JSONDecodeError:
                    pass
        
        return {}
    
    @staticmethod
    def refactor_properties_string(properties_string: str) -> Dict[str, Any]:
        """重构属性字符串，处理单位信息"""
        need_unit_dict = {}
        
        # 优先匹配 "properties = { ... }" 格式
        match = re.search(r'properties\s*=\s*(\{.*\})', properties_string, re.DOTALL)
        if match:
            dict_str = match.group(1)
        else:
            # 如果没有，则直接寻找被大括号包裹的内容
            match = re.search(r'(\{.*\})', properties_string, re.DOTALL)
            dict_str = match.group(1) if match else properties_string
        
        try:
            # 使用 ast.literal_eval 安全地将字符串解析为 Python 字典
            properties_dict = ast.literal_eval(dict_str)
            if not isinstance(properties_dict, dict):
                raise ValueError("解析的对象不是字典")
        except (ValueError, SyntaxError) as e:
            print(f"ast.literal_eval 失败 ('{e}')，使用原始字符串")
            return {"properties_row": properties_string, "need_unit": {}}
        
        # 遍历字典，重构包含单位的 'number' 类型的属性
        for key, value in properties_dict.items():
            desc = value.get("description", "") if isinstance(value, dict) else ""
            unit = ""
            main_desc = desc
            
            # 英文 in ...
            if isinstance(value, dict) and value.get("type") == "number" and " in " in desc:
                m = re.search(r'(.+?) in (.+)', desc)
                if m:
                    main_desc = m.group(1).strip()
                    unit = m.group(2).split(',')[0].strip()
            # 中文"单位:"
            elif isinstance(value, dict) and value.get("type") == "number" and ("单位:" in desc or "单位：" in desc):
                m = re.search(r'(.+?)单位[:：]\s*([^，。；;\s]+)', desc)
                if m:
                    main_desc = m.group(1).strip()
                    unit = m.group(2).strip()
            
            # 记录需要单位转换的键和目标单位
            if unit:
                need_unit_dict[key] = unit
                # 构建新的 'array' 结构来替代原来的 'number' 结构
                properties_dict[key] = {
                    "type": "array",
                    "description": main_desc,
                    "items": {
                        "type": "object",
                        "properties": {
                            "value": {"type": "number", "description": main_desc},
                            "unit": {"type": "string", "description": "exactly unit extracted from EMR."}
                        },
                        "required": ["value", "unit"]
                    }
                }
        
        # 将修改后的字典转换回格式化的字符串
        new_row_str = f"properties = {json.dumps(properties_dict, ensure_ascii=False, indent=4)}"
        
        return {"properties_row": new_row_str, "need_unit": need_unit_dict}
    
    @staticmethod
    def parse_function_string(function_string: str) -> Dict[str, Any]:
        """解析函数字符串"""
        try:
            # 提取函数定义
            if "def " in function_string:
                func_start = function_string.find("def ")
                func_end = function_string.find(":", func_start)
                if func_end != -1:
                    func_def = function_string[func_start:func_end].strip()
                    func_name = func_def.split("(")[0].replace("def ", "")
                    
                    # 提取参数
                    params_start = func_def.find("(") + 1
                    params_end = func_def.find(")")
                    params_str = func_def[params_start:params_end]
                    params = [p.strip() for p in params_str.split(",") if p.strip()]
                    
                    return {
                        "function_name": func_name,
                        "parameters": params,
                        "function_code": function_string
                    }
        except Exception as e:
            print(f"函数解析错误: {e}")
        
        return {} 