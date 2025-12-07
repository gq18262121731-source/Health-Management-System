"""
Web版3D数字人后端API
====================

提供聊天API接口，供前端调用
包含健康评估系统API扩展
"""

import os
import sys
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS

# 添加父目录和当前目录到路径
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, current_dir)
sys.path.insert(0, parent_dir)

app = Flask(__name__, static_folder='static')
# 配置 CORS - 简化配置，避免重复设置头
CORS(app, origins="*", supports_credentials=False)

# 注册健康评估API蓝图
try:
    from web_digital_human.health_api import health_api
    app.register_blueprint(health_api)
    print("✓ 健康评估API蓝图注册成功")
except ImportError:
    try:
        from health_api import health_api
        app.register_blueprint(health_api)
        print("✓ 健康评估API蓝图注册成功")
    except ImportError as e:
        print(f"⚠ 健康评估API蓝图注册失败: {e}")

# 注册语音交互API蓝图
try:
    from web_digital_human.voice_api import voice_api
    app.register_blueprint(voice_api)
    print("✓ 语音交互API蓝图注册成功")
except ImportError:
    try:
        from voice_api import voice_api
        app.register_blueprint(voice_api)
        print("✓ 语音交互API蓝图注册成功")
    except ImportError as e:
        print(f"⚠ 语音交互API蓝图注册失败: {e}")

# 智能体系统
agent_system = None

def get_agent():
    global agent_system
    if agent_system is None:
        try:
            from agents.multi_agent_system import MultiAgentSystem
            agent_system = MultiAgentSystem(user_id="web_user", enable_assessment=False)
            print("✓ 多智能体系统初始化完成")
        except Exception as e:
            print(f"智能体初始化失败: {e}")
    return agent_system


@app.route('/')
def index():
    return send_from_directory('static', 'index.html')


@app.route('/static/<path:filename>')
def serve_static(filename):
    return send_from_directory('static', filename)


@app.route('/models/<path:filename>')
def serve_model(filename):
    """提供VRM模型文件"""
    models_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'little shark')
    return send_from_directory(models_dir, filename)


@app.route('/api/chat', methods=['POST'])
def chat():
    """聊天API"""
    data = request.json
    message = data.get('message', '')
    
    if not message:
        return jsonify({'error': '消息不能为空'}), 400
    
    agent = get_agent()
    if agent:
        try:
            response = agent.chat(message)
            return jsonify({
                'response': response,
                'emotion': 'happy'  # 可以根据内容分析情绪
            })
        except Exception as e:
            return jsonify({'response': f'抱歉，出现了问题：{str(e)}', 'emotion': 'neutral'})
    else:
        return jsonify({'response': '系统正在初始化，请稍后再试', 'emotion': 'neutral'})


@app.route('/api/greeting', methods=['GET'])
def greeting():
    """获取问候语"""
    agent = get_agent()
    if agent:
        return jsonify({'message': agent.get_greeting()})
    return jsonify({'message': '你好！我是小康，很高兴见到你！'})


if __name__ == '__main__':
    print("=" * 55)
    print("  🌐 Web 3D数字人服务器")
    print("=" * 55)
    print()
    print("  访问: http://localhost:5000")
    print()
    app.run(host='0.0.0.0', port=5000, debug=True)
