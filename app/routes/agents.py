"""
智能体管理路由
"""

from flask import Blueprint, render_template, request, jsonify, current_app
from app.services.agent_manager import Agent

agents_bp = Blueprint('agents', __name__)

@agents_bp.route('/')
def list_agents():
    """智能体列表页面"""
    return render_template('agents/list.html')

@agents_bp.route('/create')
def create_agent_page():
    """创建智能体页面"""
    agent_manager = current_app.agent_manager
    categories = agent_manager.get_categories()
    return render_template('agents/create.html', categories=categories)

@agents_bp.route('/<agent_id>/edit')
def edit_agent_page(agent_id):
    """编辑智能体页面"""
    agent_manager = current_app.agent_manager
    categories = agent_manager.get_categories()
    return render_template('agents/edit.html', agent_id=agent_id, categories=categories)

@agents_bp.route('/<agent_id>')
def agent_detail(agent_id):
    """智能体详情页面"""
    return render_template('agents/detail.html', agent_id=agent_id)
