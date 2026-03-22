#!/bin/bash

# AgentHub 启动脚本
# 一键启动 AgentHub + OpenCode 服务

set -e

AGENCY_AGENTS_DIR="/root/agency-agents-zh-main"
CURRENT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "🚀 AgentHub 启动中..."

# 检查 Python 依赖
echo "📦 检查依赖..."
if ! pip show flask flask-sqlalchemy >/dev/null 2>&1; then
    echo "   安装 Python 依赖..."
    pip install -r requirements.txt
fi

# 检查 OpenCode
echo "🔧 检查 OpenCode..."
if ! command -v opencode &> /dev/null; then
    echo "   正在安装 OpenCode..."
    curl -fsSL https://opencode.ai/install | bash
    source ~/.bashrc
fi

# 检查并复制 .opencode 目录
echo "📁 检查数字员工配置..."
if [ -d "$AGENCY_AGENTS_DIR/.opencode" ]; then
    if [ ! -d "$CURRENT_DIR/.opencode" ] || [ "$AGENCY_AGENTS_DIR/.opencode" -nt "$CURRENT_DIR/.opencode" ]; then
        echo "   复制数字员工配置..."
        cp -r "$AGENCY_AGENTS_DIR/.opencode" "$CURRENT_DIR/"
    fi
else
    echo "⚠️  警告: 未找到 agency-agents 的 .opencode 目录"
    echo "   请先安装: git clone https://github.com/anomalyco/agency-agents-zh.git"
fi

# 清理占用端口的进程
cleanup_port() {
    local port=$1
    if lsof -i:$port >/dev/null 2>&1; then
        echo "   释放端口 $port..."
        lsof -ti:$port | xargs -r kill -9 2>/dev/null || true
        sleep 1
    fi
}

cleanup_port 5000
cleanup_port 8080

# 启动 Flask 应用
echo "📦 启动 Web 服务 (端口 5000)..."
cd "$CURRENT_DIR"
python app_v1.py &
APP_PID=$!

# 等待服务启动
sleep 3

# 启动 OpenCode 服务
echo "🤖 启动 OpenCode 服务 (端口 8080)..."
opencode serve --port 8080 &
OPENCODE_PID=$!

echo ""
echo "═══════════════════════════════════════════"
echo "  ✅ AgentHub 已启动!"
echo ""
echo "  📱 Web 界面:  http://localhost:5000"
echo "  🔧 OpenCode:  http://localhost:8080"
echo ""
echo "  按 Ctrl+C 停止所有服务"
echo "═══════════════════════════════════════════"

# 捕获 Ctrl+C 信号
trap "echo ''; echo '🛑 正在停止服务...'; kill $APP_PID $OPENCODE_PID 2>/dev/null; echo '✅ 已停止'; exit" INT TERM

# 等待所有后台进程
wait
