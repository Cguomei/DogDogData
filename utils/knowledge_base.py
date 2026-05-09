"""
AI助手知识库系统
提供基于本地知识的快速问答，减少对模型的依赖
"""
import json
import os
from datetime import datetime
from typing import Optional, Dict, List


class KnowledgeBase:
    """本地知识库管理类"""
    
    def __init__(self, kb_file='data/knowledge_base.json'):
        """
        初始化知识库
        
        Args:
            kb_file: 知识库文件路径
        """
        self.kb_file = kb_file
        self.knowledge = {}
        self.stats = {
            'total_queries': 0,
            'kb_hits': 0,
            'kb_misses': 0,
            'last_updated': None
        }
        
        # 确保目录存在
        os.makedirs(os.path.dirname(kb_file), exist_ok=True)
        
        # 加载知识库
        self.load()
        
        # 如果没有数据，初始化默认知识
        if not self.knowledge:
            self._init_default_knowledge()
    
    def load(self):
        """从文件加载知识库"""
        try:
            if os.path.exists(self.kb_file):
                with open(self.kb_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.knowledge = data.get('knowledge', {})
                    self.stats = data.get('stats', self.stats)
                print(f"✅ 知识库加载成功: {len(self.knowledge)} 条知识")
            else:
                print("📝 知识库文件不存在，将创建新的")
        except Exception as e:
            print(f"⚠️  加载知识库失败: {e}")
            self.knowledge = {}
    
    def save(self):
        """保存知识库到文件"""
        try:
            self.stats['last_updated'] = datetime.now().isoformat()
            data = {
                'knowledge': self.knowledge,
                'stats': self.stats,
                'version': '1.0'
            }
            
            with open(self.kb_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            print(f"💾 知识库已保存: {len(self.knowledge)} 条知识")
        except Exception as e:
            print(f"❌ 保存知识库失败: {e}")
    
    def _init_default_knowledge(self):
        """初始化默认知识库"""
        print("📚 初始化默认知识库...")
        
        default_knowledge = {
            # 品种信息
            "泰迪的特点": {
                "question_patterns": ["泰迪.*特点", "泰迪.*怎么样", "泰迪犬介绍"],
                "answer": "🐕 **泰迪犬（贵宾犬）特点**\n\n"
                         "• **体型**: 小型犬，体重3-6kg\n"
                         "• **性格**: 聪明、活泼、粘人\n"
                         "• **智商**: 排名第2，非常易训练\n"
                         "• **毛发**: 卷曲不掉毛，需要定期美容\n"
                         "• **寿命**: 12-16年\n"
                         "• **适合人群**: 新手、公寓住户、老人\n\n"
                         "💡 **养护要点**: 每天梳毛、定期美容、适量运动",
                "category": "breed_info",
                "confidence": 0.95,
                "created_at": datetime.now().isoformat(),
                "usage_count": 0
            },
            
            "金毛的特点": {
                "question_patterns": ["金毛.*特点", "金毛.*怎么样", "金毛犬介绍"],
                "answer": "🐕 **金毛寻回犬特点**\n\n"
                         "• **体型**: 大型犬，体重25-35kg\n"
                         "• **性格**: 温顺、友善、忠诚\n"
                         "• **智商**: 排名第4，学习能力强\n"
                         "• **毛发**: 长毛，需要经常梳理\n"
                         "• **寿命**: 10-12年\n"
                         "• **适合人群**: 有院子、喜欢户外运动的家庭\n\n"
                         "💡 **养护要点**: 每天运动1-2小时、定期洗澡、注意髋关节健康",
                "category": "breed_info",
                "confidence": 0.95,
                "created_at": datetime.now().isoformat(),
                "usage_count": 0
            },
            
            "柯基的特点": {
                "question_patterns": ["柯基.*特点", "柯基.*怎么样", "柯基犬介绍"],
                "answer": "🐕 **柯基犬特点**\n\n"
                         "• **体型**: 中小型犬，体重10-14kg\n"
                         "• **性格**: 勇敢、警觉、活泼\n"
                         "• **智商**: 排名第11，聪明但有点固执\n"
                         "• **特征**: 短腿、大耳朵、蜜桃臀\n"
                         "• **寿命**: 12-15年\n"
                         "• **适合人群**: 活跃家庭、能接受掉毛的主人\n\n"
                         "💡 **养护要点**: 控制体重、保护脊椎、大量运动",
                "category": "breed_info",
                "confidence": 0.95,
                "created_at": datetime.now().isoformat(),
                "usage_count": 0
            },
            
            # 新手推荐
            "适合新手的狗狗": {
                "question_patterns": ["新手.*养.*狗", "第一次.*养狗", "适合.*新手"],
                "answer": "🌟 **适合新手养的狗狗推荐**\n\n"
                         "**1. 泰迪犬（贵宾犬）** ⭐⭐⭐⭐⭐\n"
                         "• 优点：聪明、不掉毛、体型小\n"
                         "• 难度：★☆☆☆☆\n\n"
                         "**2. 比熊犬** ⭐⭐⭐⭐⭐\n"
                         "• 优点：温顺、不掉毛、颜值高\n"
                         "• 难度：★☆☆☆☆\n\n"
                         "**3. 拉布拉多** ⭐⭐⭐⭐\n"
                         "• 优点：温顺、聪明、好训练\n"
                         "• 难度：★★☆☆☆\n\n"
                         "**4. 金毛** ⭐⭐⭐⭐\n"
                         "• 优点：友善、忠诚、稳定\n"
                         "• 难度：★★☆☆☆\n\n"
                         "💡 **新手建议**: 选择性格稳定、易训练的品种，避免哈士奇、边境牧羊犬等高能量犬种",
                "category": "recommendation",
                "confidence": 0.90,
                "created_at": datetime.now().isoformat(),
                "usage_count": 0
            },
            
            # 价格区间（通用知识）
            "狗狗价格区间": {
                "question_patterns": [".*价格.*多少", ".*多少钱", ".*价位"],
                "answer": "💰 **常见犬种价格参考**\n\n"
                         "• **泰迪**: ¥1000-5000（宠物级）\n"
                         "• **金毛**: ¥1500-6000（宠物级）\n"
                         "• **柯基**: ¥2000-8000（宠物级）\n"
                         "• **哈士奇**: ¥1500-5000（宠物级）\n"
                         "• **拉布拉多**: ¥1500-5000（宠物级）\n\n"
                         "⚠️ **注意**: \n"
                         "• 价格因地区、血统、品相差异很大\n"
                         "• 建议选择正规犬舍，避免星期狗\n"
                         "• 领养代替购买也是很好的选择\n\n"
                         "💡 我可以帮你查询具体品种的市场价格",
                "category": "price_query",
                "confidence": 0.85,
                "created_at": datetime.now().isoformat(),
                "usage_count": 0
            },
            
            # 养护知识
            "狗狗日常护理": {
                "question_patterns": ["怎么.*护理", "日常.*照顾", "养护.*知识"],
                "answer": "🏥 **狗狗日常护理指南**\n\n"
                         "**1. 饮食管理**\n"
                         "• 定时定量喂食\n"
                         "• 提供清洁饮用水\n"
                         "• 避免人类食物（巧克力、葡萄等有毒）\n\n"
                         "**2. 卫生护理**\n"
                         "• 每周洗澡1-2次\n"
                         "• 每天刷牙或每周3次\n"
                         "• 定期修剪指甲\n"
                         "• 清洁耳朵和眼睛\n\n"
                         "**3. 健康管理**\n"
                         "• 按时接种疫苗\n"
                         "• 定期驱虫（体内3个月/次，体外1个月/次）\n"
                         "• 每年体检一次\n\n"
                         "**4. 运动社交**\n"
                         "• 每天遛狗至少30分钟\n"
                         "• 适当社交训练\n"
                         "• 提供玩具和智力游戏",
                "category": "general_qa",
                "confidence": 0.90,
                "created_at": datetime.now().isoformat(),
                "usage_count": 0
            },
            
            # 训练技巧
            "定点排便训练": {
                "question_patterns": ["怎么.*定点.*排便", "如何.*上厕所", "训练.*大小便"],
                "answer": "🚽 **狗狗定点排便训练方法**\n\n"
                         "**第1步：准备工具**\n"
                         "• 尿垫或狗厕所\n"
                         "• 奖励零食\n"
                         "• 清洁剂（去除异味）\n\n"
                         "**第2步：建立规律**\n"
                         "• 饭后15-30分钟带它去指定地点\n"
                         "• 醒来后、玩耍后立即带去\n"
                         "• 每次停留5-10分钟\n\n"
                         "**第3步：正确引导**\n"
                         "• 在指定地点说固定口令（如\"上厕所\"）\n"
                         "• 成功后立即奖励零食+夸奖\n"
                         "• 失败时不要惩罚，默默清理\n\n"
                         "**第4步：巩固习惯**\n"
                         "• 坚持2-4周形成习惯\n"
                         "• 逐渐减少尿垫数量\n"
                         "• 偶尔犯错是正常的\n\n"
                         "💡 **关键**: 耐心+一致性+正向奖励",
                "category": "general_qa",
                "confidence": 0.92,
                "created_at": datetime.now().isoformat(),
                "usage_count": 0
            },
            
            # 对比知识
            "金毛vs泰迪对比": {
                "question_patterns": ["金毛.*泰迪.*对比", "金毛.*泰迪.*哪个.*好"],
                "answer": "⚖️ **金毛 vs 泰迪 对比分析**\n\n"
                         "| 项目 | 金毛 | 泰迪 |\n"
                         "|------|------|------|\n"
                         "| 体型 | 大型(25-35kg) | 小型(3-6kg) |\n"
                         "| 运动量 | 高(每天1-2h) | 低(每天30min) |\n"
                         "| 掉毛 | 严重 | 几乎不掉 |\n"
                         "| 美容 | 简单梳理 | 需定期美容 |\n"
                         "| 智商 | #4 | #2 |\n"
                         "| 寿命 | 10-12年 | 12-16年 |\n"
                         "| 空间需求 | 需要院子 | 公寓即可 |\n"
                         "| 价格 | ¥1500-6000 | ¥1000-5000 |\n\n"
                         "**选择建议**:\n"
                         "• 选**金毛**: 有大空间、喜欢户外、能接受掉毛\n"
                         "• 选**泰迪**: 住公寓、怕麻烦、想要聪明伴侣\n\n"
                         "💡 两种都是优秀犬种，关键看你的生活方式",
                "category": "comparison",
                "confidence": 0.88,
                "created_at": datetime.now().isoformat(),
                "usage_count": 0
            }
        }
        
        # 添加到知识库
        for key, value in default_knowledge.items():
            self.add_knowledge(key, value)
        
        self.save()
        print(f"✅ 默认知识库初始化完成: {len(default_knowledge)} 条")
    
    def add_knowledge(self, key: str, knowledge_item: dict):
        """
        添加知识条目
        
        Args:
            key: 知识键名
            knowledge_item: 知识内容
        """
        self.knowledge[key] = knowledge_item
    
    def search(self, question: str, category: str = None) -> Optional[dict]:
        """
        搜索知识库
        
        Args:
            question: 用户问题
            category: 问题类别（可选）
            
        Returns:
            匹配的知识条目，未找到返回None
        """
        import re
        
        self.stats['total_queries'] += 1
        
        best_match = None
        best_score = 0
        
        for key, item in self.knowledge.items():
            # 如果指定了类别，只搜索该类别
            if category and item.get('category') != category:
                continue
            
            # 检查问题模式匹配
            patterns = item.get('question_patterns', [])
            score = 0
            
            for pattern in patterns:
                if re.search(pattern, question, re.IGNORECASE):
                    score += 1
            
            # 也检查关键词匹配
            keywords = key.split()
            for keyword in keywords:
                if keyword in question:
                    score += 0.5
            
            # 更新最佳匹配
            if score > best_score:
                best_score = score
                best_match = item
        
        if best_match and best_score > 0:
            self.stats['kb_hits'] += 1
            best_match['usage_count'] = best_match.get('usage_count', 0) + 1
            print(f"📚 知识库命中: {best_match.get('category')} (得分: {best_score})")
            return best_match
        else:
            self.stats['kb_misses'] += 1
            print(f"🔍 知识库未命中")
            return None
    
    def add_from_model_response(self, question: str, answer: str, category: str, confidence: float = 0.7):
        """
        从模型回答中学习，添加到知识库
        
        Args:
            question: 用户问题
            answer: 模型回答
            category: 问题类别
            confidence: 置信度阈值
        """
        # 生成知识键
        key = self._generate_key(question)
        
        # 检查是否已存在
        if key in self.knowledge:
            print(f"⚠️  知识已存在，跳过: {key}")
            return
        
        # 添加新知识
        knowledge_item = {
            "question_patterns": [question],
            "answer": answer,
            "category": category,
            "confidence": confidence,
            "created_at": datetime.now().isoformat(),
            "usage_count": 0,
            "source": "model_learning"
        }
        
        self.add_knowledge(key, knowledge_item)
        self.save()
        print(f"📖 学习到新知识: {key}")
    
    def _generate_key(self, question: str) -> str:
        """
        从问题生成知识键
        
        Args:
            question: 用户问题
            
        Returns:
            知识键名
        """
        # 简化问题作为键
        # 移除标点符号
        import re
        key = re.sub(r'[？?！!。，、；：""''（）]', '', question)
        # 取前20个字符
        key = key[:20].strip()
        return key
    
    def get_stats(self) -> dict:
        """获取知识库统计信息"""
        total = len(self.knowledge)
        hits = self.stats.get('kb_hits', 0)
        misses = self.stats.get('kb_misses', 0)
        hit_rate = (hits / (hits + misses) * 100) if (hits + misses) > 0 else 0
        
        return {
            'total_knowledge': total,
            'total_queries': self.stats.get('total_queries', 0),
            'kb_hits': hits,
            'kb_misses': misses,
            'hit_rate': f"{hit_rate:.1f}%",
            'last_updated': self.stats.get('last_updated'),
            'categories': self._get_category_stats()
        }
    
    def _get_category_stats(self) -> dict:
        """获取各类别知识数量统计"""
        categories = {}
        for item in self.knowledge.values():
            cat = item.get('category', 'unknown')
            categories[cat] = categories.get(cat, 0) + 1
        return categories
    
    def clear_unused(self, days: int = 90):
        """
        清理长期未使用的知识
        
        Args:
            days: 天数阈值
        """
        from datetime import timedelta
        
        cutoff_date = datetime.now() - timedelta(days=days)
        removed = 0
        
        keys_to_remove = []
        for key, item in self.knowledge.items():
            # 保留默认知识和高频使用的知识
            if item.get('source') == 'default' or item.get('usage_count', 0) > 10:
                continue
            
            created_at = datetime.fromisoformat(item.get('created_at', ''))
            if created_at < cutoff_date and item.get('usage_count', 0) == 0:
                keys_to_remove.append(key)
        
        for key in keys_to_remove:
            del self.knowledge[key]
            removed += 1
        
        if removed > 0:
            self.save()
            print(f"🗑️  清理了 {removed} 条未使用的知识")
        
        return removed


# 全局知识库实例
_kb_instance = None


def get_knowledge_base() -> KnowledgeBase:
    """获取全局知识库实例（单例模式）"""
    global _kb_instance
    if _kb_instance is None:
        _kb_instance = KnowledgeBase()
    return _kb_instance
