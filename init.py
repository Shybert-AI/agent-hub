#!/usr/bin/env python3
"""
初始化脚本 - 创建必要的目录和文件
"""

import os
import sys

def init_project():
    dirs = [
        'logs',
        'instance',
    ]
    
    for d in dirs:
        os.makedirs(d, exist_ok=True)
        print(f"✓ 创建目录: {d}")
    
    # 创建 .env.example
    if not os.path.exists('.env.example'):
        with open('.env.example', 'w') as f:
            f.write("""# Flask
SECRET_KEY=your-secret-key-here
FLASK_ENV=development

# DeepSeek API
DEEPSEEK_API_KEY=your-deepseek-api-key

# OpenCode
OPENCODE_API_URL=http://localhost:8080
""")
        print("✓ 创建文件: .env.example")
    
    # 创建 .gitignore
    if not os.path.exists('.gitignore'):
        with open('.gitignore', 'w') as f:
            f.write("""__pycache__/
*.py[cod]
*$py.class
*.so
.Python
env/
venv/
instance/
.env
.flaskenv
*.log
logs/*.log
*.db
*.sqlite
.DS_Store
.idea/
.vscode/
""")
        print("✓ 创建文件: .gitignore")
    
    print("\n✅ 初始化完成！")
    print("\n下一步:")
    print("1. 复制 .env.example 为 .env 并配置")
    print("2. 运行: pip install -r requirements.txt")
    print("3. 运行: python app.py")
    print("4. 访问: http://localhost:5000")

if __name__ == '__main__':
    init_project()
