"""
对话服务 - 处理与 DeepSeek 和 OpenCode 的通信
"""

import os
import json
import logging
import requests
from typing import Generator, Dict, List

logger = logging.getLogger(__name__)

class DialogueService:
    def __init__(self):
        self.deepseek_api_key = os.environ.get('DEEPSEEK_API_KEY', '')
        self.deepseek_base_url = 'https://api.deepseek.com/v1'
        self.opencode_url = os.environ.get('OPENCODE_API_URL', 'http://localhost:8080')
    
    def chat_with_deepseek(
        self, 
        messages: List[Dict], 
        model: str = "deepseek-chat",
        stream: bool = True,
        api_key: str = None
    ) -> Generator[str, None, None]:
        """调用 DeepSeek API"""
        deepseek_api_key = api_key or self.deepseek_api_key
        if not deepseek_api_key:
            yield "错误: 未配置 DeepSeek API Key，请在设置页面配置"
            return
        
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {deepseek_api_key}'
        }
        
        payload = {
            'model': model,
            'messages': messages,
            'stream': stream,
            'temperature': 0.7,
            'max_tokens': 4096
        }
        
        try:
            response = requests.post(
                f'{self.deepseek_base_url}/chat/completions',
                headers=headers,
                json=payload,
                stream=stream,
                timeout=120
            )
            
            if response.status_code != 200:
                yield f"API 错误: {response.status_code} - {response.text}"
                return
            
            for line in response.iter_lines():
                if line:
                    line = line.decode('utf-8')
                    if line.startswith('data: '):
                        data = line[6:]
                        if data == '[DONE]':
                            break
                        try:
                            chunk = json.loads(data)
                            content = chunk.get('choices', [{}])[0].get('delta', {}).get('content', '')
                            if content:
                                yield content
                        except json.JSONDecodeError:
                            continue
                            
        except requests.exceptions.Timeout:
            yield "请求超时，请重试"
        except Exception as e:
            yield f"发生错误: {str(e)}"
    
    def chat_with_opencode(
        self,
        message: str,
        agent_id: str = None,
        session_id: str = None,
        agent: Dict = None
    ) -> Generator[str, None, None]:
        """调用 OpenCode API"""
        try:
            if not session_id:
                create_url = f'{self.opencode_url}/session'
                logger.info(f"[OpenCode] 创建新 session: {create_url}")
                resp = requests.post(create_url, json={}, timeout=30)
                if resp.status_code != 200:
                    yield f"创建 session 失败: {resp.status_code}"
                    return
                session_data = resp.json()
                session_id = session_data.get('id')
                logger.info(f"[OpenCode] Session 创建成功: {session_id}")

            url = f'{self.opencode_url}/session/{session_id}/message'
            logger.info(f"[OpenCode] 发送消息到: {url}")
            
            payload = {
                'parts': [{'type': 'text', 'text': message}]
            }
            
            if agent and agent.get('system_prompt'):
                payload['system'] = agent.get('system_prompt')
                logger.info(f"[OpenCode] 添加 system prompt ({agent.get('name')}): {len(agent.get('system_prompt', ''))} 字符")
            
            response = requests.post(
                url,
                json=payload,
                timeout=300
            )
            
            logger.info(f"[OpenCode] 响应状态码: {response.status_code}")
            
            if response.status_code != 200:
                logger.error(f"[OpenCode] API 错误: {response.status_code} - {response.text[:500]}")
                yield f"OpenCode API 错误: {response.status_code}"
                return
            
            result = response.json()
            parts = result.get('parts', [])
            
            for part in parts:
                if part.get('type') == 'text':
                    text = part.get('text', '')
                    if text:
                        yield text
                            
        except requests.exceptions.ConnectionError as e:
            logger.error(f"[OpenCode] 连接失败: {e}")
            yield "无法连接到 OpenCode 服务，请确保 OpenCode 正在运行"
        except requests.exceptions.Timeout:
            logger.error("[OpenCode] 请求超时")
            yield "请求超时，请重试"
        except Exception as e:
            logger.error(f"[OpenCode] 未知错误: {e}")
            yield f"发生错误: {str(e)}"
    
    def chat_with_agent(
        self,
        agent_id: str,
        user_message: str,
        conversation_history: List[Dict] = None,
        use_opencode: bool = True,
        deepseek_api_key: str = None,
        model: str = "deepseek-chat",
        agent: Dict = None
    ) -> Generator[str, None, None]:
        """使用指定智能体进行对话"""
        if not agent:
            yield f"未找到智能体: {agent_id}"
            return
        
        if use_opencode:
            yield from self.chat_with_opencode(
                message=user_message,
                agent_id=agent_id,
                agent=agent
            )
        else:
            messages = []
            if agent.get('system_prompt'):
                messages.append({
                    'role': 'system',
                    'content': agent['system_prompt']
                })
            
            if conversation_history:
                for msg in conversation_history[-10:]:
                    messages.append({
                        'role': msg.get('role', 'user'),
                        'content': msg.get('content', '')
                    })
            
            messages.append({
                'role': 'user', 
                'content': user_message
            })
            
            yield from self.chat_with_deepseek(messages, model=model, api_key=deepseek_api_key)

dialogue_service = DialogueService()
