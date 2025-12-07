"""
启动Web版3D数字人
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# 安装依赖检查
try:
    from flask import Flask
    from flask_cors import CORS
except ImportError:
    print("正在安装依赖...")
    os.system('pip install flask flask-cors')
    from flask import Flask
    from flask_cors import CORS

from web_digital_human.app import app

if __name__ == '__main__':
    print("=" * 55)
    print("  🌐 Web 3D数字人 - Little Shark")
    print("=" * 55)
    print()
    print("  特性:")
    print("    ✓ 真正的3D VRM模型")
    print("    ✓ 说话嘴型动画")
    print("    ✓ 眨眼动画")
    print("    ✓ 呼吸动画")
    print("    ✓ 表情变化")
    print("    ✓ 可嵌入任意网页")
    print()
    print("  访问地址: http://localhost:5000")
    print()
    print("  按 Ctrl+C 停止服务")
    print()
    
    app.run(host='0.0.0.0', port=5000, debug=False)
