"""
语义意图匹配器
==============

使用 Sentence-Transformers 进行语义级意图匹配。
相比关键词规则匹配，可以理解同义表达。

示例：
- "我走路比较少" → exercise（规则匹配可能失败）
- "血压有点高正常吗" → blood_pressure（语义理解）
"""

import logging
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass

logger = logging.getLogger(__name__)

# 尝试导入 sentence-transformers
try:
    from sentence_transformers import SentenceTransformer, util
    import torch
    HAS_SENTENCE_TRANSFORMERS = True
except ImportError:
    HAS_SENTENCE_TRANSFORMERS = False
    logger.warning("sentence-transformers 未安装，语义匹配不可用。安装: pip install sentence-transformers")


@dataclass
class SemanticMatchResult:
    """语义匹配结果"""
    intent: str
    confidence: float
    matched_description: str


class SemanticIntentMatcher:
    """
    语义意图匹配器
    
    使用多语言小模型进行语义相似度计算。
    模型大小约 ~120MB，CPU 可运行。
    """
    
    # 意图描述库（用于语义匹配）
    INTENT_DESCRIPTIONS = {
        # 慢病管理
        "blood_pressure": [
            "血压相关问题",
            "高血压低血压",
            "血压测量结果是否正常",
            "收缩压舒张压数值",
            "降压药吃药",
        ],
        "blood_sugar": [
            "血糖相关问题",
            "糖尿病血糖控制",
            "空腹血糖餐后血糖",
            "胰岛素降糖药",
            "血糖高低是否正常",
        ],
        "blood_lipid": [
            "血脂胆固醇问题",
            "甘油三酯高密度低密度",
            "血脂异常需要注意什么",
        ],
        "heart_disease": [
            "心脏心血管问题",
            "心跳心率心悸",
            "胸闷胸痛不舒服",
            "冠心病心绞痛",
        ],
        "medication": [
            "吃药服药用药",
            "药物副作用",
            "什么时候吃药",
            "药能不能停",
        ],
        
        # 生活方式
        "exercise": [
            "运动锻炼健身",
            "走路散步跑步",
            "活动量步数不够",
            "久坐不动需要运动",
            "适合什么运动",
        ],
        "diet": [
            "饮食吃什么",
            "食物营养搭配",
            "能吃不能吃忌口",
            "蔬菜水果蛋白质",
        ],
        "sleep": [
            "睡眠失眠睡不着",
            "睡眠质量不好",
            "早醒多梦",
            "晚上睡不好白天困",
        ],
        "weight": [
            "体重减肥肥胖",
            "BMI超重",
            "需要控制体重",
        ],
        
        # 情绪心理
        "anxiety": [
            "担心害怕焦虑紧张",
            "心里不安烦躁",
            "总是担心身体问题",
        ],
        "loneliness": [
            "孤独寂寞一个人",
            "没人陪没人说话",
            "子女不在身边",
        ],
        "depression": [
            "难过伤心不开心",
            "情绪低落没意思",
            "什么都不想做",
        ],
        "stress": [
            "压力大累疲惫",
            "撑不住坚持不下去",
            "身心俱疲",
        ],
        
        # 症状报告
        "symptom_report": [
            "身体不舒服难受",
            "头晕头痛恶心",
            "发烧咳嗽乏力",
            "哪里疼痛不适",
        ],
        
        # 数据解读
        "data_interpret": [
            "数据指标报告结果",
            "这个数值正常吗",
            "偏高偏低什么意思",
        ],
        
        # 控制命令
        "control_navigate": [
            "打开页面跳转",
            "去首页设置",
            "返回上一页",
            "进入某个功能",
        ],
        "control_query": [
            "查看查询数据",
            "看看我的记录",
            "显示健康数据",
            "告诉我今天的情况",
        ],
        "control_reminder": [
            "设置提醒闹钟",
            "提醒我吃药",
            "几点提醒",
        ],
        "control_stop": [
            "停止暂停",
            "别说了安静",
            "取消算了",
        ],
        
        # 紧急
        "emergency": [
            "救命帮帮我",
            "紧急呼救求助",
            "身体很不舒服需要帮助",
            "晕倒昏迷抽搐",
        ],
        
        # 交互
        "greeting": [
            "你好早上好",
            "打招呼问候",
        ],
        "thanks": [
            "谢谢感谢",
            "多谢帮忙",
        ],
        "goodbye": [
            "再见拜拜",
            "下次见",
        ],
    }
    
    def __init__(self, model_name: str = "paraphrase-multilingual-MiniLM-L12-v2"):
        """
        初始化语义匹配器
        
        Args:
            model_name: Sentence-Transformers 模型名称
                - paraphrase-multilingual-MiniLM-L12-v2 (推荐，多语言，~120MB)
                - distiluse-base-multilingual-cased-v2 (更大，~250MB)
        """
        self.model = None
        self.intent_embeddings: Dict[str, torch.Tensor] = {}
        self.model_name = model_name
        self._initialized = False
        
    def initialize(self) -> bool:
        """延迟初始化（首次使用时加载模型）"""
        if self._initialized:
            return True
            
        if not HAS_SENTENCE_TRANSFORMERS:
            logger.error("sentence-transformers 未安装")
            return False
        
        try:
            logger.info(f"正在加载语义模型: {self.model_name}")
            self.model = SentenceTransformer(self.model_name)
            
            # 预计算所有意图的向量
            self._precompute_embeddings()
            
            self._initialized = True
            logger.info(f"✅ 语义匹配器初始化完成，共 {len(self.intent_embeddings)} 个意图")
            return True
            
        except Exception as e:
            logger.error(f"语义模型加载失败: {e}")
            return False
    
    def _precompute_embeddings(self):
        """预计算所有意图描述的向量"""
        for intent, descriptions in self.INTENT_DESCRIPTIONS.items():
            # 将所有描述合并编码，取平均
            embeddings = self.model.encode(descriptions, convert_to_tensor=True)
            # 存储平均向量
            self.intent_embeddings[intent] = embeddings.mean(dim=0)
    
    def match(self, text: str, top_k: int = 3) -> List[SemanticMatchResult]:
        """
        语义匹配意图
        
        Args:
            text: 用户输入
            top_k: 返回前 k 个匹配结果
            
        Returns:
            匹配结果列表，按置信度降序
        """
        if not self._initialized:
            if not self.initialize():
                return []
        
        try:
            # 编码用户输入
            query_embedding = self.model.encode(text, convert_to_tensor=True)
            
            # 计算与所有意图的相似度
            results = []
            for intent, intent_emb in self.intent_embeddings.items():
                similarity = util.cos_sim(query_embedding, intent_emb).item()
                results.append(SemanticMatchResult(
                    intent=intent,
                    confidence=similarity,
                    matched_description=self.INTENT_DESCRIPTIONS[intent][0]
                ))
            
            # 按相似度排序
            results.sort(key=lambda x: x.confidence, reverse=True)
            
            return results[:top_k]
            
        except Exception as e:
            logger.error(f"语义匹配失败: {e}")
            return []
    
    def match_best(self, text: str) -> Optional[SemanticMatchResult]:
        """获取最佳匹配"""
        results = self.match(text, top_k=1)
        return results[0] if results else None


# 单例实例（延迟初始化）
semantic_matcher = SemanticIntentMatcher()
