/**
 * AgentHub Chat Page JavaScript
 */

class ChatApp {
    constructor() {
        this.currentAgent = null;
        this.messages = [];
        this.isStreaming = false;
        this.currentConversationId = null;
        this.conversations = JSON.parse(localStorage.getItem('conversations') || '{}');
        
        this.initElements();
        this.initEvents();
        this.loadAgents();
        this.loadSettings();
        this.loadTheme();
        this.loadConversationList();
        
        // 检查 URL 参数中的 agent
        const urlParams = new URLSearchParams(window.location.search);
        const agentId = urlParams.get('agent');
        if (agentId) {
            this.selectAgent(agentId);
        }
    }
    
    loadTheme() {
        const savedTheme = localStorage.getItem('theme') || 'dark';
        if (savedTheme === 'light') {
            document.documentElement.setAttribute('data-theme', 'light');
        }
    }
    
    initElements() {
        this.chatInput = document.getElementById('chatInput');
        this.sendBtn = document.getElementById('sendBtn');
        this.messagesList = document.getElementById('messagesList');
        this.loadingIndicator = document.getElementById('loadingIndicator');
        this.welcomeMessage = document.getElementById('welcomeMessage');
        this.agentCategories = document.getElementById('agentCategories');
        this.currentAgentEl = document.getElementById('currentAgent');
        this.currentAgentDetail = document.getElementById('currentAgentDetail');
        this.settingsPanel = document.getElementById('settingsPanel');
        this.agentSearch = document.getElementById('agentSearch');
        this.useOpencodeCheckbox = document.getElementById('useOpencode');
    }
    
    initEvents() {
        // 发送消息
        this.sendBtn.addEventListener('click', () => this.sendMessage());
        this.chatInput.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                this.sendMessage();
            }
        });
        
        // 自动调整输入框高度
        this.chatInput.addEventListener('input', () => {
            this.chatInput.style.height = 'auto';
            this.chatInput.style.height = Math.min(this.chatInput.scrollHeight, 200) + 'px';
        });
        
        // 切换侧边栏
        document.getElementById('toggleSidebar').addEventListener('click', () => {
            document.getElementById('chatSidebar').classList.toggle('collapsed');
        });
        
        // 切换设置面板
        document.getElementById('toggleSettings').addEventListener('click', () => {
            this.settingsPanel.classList.toggle('open');
        });
        
        document.getElementById('closeSettings').addEventListener('click', () => {
            this.settingsPanel.classList.remove('open');
        });
        
        // 清空对话
        document.getElementById('clearChat').addEventListener('click', () => {
            this.clearChat();
        });
        
        // 搜索智能体
        this.agentSearch.addEventListener('input', (e) => {
            this.filterAgents(e.target.value);
        });
    }
    
    async loadAgents() {
        try {
            const [categoriesRes, agentsRes] = await Promise.all([
                fetch('/api/agents/categories'),
                fetch('/api/agents')
            ]);
            
            const categories = await categoriesRes.json();
            const agents = await agentsRes.json();
            
            this.renderCategories(categories.data, agents.data);
        } catch (error) {
            console.error('加载智能体失败:', error);
            this.showToast('加载智能体失败', 'error');
        }
    }
    
    renderCategories(categories, agents) {
        this.agentCategories.innerHTML = categories.map(cat => {
            const categoryAgents = agents.filter(a => a.category === cat.id);
            return `
                <div class="agent-category-group" data-category="${cat.id}">
                    <div class="category-header" onclick="this.classList.toggle('expanded')">
                        <span class="category-icon">${cat.icon}</span>
                        <span class="category-name">${cat.name}</span>
                        <span class="category-count">${categoryAgents.length}</span>
                        <svg class="expand-icon" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                            <polyline points="6 9 12 15 18 9"/>
                        </svg>
                    </div>
                    <div class="category-agents">
                        ${categoryAgents.map(agent => `
                            <div class="agent-item" data-agent-id="${agent.id}" onclick="chatApp.selectAgent('${agent.id}')">
                                <div class="agent-icon" style="background: ${agent.color}20;">
                                    ${agent.icon}
                                </div>
                                <span class="agent-name">${agent.name}</span>
                            </div>
                        `).join('')}
                    </div>
                </div>
            `;
        }).join('');
        
        // 默认展开第一个分类
        const firstCategory = this.agentCategories.querySelector('.category-header');
        if (firstCategory) {
            firstCategory.classList.add('expanded');
        }
    }
    
    filterAgents(query) {
        const items = this.agentCategories.querySelectorAll('.agent-item');
        const groups = this.agentCategories.querySelectorAll('.agent-category-group');
        
        query = query.toLowerCase();
        
        items.forEach(item => {
            const name = item.querySelector('.agent-name').textContent.toLowerCase();
            item.style.display = name.includes(query) ? 'flex' : 'none';
        });
        
        groups.forEach(group => {
            const visibleItems = group.querySelectorAll('.agent-item[style="flex"], .agent-item:not([style])');
            const hasVisible = Array.from(group.querySelectorAll('.agent-item')).some(
                item => item.style.display !== 'none'
            );
            group.style.display = hasVisible ? 'block' : 'none';
        });
    }
    
    async selectAgent(agentId) {
        try {
            const res = await fetch(`/api/agents/${agentId}`);
            const data = await res.json();
            
            if (data.code === 0) {
                this.currentAgent = data.data;
                this.updateCurrentAgentUI();
                
                // 更新选中状态
                document.querySelectorAll('.agent-item').forEach(item => {
                    item.classList.toggle('active', item.dataset.agentId === agentId);
                });
                
                // 更新 URL
                const url = new URL(window.location);
                url.searchParams.set('agent', agentId);
                window.history.pushState({}, '', url);
                
                // 切换到对话模式
                this.welcomeMessage.style.display = 'none';
            }
        } catch (error) {
            console.error('选择智能体失败:', error);
            this.showToast('选择智能体失败', 'error');
        }
    }
    
    updateCurrentAgentUI() {
        if (!this.currentAgent) return;
        
        const html = `
            <div class="agent-avatar-sm" style="background: ${this.currentAgent.color};">
                ${this.currentAgent.icon}
            </div>
            <div class="agent-info">
                <div class="agent-name">${this.currentAgent.name}</div>
                <div class="agent-status">在线</div>
            </div>
        `;
        this.currentAgentEl.innerHTML = html;
        
        const detailHtml = `
            <div class="agent-avatar-lg" style="background: ${this.currentAgent.color};">
                ${this.currentAgent.icon}
            </div>
            <div>
                <div class="agent-name">${this.currentAgent.name}</div>
                <div class="agent-desc">${this.currentAgent.description}</div>
            </div>
        `;
        this.currentAgentDetail.innerHTML = detailHtml;
    }
    
    async sendMessage() {
        const message = this.chatInput.value.trim();
        if (!message || this.isStreaming) return;
        
        // 如果没有选择智能体，使用默认
        if (!this.currentAgent) {
            this.currentAgent = {
                id: 'default',
                name: '默认助手',
                icon: '🤖',
                color: '#6366F1'
            };
            this.updateCurrentAgentUI();
        }
        
        // 清空输入框
        this.chatInput.value = '';
        this.chatInput.style.height = 'auto';
        
        // 隐藏欢迎消息
        this.welcomeMessage.style.display = 'none';
        
        // 添加用户消息
        this.addMessage('user', message);
        
        // 显示加载指示器
        this.loadingIndicator.style.display = 'flex';
        this.isStreaming = true;
        
        try {
            const useOpencode = this.useOpencodeCheckbox.checked;
            const deepseekApiKey = localStorage.getItem('deepseekApiKey') || '';
            const model = document.getElementById('modelSelect')?.value || 'deepseek-chat';
            
            const response = await fetch('/api/chat', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    message,
                    agent_id: this.currentAgent.id,
                    use_opencode: useOpencode,
                    deepseek_api_key: deepseekApiKey,
                    model: model
                })
            });
            
            // 创建助手消息元素
            const assistantMsg = this.addMessage('assistant', '');
            
            // 处理流式响应
            const reader = response.body.getReader();
            const decoder = new TextDecoder();
            let fullContent = '';
            
            while (true) {
                const { done, value } = await reader.read();
                if (done) break;
                
                const chunk = decoder.decode(value);
                const lines = chunk.split('\n');
                
                for (const line of lines) {
                    if (line.startsWith('data: ')) {
                        const data = line.slice(6);
                        if (data === '[DONE]') continue;
                        
                        try {
                            const parsed = JSON.parse(data);
                            if (parsed.content) {
                                fullContent += parsed.content;
                                assistantMsg.querySelector('.message-bubble').innerHTML = this.renderMarkdown(fullContent);
                                this.scrollToBottom();
                            }
                        } catch (e) {
                            // 忽略解析错误
                        }
                    }
                }
            }
            
            // 保存对话
            this.saveConversation(message, fullContent);
            
        } catch (error) {
            console.error('发送消息失败:', error);
            assistantMsg.querySelector('.message-bubble').innerHTML = `
                <p style="color: var(--danger-color);">
                    发送消息失败: ${error.message}<br>
                    请检查 OpenCode 服务是否运行，或尝试关闭「使用 OpenCode」选项。
                </p>
            `;
            this.showToast('发送消息失败', 'error');
        } finally {
            this.loadingIndicator.style.display = 'none';
            this.isStreaming = false;
        }
    }
    
    addMessage(role, content) {
        const messageEl = document.createElement('div');
        messageEl.className = `message ${role}`;
        
        const avatar = role === 'user' ? '👤' : (this.currentAgent?.icon || '🤖');
        const avatarBg = role === 'user' ? 'var(--primary-color)' : (this.currentAgent?.color || 'var(--secondary-color)');
        
        messageEl.innerHTML = `
            <div class="message-avatar" style="background: ${avatarBg};">
                ${avatar}
            </div>
            <div class="message-content">
                <div class="message-bubble">${this.renderMarkdown(content)}</div>
                <div class="message-actions">
                    <button class="message-action" onclick="chatApp.copyMessage(this)">
                        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                            <rect x="9" y="9" width="13" height="13" rx="2" ry="2"/>
                            <path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"/>
                        </svg>
                        复制
                    </button>
                    <button class="message-action" onclick="chatApp.regenerateMessage(this)">
                        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                            <polyline points="23 4 23 10 17 10"/>
                            <path d="M20.49 15a9 9 0 1 1-2.12-9.36L23 10"/>
                        </svg>
                        重新生成
                    </button>
                </div>
            </div>
        `;
        
        this.messagesList.appendChild(messageEl);
        this.scrollToBottom();
        
        return messageEl;
    }
    
    renderMarkdown(text) {
        if (!text) return '';
        
        // 简单的 Markdown 渲染
        let html = text
            // 代码块
            .replace(/```(\w*)\n([\s\S]*?)```/g, '<pre><code class="language-$1">$2</code></pre>')
            // 行内代码
            .replace(/`([^`]+)`/g, '<code>$1</code>')
            // 粗体
            .replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>')
            // 斜体
            .replace(/\*([^*]+)\*/g, '<em>$1</em>')
            // 链接
            .replace(/\[([^\]]+)\]\(([^)]+)\)/g, '<a href="$2" target="_blank">$1</a>')
            // 标题
            .replace(/^### (.+)$/gm, '<h3>$1</h3>')
            .replace(/^## (.+)$/gm, '<h2>$1</h2>')
            .replace(/^# (.+)$/gm, '<h1>$1</h1>')
            // 引用
            .replace(/^> (.+)$/gm, '<blockquote>$1</blockquote>')
            // 列表
            .replace(/^- (.+)$/gm, '<li>$1</li>')
            // 换行
            .replace(/\n/g, '<br>');
        
        // 包装列表项
        html = html.replace(/(<li>.*<\/li>)/gs, '<ul>$1</ul>');
        
        return html;
    }
    
    copyMessage(btn) {
        const bubble = btn.closest('.message').querySelector('.message-bubble');
        const text = bubble.innerText;
        
        navigator.clipboard.writeText(text).then(() => {
            this.showToast('已复制到剪贴板', 'success');
        });
    }
    
    regenerateMessage(btn) {
        const messageEl = btn.closest('.message');
        const prevUserMsg = messageEl.previousElementSibling;
        
        if (prevUserMsg && prevUserMsg.classList.contains('user')) {
            const userContent = prevUserMsg.querySelector('.message-bubble').innerText;
            messageEl.remove();
            prevUserMsg.remove();
            this.chatInput.value = userContent;
            this.sendMessage();
        }
    }
    
    clearChat() {
        if (confirm('确定要清空当前对话吗？')) {
            this.messagesList.innerHTML = '';
            this.welcomeMessage.style.display = 'block';
            this.messages = [];
            this.currentConversationId = null;
        }
    }
    
    scrollToBottom() {
        const chatMessages = document.getElementById('chatMessages');
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }
    
    saveConversation(userMsg, assistantMsg) {
        const id = Date.now().toString();
        if (!this.conversations[this.currentAgent.id]) {
            this.conversations[this.currentAgent.id] = [];
        }
        this.conversations[this.currentAgent.id].push({
            id,
            user: userMsg,
            assistant: assistantMsg,
            timestamp: new Date().toISOString()
        });
        localStorage.setItem('conversations', JSON.stringify(this.conversations));
    }
    
    loadSettings() {
        const settings = JSON.parse(localStorage.getItem('chatSettings') || '{}');
        if (settings.useOpencode !== undefined) {
            this.useOpencodeCheckbox.checked = settings.useOpencode;
        }
    }
    
    async loadConversationList() {
        try {
            const res = await fetch('/api/conversations');
            const data = await res.json();
            
            if (data.code === 0) {
                this.serverConversations = data.data;
                this.renderConversationList();
            }
        } catch (error) {
            console.error('加载对话列表失败:', error);
        }
    }
    
    renderConversationList() {
        const conversationList = document.getElementById('conversationList');
        if (!conversationList) return;
        
        if (!this.serverConversations || this.serverConversations.length === 0) {
            conversationList.innerHTML = '<div class="empty-state"><p>暂无历史对话</p></div>';
            return;
        }
        
        conversationList.innerHTML = this.serverConversations.map(conv => `
            <div class="conversation-item" data-id="${conv.id}" onclick="chatApp.loadConversation(${conv.id})">
                <span class="conversation-title">${conv.title}</span>
                <span class="conversation-time">${new Date(conv.updated_at).toLocaleDateString()}</span>
            </div>
        `).join('');
    }
    
    async loadConversation(convId) {
        try {
            const res = await fetch(`/api/conversations/${convId}`);
            const data = await res.json();
            
            if (data.code === 0) {
                this.currentConversationId = convId;
                this.messagesList.innerHTML = '';
                this.welcomeMessage.style.display = 'none';
                
                data.data.messages.forEach(msg => {
                    this.addMessage(msg.role, msg.content);
                });
            }
        } catch (error) {
            console.error('加载对话失败:', error);
        }
    }
    
    async saveConversation(userMsg, assistantMsg) {
        // 保存到服务器
        try {
            if (!this.currentConversationId) {
                const res = await fetch('/api/conversations', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        agent_id: this.currentAgent?.id || 'default',
                        title: userMsg.substring(0, 30) + '...'
                    })
                });
                const data = await res.json();
                if (data.code === 0) {
                    this.currentConversationId = data.data.id;
                    this.loadConversationList();
                }
            }
            
            // 保存用户消息
            await fetch(`/api/conversations/${this.currentConversationId}/messages`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    role: 'user',
                    content: userMsg
                })
            });
            
            // 保存助手消息
            await fetch(`/api/conversations/${this.currentConversationId}/messages`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    role: 'assistant',
                    content: assistantMsg
                })
            });
        } catch (error) {
            console.error('保存对话失败:', error);
        }
        
        // 同时保存到本地
        const id = Date.now().toString();
        if (!this.conversations[this.currentAgent.id]) {
            this.conversations[this.currentAgent.id] = [];
        }
        this.conversations[this.currentAgent.id].push({
            id,
            user: userMsg,
            assistant: assistantMsg,
            timestamp: new Date().toISOString()
        });
        localStorage.setItem('conversations', JSON.stringify(this.conversations));
    }
    
    saveSettings() {
        const settings = {
            useOpencode: this.useOpencodeCheckbox.checked
        };
        localStorage.setItem('chatSettings', JSON.stringify(settings));
    }
    
    showToast(message, type = 'info') {
        const container = document.getElementById('toastContainer');
        const toast = document.createElement('div');
        toast.className = `toast ${type}`;
        toast.innerHTML = `
            <span>${type === 'success' ? '✓' : type === 'error' ? '✕' : 'ℹ'}</span>
            <span>${message}</span>
        `;
        container.appendChild(toast);
        
        setTimeout(() => {
            toast.style.opacity = '0';
            setTimeout(() => toast.remove(), 300);
        }, 3000);
    }
}

// 全局函数
function sendQuickPrompt(prompt) {
    if (!window.chatApp) return;
    window.chatApp.chatInput.value = prompt;
    window.chatApp.sendMessage();
}

// 初始化
window.chatApp = new ChatApp();
