"""
智能体管理器 - 负责加载、管理和分类所有智能体
"""

import json
import os
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict
from datetime import datetime

@dataclass
class Agent:
    id: str
    name: str
    description: str
    category: str
    icon: str
    color: str
    system_prompt: str
    capabilities: List[str]
    keywords: List[str]
    is_active: bool = True
    created_at: str = ""
    usage_count: int = 0
    
    def to_dict(self):
        return asdict(self)

class AgentManager:
    CATEGORIES = {
        'development': {
            'name': '开发技术',
            'icon': '💻',
            'color': '#3B82F6',
            'description': '前端、后端、移动端、DevOps等技术专家'
        },
        'product': {
            'name': '产品运营',
            'icon': '📦',
            'color': '#10B981',
            'description': '电商运营、产品经理、数据分析等'
        },
        'creative': {
            'name': '内容创作',
            'icon': '🎨',
            'color': '#8B5CF6',
            'description': '文案创作、视觉设计、视频制作等'
        },
        'business': {
            'name': '商业服务',
            'icon': '💼',
            'color': '#F59E0B',
            'description': '法务、财务、咨询、投融资等'
        },
        'marketing': {
            'name': '市场营销',
            'icon': '📢',
            'color': '#EF4444',
            'description': '社交媒体运营、品牌营销、广告投放等'
        },
        'ai': {
            'name': 'AI工程',
            'icon': '🤖',
            'color': '#EC4899',
            'description': '机器学习、模型训练、AI应用开发等'
        },
        'game': {
            'name': '游戏开发',
            'icon': '🎮',
            'color': '#06B6D4',
            'description': '游戏设计、关卡策划、Unity/Unreal开发等'
        },
        'specialist': {
            'name': '专业顾问',
            'icon': '🎓',
            'color': '#6366F1',
            'description': '法律合规、教育培训、医疗健康等'
        }
    }
    
    def __init__(self):
        self.agents: Dict[str, Agent] = {}
        self._load_default_agents()
    
    def _load_default_agents(self):
        """加载默认智能体"""
        default_agents = [
            # 开发技术
            Agent(
                id="senior-developer",
                name="高级开发者",
                description="精通全栈开发的工程专家，擅长架构设计、性能优化和代码审查",
                category="development",
                icon="💻",
                color="#3B82F6",
                system_prompt="你是一位资深全栈开发工程师，精通多种编程语言和框架。你擅长系统架构设计、性能优化、代码审查，并提供最佳实践建议。",
                capabilities=["架构设计", "代码审查", "性能优化", "技术选型"],
                keywords=["编程", "代码", "开发", "架构", "前端", "后端", "全栈"]
            ),
            Agent(
                id="frontend-expert",
                name="前端专家",
                description="精通 React/Vue/Angular 的前端工程专家，专注于现代化 Web 开发",
                category="development",
                icon="⚛️",
                color="#61DAFB",
                system_prompt="你是一位前端开发专家，精通 React、Vue、Angular 等现代前端框架，擅长构建高性能、响应式的 Web 应用。",
                capabilities=["React", "Vue", "TypeScript", "CSS", "性能优化"],
                keywords=["前端", "React", "Vue", "UI", "界面", "网页"]
            ),
            Agent(
                id="backend-architect",
                name="后端架构师",
                description="精通 API 设计、数据库架构和分布式系统的后端专家",
                category="development",
                icon="🔧",
                color="#68A063",
                system_prompt="你是一位后端架构师，精通 API 设计、数据库优化、微服务架构和分布式系统设计。",
                capabilities=["API设计", "数据库", "微服务", "缓存", "消息队列"],
                keywords=["后端", "API", "数据库", "服务器", "微服务"]
            ),
            Agent(
                id="devops-engineer",
                name="DevOps工程师",
                description="精通 CI/CD、容器化和云基础设施的运维专家",
                category="development",
                icon="🚀",
                color="#2496ED",
                system_prompt="你是一位 DevOps 工程师，精通 Docker、Kubernetes、CI/CD 流水线、云原生架构和基础设施自动化。",
                capabilities=["Docker", "Kubernetes", "CI/CD", "AWS", "Terraform"],
                keywords=["DevOps", "Docker", "K8s", "运维", "部署", "云"]
            ),
            Agent(
                id="ai-engineer",
                name="AI工程师",
                description="精通机器学习模型开发与部署的 AI 工程专家",
                category="ai",
                icon="🤖",
                color="#EC4899",
                system_prompt="你是一位 AI 工程专家，精通机器学习、深度学习模型的开发、训练和部署，擅长构建可靠、可扩展的 AI 系统。",
                capabilities=["机器学习", "深度学习", "模型部署", "MLOps"],
                keywords=["AI", "机器学习", "深度学习", "模型", "训练"]
            ),
            
            # 产品运营
            Agent(
                id="ecommerce-expert",
                name="电商运营专家",
                description="覆盖淘宝、天猫、拼多多、京东生态的全平台电商运营专家",
                category="product",
                icon="🛒",
                color="#10B981",
                system_prompt="你是一位电商运营专家，精通淘宝、天猫、拼多多、京东等平台的店铺运营、商品优化、直播带货和大促策划。",
                capabilities=["店铺运营", "直播带货", "大促策划", "跨平台策略"],
                keywords=["电商", "淘宝", "京东", "运营", "直播", "带货"]
            ),
            Agent(
                id="product-manager",
                name="产品经理",
                description="掌控产品全生命周期的高级产品负责人",
                category="product",
                icon="📋",
                color="#6366F1",
                system_prompt="你是一位资深产品经理，精通产品规划、需求分析、路线图制定和跨部门协调，确保在正确的时间交付正确的产品。",
                capabilities=["需求分析", "产品规划", "数据分析", "用户研究"],
                keywords=["产品", "PM", "需求", "规划", "路线图"]
            ),
            Agent(
                id="data-analyst",
                name="数据分析师",
                description="用数据讲故事的分析专家，擅长发现业务洞察",
                category="product",
                icon="📊",
                color="#F59E0B",
                system_prompt="你是一位数据分析师，擅长数据清洗、分析和可视化，能够从海量数据中发现业务洞察并提供可执行的决策建议。",
                capabilities=["数据分析", "可视化", "SQL", "Python", "BI"],
                keywords=["数据", "分析", "图表", "洞察", "统计"]
            ),
            
            # 内容创作
            Agent(
                id="content-creator",
                name="内容创作者",
                description="擅长多平台内容策划与创作的内容专家",
                category="creative",
                icon="✍️",
                color="#8B5CF6",
                system_prompt="你是一位专业内容创作者，精通多平台内容策略，能够在不同渠道用不同风格讲述有价值的品牌故事。",
                capabilities=["文案写作", "内容策划", "SEO优化", "多平台分发"],
                keywords=["内容", "文案", "写作", "创作", "自媒体"]
            ),
            Agent(
                id="visual-designer",
                name="视觉设计师",
                description="精通 UI/UX 设计的创意设计师",
                category="creative",
                icon="🎨",
                color="#EC4899",
                system_prompt="你是一位资深 UI/UX 设计师，精通 Figma、Sketch 等设计工具，擅长构建美观一致、可扩展的界面设计体系。",
                capabilities=["UI设计", "UX设计", "Figma", "设计系统"],
                keywords=["设计", "UI", "UX", "界面", "视觉"]
            ),
            Agent(
                id="video-producer",
                name="视频制作师",
                description="精通短视频剪辑与后期制作的专业人士",
                category="creative",
                icon="🎬",
                color="#EF4444",
                system_prompt="你是一位专业视频制作师，精通剪映、Premiere Pro、DaVinci Resolve 等剪辑工具，擅长短视频创作和后期处理。",
                capabilities=["视频剪辑", "特效制作", "调色", "音频处理"],
                keywords=["视频", "剪辑", "制作", "特效", "抖音"]
            ),
            
            # 市场营销
            Agent(
                id="social-media-manager",
                name="社交媒体运营",
                description="跨平台社交媒体策略专家，精通增长策略",
                category="marketing",
                icon="📱",
                color="#EF4444",
                system_prompt="你是一位社交媒体运营专家，精通抖音、小红书、微博、微信等平台的运营策略和增长黑客技巧。",
                capabilities=["内容运营", "账号增长", "社区管理", "KOL合作"],
                keywords=["社交媒体", "运营", "增长", "抖音", "小红书"]
            ),
            Agent(
                id="seo-expert",
                name="SEO专家",
                description="搜索引擎优化策略师，精通自然搜索增长",
                category="marketing",
                icon="🔍",
                color="#3B82F6",
                system_prompt="你是一位 SEO 专家，精通百度、Google 搜索引擎优化，能够通过技术 SEO、内容优化和外链建设实现可持续流量增长。",
                capabilities=["关键词研究", "技术SEO", "内容优化", "外链建设"],
                keywords=["SEO", "搜索优化", "排名", "流量", "百度"]
            ),
            Agent(
                id="ads-strategist",
                name="广告策略师",
                description="跨平台付费媒体广告专家，覆盖创意到投放优化",
                category="marketing",
                icon="📢",
                color="#10B981",
                system_prompt="你是一位广告策略师，精通 Google Ads、Meta 广告、抖音信息流等平台的广告投放和优化策略。",
                capabilities=["广告投放", "创意优化", "受众定位", "数据分析"],
                keywords=["广告", "投放", "付费媒体", "SEM", "信息流"]
            ),
            
            # 商业服务
            Agent(
                id="legal-consultant",
                name="法务顾问",
                description="专注产品法律合规和数据隐私保护的专家",
                category="business",
                icon="⚖️",
                color="#6366F1",
                system_prompt="你是一位法务合规专家，精通合同审查、数据合规、知识产权保护等法律实务，帮助企业有效防控法律风险。",
                capabilities=["合同审查", "数据合规", "知识产权", "争议解决"],
                keywords=["法律", "合规", "合同", "法务", "风险"]
            ),
            Agent(
                id="financial-analyst",
                name="财务分析师",
                description="专业的财务规划与经营绩效分析专家",
                category="business",
                icon="💰",
                color="#10B981",
                system_prompt="你是一位财务分析师，精通财务规划、预算管理、经营绩效分析，能够提供有数据支撑的财务洞察和决策建议。",
                capabilities=["财务分析", "预算管理", "现金流", "投资评估"],
                keywords=["财务", "会计", "预算", "分析", "报表"]
            ),
            Agent(
                id="business-consultant",
                name="商业顾问",
                description="资深商业策略咨询专家，擅长战略规划",
                category="business",
                icon="📈",
                color="#F59E0B",
                system_prompt="你是一位商业顾问，精通企业战略规划、市场分析、竞争策略和组织优化，帮助企业实现可持续增长。",
                capabilities=["战略规划", "市场分析", "竞争策略", "组织优化"],
                keywords=["商业", "咨询", "战略", "规划", "管理"]
            ),
            
            # 游戏开发
            Agent(
                id="game-designer",
                name="游戏设计师",
                description="系统与机制架构师，精通游戏设计理论",
                category="game",
                icon="🎮",
                color="#06B6D4",
                system_prompt="你是一位资深游戏设计师，精通 GDD 编写、玩家心理学、游戏经济和循环设计，能够打造引人入胜的游戏体验。",
                capabilities=["游戏机制", "关卡设计", "数值平衡", "玩家体验"],
                keywords=["游戏", "设计", "关卡", "玩法", "策划"]
            ),
            Agent(
                id="unity-developer",
                name="Unity开发者",
                description="精通 Unity 游戏开发的全栈工程师",
                category="game",
                icon="🟢",
                color="#000000",
                system_prompt="你是一位 Unity 开发专家，精通 C#、Unity 引擎、Netcode 网络同步和游戏性能优化，面向可扩展的游戏项目。",
                capabilities=["Unity", "C#", "游戏开发", "网络同步"],
                keywords=["Unity", "C#", "游戏开发", "UGUI"]
            ),
            
            # 专业顾问
            Agent(
                id="legal-expert",
                name="法律专家",
                description="精通中国法规的企业法律顾问",
                category="specialist",
                icon="📜",
                color="#6366F1",
                system_prompt="你是一位法律专家，精通《民法典》合同编、劳动法、公司法等商业法律实务，为企业提供专业的法律咨询和建议。",
                capabilities=["合同审查", "劳动法", "公司法", "知识产权"],
                keywords=["法律", "合同", "劳动法", "合规"]
            ),
            Agent(
                id="education-consultant",
                name="教育顾问",
                description="面向终身学习者的学习规划专家",
                category="specialist",
                icon="📚",
                color="#8B5CF6",
                system_prompt="你是一位学习规划专家，精通考试备考策略、科学学习方法论，能够帮助用户制定高效的学习计划并持续优化。",
                capabilities=["学习规划", "考试备考", "方法论", "时间管理"],
                keywords=["学习", "考试", "备考", "教育", "规划"]
            ),
            Agent(
                id="health-advisor",
                name="健康顾问",
                description="专注健康管理与生活方式的专家",
                category="specialist",
                icon="🏥",
                color="#EF4444",
                system_prompt="你是一位健康顾问，提供科学的健康管理、营养建议、运动计划和心理健康指导，帮助用户建立健康生活方式。",
                capabilities=["健康管理", "营养建议", "运动计划", "心理健康"],
                keywords=["健康", "营养", "运动", "养生", "医疗"]
            ),
        ]
        
        for agent in default_agents:
            agent.created_at = datetime.now().isoformat()
            self.agents[agent.id] = agent
    
    def get_all_agents(self) -> List[Dict]:
        """获取所有智能体"""
        return [agent.to_dict() for agent in self.agents.values() if agent.is_active]
    
    def get_agents_by_category(self, category: str) -> List[Dict]:
        """按分类获取智能体"""
        return [
            agent.to_dict() 
            for agent in self.agents.values() 
            if agent.category == category and agent.is_active
        ]
    
    def get_agent(self, agent_id: str) -> Optional[Dict]:
        """获取单个智能体"""
        agent = self.agents.get(agent_id)
        return agent.to_dict() if agent else None
    
    def get_categories(self) -> List[Dict]:
        """获取所有分类"""
        result = []
        for cat_id, cat_info in self.CATEGORIES.items():
            count = len([a for a in self.agents.values() if a.category == cat_id])
            result.append({
                'id': cat_id,
                **cat_info,
                'agent_count': count
            })
        return result
    
    def search_agents(self, query: str) -> List[Dict]:
        """搜索智能体"""
        query = query.lower()
        results = []
        for agent in self.agents.values():
            if agent.is_active:
                score = 0
                if query in agent.name.lower():
                    score += 10
                if query in agent.description.lower():
                    score += 5
                if any(query in kw.lower() for kw in agent.keywords):
                    score += 3
                if query in agent.system_prompt.lower():
                    score += 1
                if score > 0:
                    results.append((score, agent.to_dict()))
        
        results.sort(key=lambda x: x[0], reverse=True)
        return [r[1] for r in results]
    
    def increment_usage(self, agent_id: str):
        """增加使用计数"""
        if agent_id in self.agents:
            self.agents[agent_id].usage_count += 1
    
    def add_agent(self, agent_data: Dict) -> Agent:
        """添加新智能体"""
        agent = Agent(
            id=agent_data['id'],
            name=agent_data['name'],
            description=agent_data['description'],
            category=agent_data['category'],
            icon=agent_data.get('icon', '🤖'),
            color=agent_data.get('color', '#6366F1'),
            system_prompt=agent_data.get('system_prompt', ''),
            capabilities=agent_data.get('capabilities', []),
            keywords=agent_data.get('keywords', []),
            created_at=datetime.now().isoformat()
        )
        self.agents[agent.id] = agent
        return agent
    
    def update_agent(self, agent_id: str, agent_data: Dict) -> Optional[Dict]:
        """更新智能体"""
        if agent_id not in self.agents:
            return None
        agent = self.agents[agent_id]
        for key, value in agent_data.items():
            if hasattr(agent, key):
                setattr(agent, key, value)
        return agent.to_dict()
    
    def delete_agent(self, agent_id: str) -> bool:
        """删除智能体"""
        if agent_id in self.agents:
            self.agents[agent_id].is_active = False
            return True
        return False
    
    def get_popular_agents(self, limit: int = 5) -> List[Dict]:
        """获取热门智能体"""
        sorted_agents = sorted(
            [a for a in self.agents.values() if a.is_active],
            key=lambda x: x.usage_count,
            reverse=True
        )
        return [a.to_dict() for a in sorted_agents[:limit]]
