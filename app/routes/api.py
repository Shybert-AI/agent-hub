"""
API 路由 - 数据接口
"""

from flask import Blueprint, request, jsonify, Response, current_app, session
from app.models import db, Conversation, Message
from app.services.agent_manager import AgentManager
from app.services.dialogue_service import dialogue_service
import json
import logging

logger = logging.getLogger(__name__)

api_bp = Blueprint('api', __name__)

@api_bp.route('/agents', methods=['GET'])
def get_agents():
    """获取所有智能体"""
    agent_manager = current_app.agent_manager
    return jsonify({
        'code': 0,
        'data': agent_manager.get_all_agents()
    })

@api_bp.route('/agents/categories', methods=['GET'])
def get_categories():
    """获取所有分类"""
    agent_manager = current_app.agent_manager
    return jsonify({
        'code': 0,
        'data': agent_manager.get_categories()
    })

@api_bp.route('/agents/<agent_id>', methods=['GET'])
def get_agent(agent_id):
    """获取单个智能体"""
    agent_manager = current_app.agent_manager
    agent = agent_manager.get_agent(agent_id)
    if agent:
        return jsonify({'code': 0, 'data': agent})
    return jsonify({'code': 404, 'message': 'Agent not found'}), 404

@api_bp.route('/agents/category/<category>', methods=['GET'])
def get_agents_by_category(category):
    """按分类获取智能体"""
    agent_manager = current_app.agent_manager
    return jsonify({
        'code': 0,
        'data': agent_manager.get_agents_by_category(category)
    })

@api_bp.route('/agents/search', methods=['GET'])
def search_agents():
    """搜索智能体"""
    query = request.args.get('q', '')
    agent_manager = current_app.agent_manager
    results = agent_manager.search_agents(query)
    return jsonify({
        'code': 0,
        'data': results
    })

@api_bp.route('/agents/popular', methods=['GET'])
def get_popular_agents():
    """获取热门智能体"""
    agent_manager = current_app.agent_manager
    limit = request.args.get('limit', 5, type=int)
    return jsonify({
        'code': 0,
        'data': agent_manager.get_popular_agents(limit)
    })

@api_bp.route('/agents', methods=['POST'])
def create_agent():
    """创建新智能体"""
    data = request.get_json()
    agent_manager = current_app.agent_manager
    try:
        agent = agent_manager.add_agent(data)
        return jsonify({'code': 0, 'data': agent.to_dict()})
    except Exception as e:
        return jsonify({'code': 500, 'message': str(e)}), 500

@api_bp.route('/agents/<agent_id>', methods=['PUT'])
def update_agent(agent_id):
    """更新智能体"""
    data = request.get_json()
    agent_manager = current_app.agent_manager
    result = agent_manager.update_agent(agent_id, data)
    if result:
        return jsonify({'code': 0, 'data': result})
    return jsonify({'code': 404, 'message': 'Agent not found'}), 404

@api_bp.route('/agents/<agent_id>', methods=['DELETE'])
def delete_agent(agent_id):
    """删除智能体"""
    agent_manager = current_app.agent_manager
    if agent_manager.delete_agent(agent_id):
        return jsonify({'code': 0, 'message': 'Agent deleted'})
    return jsonify({'code': 404, 'message': 'Agent not found'}), 404

@api_bp.route('/chat', methods=['POST'])
def chat():
    """处理对话请求"""
    logger.info("[Chat] 收到请求")
    data = request.get_json()
    message = data.get('message', '')
    agent_id = data.get('agent_id', 'default')
    use_opencode = data.get('use_opencode', True)
    deepseek_api_key = data.get('deepseek_api_key', '')
    model = data.get('model', 'deepseek-chat')
    
    logger.info(f"[Chat] 参数: agent_id={agent_id}, use_opencode={use_opencode}, message长度={len(message)}")
    
    if not message:
        return jsonify({'code': 400, 'message': 'Message is required'}), 400
    
    agent_manager = current_app.agent_manager
    agent = agent_manager.get_agent(agent_id)
    if not agent:
        if agent_id == 'default':
            all_agents = agent_manager.get_all_agents()
            if all_agents:
                agent = all_agents[0]
                agent_id = agent['id']
                logger.info(f"[Chat] 使用默认智能体: {agent_id}")
            else:
                return jsonify({'code': 404, 'message': '未找到任何智能体'}), 404
        else:
            return jsonify({'code': 404, 'message': f'未找到智能体: {agent_id}'}), 404
    
    logger.info(f"[Chat] 使用智能体: {agent['name']} (id={agent_id})")
    agent_manager.increment_usage(agent_id)
    
    def generate():
        for chunk in dialogue_service.chat_with_agent(
            agent_id=agent_id,
            user_message=message,
            agent=agent,
            use_opencode=use_opencode,
            deepseek_api_key=deepseek_api_key,
            model=model
        ):
            yield f"data: {json.dumps({'content': chunk})}\n\n"
        yield "data: [DONE]\n\n"
    
    return Response(
        generate(),
        mimetype='text/event-stream',
        headers={
            'Cache-Control': 'no-cache',
            'Connection': 'keep-alive',
            'X-Accel-Buffering': 'no'
        }
    )

@api_bp.route('/chat/deepseek', methods=['POST'])
def chat_deepseek():
    """直接调用 DeepSeek"""
    data = request.get_json()
    messages = data.get('messages', [])
    deepseek_api_key = data.get('deepseek_api_key', '')
    model = data.get('model', 'deepseek-chat')
    
    if not messages:
        return jsonify({'code': 400, 'message': 'Messages is required'}), 400
    
    def generate():
        for chunk in dialogue_service.chat_with_deepseek(messages):
            yield f"data: {json.dumps({'content': chunk})}\n\n"
        yield "data: [DONE]\n\n"
    
    return Response(
        generate(),
        mimetype='text/event-stream',
        headers={
            'Cache-Control': 'no-cache',
            'Connection': 'keep-alive',
            'X-Accel-Buffering': 'no'
        }
    )

@api_bp.route('/health', methods=['GET'])
def health():
    """健康检查"""
    return jsonify({'status': 'ok', 'code': 0})

# ============ 对话历史 API ============

@api_bp.route('/conversations', methods=['GET'])
def get_conversations():
    """获取当前用户的所有对话"""
    user_id = session.get('user_id')
    conversations = Conversation.query.filter_by(user_id=user_id).order_by(
        Conversation.updated_at.desc()
    ).all()
    return jsonify({
        'code': 0,
        'data': [conv.to_dict() for conv in conversations]
    })

@api_bp.route('/conversations', methods=['POST'])
def create_conversation():
    """创建新对话"""
    data = request.get_json()
    user_id = session.get('user_id')
    
    conversation = Conversation(
        user_id=user_id,
        agent_id=data.get('agent_id', 'default'),
        title=data.get('title', '新对话')
    )
    db.session.add(conversation)
    db.session.commit()
    
    return jsonify({
        'code': 0,
        'data': conversation.to_dict()
    })

@api_bp.route('/conversations/<int:conv_id>', methods=['GET'])
def get_conversation(conv_id):
    """获取对话详情"""
    user_id = session.get('user_id')
    conversation = Conversation.query.filter_by(id=conv_id, user_id=user_id).first()
    
    if not conversation:
        return jsonify({'code': 404, 'message': 'Conversation not found'}), 404
    
    messages = conversation.messages.order_by(Message.created_at.asc()).all()
    
    return jsonify({
        'code': 0,
        'data': {
            'conversation': conversation.to_dict(),
            'messages': [msg.to_dict() for msg in messages]
        }
    })

@api_bp.route('/conversations/<int:conv_id>', methods=['PUT'])
def update_conversation(conv_id):
    """更新对话"""
    data = request.get_json()
    user_id = session.get('user_id')
    conversation = Conversation.query.filter_by(id=conv_id, user_id=user_id).first()
    
    if not conversation:
        return jsonify({'code': 404, 'message': 'Conversation not found'}), 404
    
    if 'title' in data:
        conversation.title = data['title']
    db.session.commit()
    
    return jsonify({
        'code': 0,
        'data': conversation.to_dict()
    })

@api_bp.route('/conversations/<int:conv_id>', methods=['DELETE'])
def delete_conversation(conv_id):
    """删除对话"""
    user_id = session.get('user_id')
    conversation = Conversation.query.filter_by(id=conv_id, user_id=user_id).first()
    
    if not conversation:
        return jsonify({'code': 404, 'message': 'Conversation not found'}), 404
    
    db.session.delete(conversation)
    db.session.commit()
    
    return jsonify({
        'code': 0,
        'message': 'Conversation deleted'
    })

# ============ 消息 API ============

@api_bp.route('/conversations/<int:conv_id>/messages', methods=['GET'])
def get_messages(conv_id):
    """获取对话中的所有消息"""
    user_id = session.get('user_id')
    conversation = Conversation.query.filter_by(id=conv_id, user_id=user_id).first()
    
    if not conversation:
        return jsonify({'code': 404, 'message': 'Conversation not found'}), 404
    
    messages = conversation.messages.order_by(Message.created_at.asc()).all()
    
    return jsonify({
        'code': 0,
        'data': [msg.to_dict() for msg in messages]
    })

@api_bp.route('/conversations/<int:conv_id>/messages', methods=['POST'])
def add_message(conv_id):
    """添加消息到对话"""
    data = request.get_json()
    user_id = session.get('user_id')
    conversation = Conversation.query.filter_by(id=conv_id, user_id=user_id).first()
    
    if not conversation:
        return jsonify({'code': 404, 'message': 'Conversation not found'}), 404
    
    message = Message(
        conversation_id=conv_id,
        role=data.get('role', 'user'),
        content=data.get('content', '')
    )
    db.session.add(message)
    conversation.updated_at = message.created_at
    db.session.commit()
    
    return jsonify({
        'code': 0,
        'data': message.to_dict()
    })

# ============ 智能体评分 API ============

@api_bp.route('/agents/<agent_id>/rating', methods=['POST'])
def rate_agent(agent_id):
    """为智能体评分"""
    data = request.get_json()
    user_id = session.get('user_id')
    
    if not user_id:
        return jsonify({'code': 401, 'message': '请先登录'}), 401
    
    rating = data.get('rating', 0)
    comment = data.get('comment', '')
    
    from app.models import AgentRating
    existing = AgentRating.query.filter_by(user_id=user_id, agent_id=agent_id).first()
    
    if existing:
        existing.rating = rating
        existing.comment = comment
    else:
        agent_rating = AgentRating(
            user_id=user_id,
            agent_id=agent_id,
            rating=rating,
            comment=comment
        )
        db.session.add(agent_rating)
    
    db.session.commit()
    
    avg_rating = db.session.query(db.func.avg(AgentRating.rating)).filter_by(agent_id=agent_id).scalar() or 0
    
    return jsonify({
        'code': 0,
        'message': '评分成功',
        'data': {
            'rating': float(avg_rating),
            'count': AgentRating.query.filter_by(agent_id=agent_id).count()
        }
    })

@api_bp.route('/agents/<agent_id>/ratings', methods=['GET'])
def get_agent_ratings(agent_id):
    """获取智能体的所有评分"""
    from app.models import AgentRating
    ratings = AgentRating.query.filter_by(agent_id=agent_id).order_by(
        AgentRating.created_at.desc()
    ).all()
    
    avg_rating = db.session.query(db.func.avg(AgentRating.rating)).filter_by(agent_id=agent_id).scalar() or 0
    
    return jsonify({
        'code': 0,
        'data': {
            'ratings': [r.to_dict() for r in ratings],
            'average': float(avg_rating),
            'count': len(ratings)
        }
    })
