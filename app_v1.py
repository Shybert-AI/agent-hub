"""
AgentHub - 智能体管理系统
Multi-Agent Management System
"""

import socket
import subprocess
import os
import logging
from flask import Flask, session, redirect, url_for
from functools import wraps
from app.routes.main import main_bp
from app.routes.api import api_bp
from app.routes.agents import agents_bp
from app.routes.auth import auth_bp
from app.models import db
from app.services.agent_manager import AgentManager

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def create_app():
    app = Flask(__name__, template_folder='app/templates', static_folder='app/static')
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
    app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///agenthub.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    db.init_app(app)
    
    with app.app_context():
        db.create_all()
    
    app.register_blueprint(main_bp)
    app.register_blueprint(api_bp, url_prefix='/api')
    app.register_blueprint(agents_bp, url_prefix='/agents')
    app.register_blueprint(auth_bp)
    
    app.agent_manager = AgentManager()
    
    return app

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function

def is_port_in_use(port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('localhost', port)) == 0

def kill_port(port):
    try:
        result = subprocess.run(['lsof', '-ti', str(port)], capture_output=True, text=True)
        pids = result.stdout.strip().split('\n')
        for pid in pids:
            if pid:
                subprocess.run(['kill', '-9', pid])
                print(f"Killed process {pid} on port {port}")
    except Exception as e:
        print(f"Failed to kill process on port {port}: {e}")

if __name__ == '__main__':
    port = 5000
    if is_port_in_use(port):
        print(f"Port {port} is in use, killing existing process...")
        kill_port(port)
    app = create_app()
    app.run(debug=True, host='0.0.0.0', port=port)
