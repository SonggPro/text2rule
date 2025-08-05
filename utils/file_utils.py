"""
文件工具模块
"""

import os
import json
import csv
from typing import Dict, Any, List, Optional

from config import PathConfig


class FileUtils:
    """文件工具类"""
    
    @staticmethod
    def ensure_directory(directory: str):
        """确保目录存在"""
        os.makedirs(directory, exist_ok=True)
    
    @staticmethod
    def load_jsonl(file_path: str) -> List[Dict[str, Any]]:
        """加载JSONL文件"""
        data = []
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                for line in f:
                    if line.strip():
                        data.append(json.loads(line))
        except FileNotFoundError:
            print(f"文件未找到: {file_path}")
        except json.JSONDecodeError as e:
            print(f"JSON解析错误: {e}")
        return data
    
    @staticmethod
    def save_jsonl(data: List[Dict[str, Any]], file_path: str):
        """保存为JSONL格式"""
        FileUtils.ensure_directory(os.path.dirname(file_path))
        with open(file_path, 'w', encoding='utf-8') as f:
            for item in data:
                json.dump(item, f, ensure_ascii=False)
                f.write('\n')
    
    @staticmethod
    def append_jsonl(data: Dict[str, Any], file_path: str):
        """追加到JSONL文件"""
        FileUtils.ensure_directory(os.path.dirname(file_path))
        with open(file_path, 'a', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False)
            f.write('\n')
    
    @staticmethod
    def load_json(file_path: str) -> Dict[str, Any]:
        """加载JSON文件"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"文件未找到: {file_path}")
            return {}
        except json.JSONDecodeError as e:
            print(f"JSON解析错误: {e}")
            return {}
    
    @staticmethod
    def save_json(data: Dict[str, Any], file_path: str):
        """保存为JSON格式"""
        FileUtils.ensure_directory(os.path.dirname(file_path))
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    @staticmethod
    def load_csv(file_path: str) -> List[Dict[str, Any]]:
        """加载CSV文件"""
        data = []
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    data.append(row)
        except FileNotFoundError:
            print(f"文件未找到: {file_path}")
        return data
    
    @staticmethod
    def file_exists(file_path: str) -> bool:
        """检查文件是否存在"""
        return os.path.exists(file_path)
    
    @staticmethod
    def get_file_size(file_path: str) -> int:
        """获取文件大小"""
        try:
            return os.path.getsize(file_path)
        except OSError:
            return 0
    
    @staticmethod
    def list_files(directory: str, pattern: str = "*") -> List[str]:
        """列出目录中的文件"""
        import glob
        pattern_path = os.path.join(directory, pattern)
        return glob.glob(pattern_path) 