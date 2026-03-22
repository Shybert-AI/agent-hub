from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from app.models import db, User

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login')
def login():
    if 'user_id' in session:
        return redirect(url_for('main.index'))
    return render_template('auth/login.html')

@auth_bp.route('/register')
def register():
    if 'user_id' in session:
        return redirect(url_for('main.index'))
    return render_template('auth/register.html')

@auth_bp.route('/api/auth/login', methods=['POST'])
def api_login():
    data = request.get_json()
    email = data.get('email', '').strip()
    password = data.get('password', '')
    
    if not email or not password:
        return jsonify({'code': 1, 'message': '邮箱和密码不能为空'}), 400
    
    user = User.query.filter_by(email=email).first()
    
    if not user or not check_password_hash(user.password_hash, password):
        return jsonify({'code': 1, 'message': '邮箱或密码错误'}), 401
    
    session.permanent = True
    session['user_id'] = user.id
    session['username'] = user.username
    session['email'] = user.email
    
    return jsonify({
        'code': 0, 
        'message': '登录成功',
        'data': user.to_dict()
    })

@auth_bp.route('/api/auth/register', methods=['POST'])
def api_register():
    data = request.get_json()
    username = data.get('username', '').strip()
    email = data.get('email', '').strip()
    password = data.get('password', '')
    confirm_password = data.get('confirm_password', '')
    
    if not username or not email or not password:
        return jsonify({'code': 1, 'message': '所有字段都不能为空'}), 400
    
    if len(username) < 2 or len(username) > 32:
        return jsonify({'code': 1, 'message': '用户名长度需在2-32个字符之间'}), 400
    
    if len(password) < 6:
        return jsonify({'code': 1, 'message': '密码长度至少6个字符'}), 400
    
    if password != confirm_password:
        return jsonify({'code': 1, 'message': '两次密码输入不一致'}), 400
    
    if User.query.filter_by(email=email).first():
        return jsonify({'code': 1, 'message': '该邮箱已被注册'}), 400
    
    if User.query.filter_by(username=username).first():
        return jsonify({'code': 1, 'message': '该用户名已被使用'}), 400
    
    user = User(
        username=username,
        email=email,
        password_hash=generate_password_hash(password)
    )
    db.session.add(user)
    db.session.commit()
    
    session.permanent = True
    session['user_id'] = user.id
    session['username'] = user.username
    session['email'] = user.email
    
    return jsonify({
        'code': 0, 
        'message': '注册成功',
        'data': user.to_dict()
    })

@auth_bp.route('/api/auth/logout', methods=['POST'])
def logout():
    session.clear()
    return jsonify({'code': 0, 'message': '已退出登录'})

@auth_bp.route('/api/auth/current-user')
def current_user():
    if 'user_id' in session:
        return jsonify({
            'code': 0,
            'data': {
                'id': session.get('user_id'),
                'username': session.get('username'),
                'email': session.get('email')
            }
        })
    return jsonify({'code': 1, 'message': '未登录', 'data': None})
