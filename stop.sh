#!/bin/bash

# AgentHub 停止脚本
# 停止所有相关服务

echo "🛑 正在停止 AgentHub..."

# 停止 Flask 应用
if pkill -f "python app_v1.py" 2>/dev/null; then
    echo "   ✅ Flask 服务已停止"
else
    echo "   ℹ️  Flask 服务未运行"
fi

# 停止 OpenCode 服务
if pkill -f "opencode serve" 2>/dev/null; then
    echo "   ✅ OpenCode 服务已停止"
else
    echo "   ℹ️  OpenCode 服务未运行"
fi

# 释放端口
for port in 5000 8080; do
    if lsof -i:$port >/dev/null 2>&1; then
        lsof -ti:$port | xargs -r kill -9 2>/dev/null
        echo "   🔌 端口 $port 已释放"
    fi
done

echo ""
echo "✅ 所有服务已停止"
