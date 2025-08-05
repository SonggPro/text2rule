#!/usr/bin/env python3
"""
Web界面启动脚本
"""

import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from web.gradio_app import create_app

if __name__ == "__main__":
    print("🚀 启动医学指标计算系统Web界面...")
    print("📱 访问地址: http://localhost:7860")
    print("🔄 按 Ctrl+C 停止服务")
    
    try:
        interface = create_app()
        interface.launch(
            share=True,
            server_name="0.0.0.0",
            server_port=7860,
            show_error=True
        )
    except KeyboardInterrupt:
        print("\n👋 服务已停止")
    except Exception as e:
        print(f"❌ 启动失败: {e}")
        sys.exit(1) 