"""
主路由 - 页面渲染
"""

from flask import Blueprint, render_template, request, session, jsonify
from app.services.agent_manager import AgentManager

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    """主页"""
    return render_template('index.html')

@main_bp.route('/chat')
def chat():
    """聊天页面"""
    agent_id = request.args.get('agent', None)
    return render_template('chat.html', agent_id=agent_id)

@main_bp.route('/agents')
def agents_page():
    """智能体管理页面"""
    return render_template('agents.html')

@main_bp.route('/dashboard')
def dashboard():
    """仪表盘页面"""
    return render_template('dashboard.html')

@main_bp.route('/settings')
def settings():
    """设置页面"""
    return render_template('settings.html')
