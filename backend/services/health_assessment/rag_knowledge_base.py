"""
RAG 知识库模块 - FAISS 向量检索
============================================================================

核心技术：RAG（检索增强生成）+ FAISS 向量检索
============================================================================
将医学知识库封装为向量数据库，通过语义检索获取相关知识，
结合大模型生成专业、权威的健康咨询回答。

功能：
1. 医学知识向量化存储（FAISS）
2. 语义相似度检索
3. 知识库动态更新
4. RAG 增强问答

作者: AI Health System
日期: 2024
============================================================================
"""

import os
import json
import pickle
import numpy as np
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime

# FAISS 和 sentence-transformers 已禁用，使用简化版
FAISS_AVAILABLE = False
SENTENCE_TRANSFORMER_AVAILABLE = False


@dataclass
class KnowledgeItem:
    """知识条目"""
    id: str
    category: str  # 分类：慢病管理、用药指导、饮食建议、运动指导、急救知识等
    title: str
    content: str
    keywords: List[str]
    source: str  # 来源
    created_at: str
    embedding: Optional[np.ndarray] = None


class SimpleEmbedding:
    """
    简化版文本向量化（当 sentence-transformers 不可用时使用）
    使用 TF-IDF 风格的简单向量化
    """
    def __init__(self, dim: int = 384):
        self.dim = dim
        self.vocab: Dict[str, int] = {}
        self.idf: Dict[str, float] = {}
    
    def encode(self, texts: List[str]) -> np.ndarray:
        """将文本转换为向量"""
        embeddings = []
        for text in texts:
            # 简单的字符级哈希向量化
            vec = np.zeros(self.dim, dtype=np.float32)
            words = list(text)
            for i, char in enumerate(words):
                # 使用字符的哈希值作为索引
                idx = hash(char) % self.dim
                vec[idx] += 1.0 / (i + 1)  # 位置加权
            # 归一化
            norm = np.linalg.norm(vec)
            if norm > 0:
                vec = vec / norm
            embeddings.append(vec)
        return np.array(embeddings, dtype=np.float32)


class SimpleFAISS:
    """
    简化版 FAISS（当 FAISS 不可用时使用）
    使用 numpy 实现基本的向量检索
    """
    def __init__(self, dim: int):
        self.dim = dim
        self.vectors: Optional[np.ndarray] = None
        self.ids: List[str] = []
    
    def add(self, vectors: np.ndarray, ids: List[str]):
        """添加向量"""
        if self.vectors is None:
            self.vectors = vectors
        else:
            self.vectors = np.vstack([self.vectors, vectors])
        self.ids.extend(ids)
    
    def search(self, query_vector: np.ndarray, k: int = 5) -> Tuple[List[float], List[str]]:
        """搜索最相似的向量"""
        if self.vectors is None or len(self.ids) == 0:
            return [], []
        
        # 计算余弦相似度
        query_norm = query_vector / (np.linalg.norm(query_vector) + 1e-8)
        vectors_norm = self.vectors / (np.linalg.norm(self.vectors, axis=1, keepdims=True) + 1e-8)
        similarities = np.dot(vectors_norm, query_norm.T).flatten()
        
        # 获取 top-k
        k = min(k, len(self.ids))
        top_indices = np.argsort(similarities)[-k:][::-1]
        
        scores = [float(similarities[i]) for i in top_indices]
        result_ids = [self.ids[i] for i in top_indices]
        
        return scores, result_ids
    
    def save(self, path: str):
        """保存索引"""
        data = {
            'vectors': self.vectors,
            'ids': self.ids,
            'dim': self.dim
        }
        with open(path, 'wb') as f:
            pickle.dump(data, f)
    
    def load(self, path: str):
        """加载索引"""
        with open(path, 'rb') as f:
            data = pickle.load(f)
        self.vectors = data['vectors']
        self.ids = data['ids']
        self.dim = data['dim']


class HealthKnowledgeBase:
    """
    健康知识库 - RAG 核心组件
    
    使用 FAISS 进行高效向量检索，支持：
    1. 医学知识的向量化存储
    2. 语义相似度检索
    3. 知识库的增删改查
    4. 持久化存储
    """
    
    def __init__(
        self,
        embedding_model: str = "paraphrase-multilingual-MiniLM-L12-v2",
        index_path: Optional[str] = None,
        knowledge_path: Optional[str] = None
    ):
        """
        初始化知识库
        
        Args:
            embedding_model: 文本向量化模型名称
            index_path: FAISS 索引存储路径
            knowledge_path: 知识条目存储路径
        """
        self.embedding_dim = 384
        
        # 初始化向量化模型
        if SENTENCE_TRANSFORMER_AVAILABLE:
            try:
                self.encoder = SentenceTransformer(embedding_model)
                self.embedding_dim = self.encoder.get_sentence_embedding_dimension()
                print(f"✓ 加载向量化模型: {embedding_model}")
            except Exception as e:
                print(f"⚠️ 加载模型失败: {e}，使用简化版")
                self.encoder = SimpleEmbedding(self.embedding_dim)
        else:
            self.encoder = SimpleEmbedding(self.embedding_dim)
        
        # 初始化 FAISS 索引
        if FAISS_AVAILABLE:
            self.index = faiss.IndexFlatIP(self.embedding_dim)  # 内积相似度
            print(f"✓ 初始化 FAISS 索引 (dim={self.embedding_dim})")
        else:
            self.index = SimpleFAISS(self.embedding_dim)
            print(f"✓ 初始化简化版向量索引 (dim={self.embedding_dim})")
        
        # 知识条目存储
        self.knowledge_items: Dict[str, KnowledgeItem] = {}
        self.id_to_index: Dict[str, int] = {}  # ID 到索引位置的映射
        
        # 存储路径
        base_dir = os.path.dirname(os.path.abspath(__file__))
        self.index_path = index_path or os.path.join(base_dir, "data", "faiss_index.bin")
        self.knowledge_path = knowledge_path or os.path.join(base_dir, "data", "knowledge_base.json")
        
        # 确保目录存在
        os.makedirs(os.path.dirname(self.index_path), exist_ok=True)
        
        # 尝试加载已有数据
        self._load_if_exists()
        
        # 如果知识库为空，初始化默认知识
        if len(self.knowledge_items) == 0:
            self._init_default_knowledge()
    
    def _load_if_exists(self):
        """加载已存在的知识库"""
        try:
            if os.path.exists(self.knowledge_path):
                with open(self.knowledge_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                for item_data in data:
                    item = KnowledgeItem(**item_data)
                    self.knowledge_items[item.id] = item
                print(f"✓ 加载知识库: {len(self.knowledge_items)} 条")
                
                # 重建索引
                if len(self.knowledge_items) > 0:
                    self._rebuild_index()
        except Exception as e:
            print(f"⚠️ 加载知识库失败: {e}")
    
    def _rebuild_index(self):
        """重建向量索引"""
        texts = []
        ids = []
        for item_id, item in self.knowledge_items.items():
            texts.append(f"{item.title} {item.content}")
            ids.append(item_id)
        
        if texts:
            embeddings = self._encode_texts(texts)
            if FAISS_AVAILABLE:
                self.index = faiss.IndexFlatIP(self.embedding_dim)
                self.index.add(embeddings)
            else:
                self.index = SimpleFAISS(self.embedding_dim)
                self.index.add(embeddings, ids)
            
            self.id_to_index = {id_: i for i, id_ in enumerate(ids)}
            print(f"✓ 重建向量索引: {len(ids)} 条")
    
    def _encode_texts(self, texts: List[str]) -> np.ndarray:
        """将文本转换为向量"""
        if isinstance(self.encoder, SimpleEmbedding):
            return self.encoder.encode(texts)
        else:
            embeddings = self.encoder.encode(texts, convert_to_numpy=True)
            return embeddings.astype(np.float32)
    
    def _init_default_knowledge(self):
        """初始化默认医学知识库"""
        default_knowledge = [
            # ==================== 高血压管理 ====================
            {
                "id": "hypertension_001",
                "category": "慢病管理",
                "title": "高血压的诊断标准",
                "content": "高血压诊断标准：收缩压≥140mmHg和/或舒张压≥90mmHg。血压分级：正常血压<120/80mmHg；正常高值120-139/80-89mmHg；1级高血压140-159/90-99mmHg；2级高血压160-179/100-109mmHg；3级高血压≥180/110mmHg。老年人收缩压≥150mmHg应开始药物治疗。",
                "keywords": ["高血压", "血压", "诊断", "分级"],
                "source": "中国高血压防治指南2023"
            },
            {
                "id": "hypertension_002",
                "category": "慢病管理",
                "title": "高血压的生活方式干预",
                "content": "高血压生活方式干预：1.限盐：每日食盐<6g；2.控制体重：BMI<24kg/m²；3.戒烟限酒：男性每日酒精<25g，女性<15g；4.适量运动：每周≥150分钟中等强度有氧运动；5.心理平衡：避免情绪激动；6.规律作息：保证充足睡眠。生活方式干预可使血压下降5-20mmHg。",
                "keywords": ["高血压", "生活方式", "限盐", "运动", "减重"],
                "source": "中国高血压防治指南2023"
            },
            {
                "id": "hypertension_003",
                "category": "用药指导",
                "title": "常用降压药物分类",
                "content": "常用降压药物：1.钙通道阻滞剂(CCB)：如氨氯地平，适合老年人；2.血管紧张素转换酶抑制剂(ACEI)：如依那普利，适合糖尿病患者；3.血管紧张素受体拮抗剂(ARB)：如缬沙坦，干咳少；4.利尿剂：如氢氯噻嗪，适合盐敏感性高血压；5.β受体阻滞剂：如美托洛尔，适合心率快者。用药需个体化，遵医嘱服用。",
                "keywords": ["降压药", "CCB", "ACEI", "ARB", "利尿剂"],
                "source": "临床用药指南"
            },
            
            # ==================== 糖尿病管理 ====================
            {
                "id": "diabetes_001",
                "category": "慢病管理",
                "title": "糖尿病的诊断标准",
                "content": "糖尿病诊断标准：1.空腹血糖≥7.0mmol/L；2.餐后2小时血糖≥11.1mmol/L；3.糖化血红蛋白(HbA1c)≥6.5%；4.随机血糖≥11.1mmol/L伴典型症状。糖尿病前期：空腹血糖6.1-6.9mmol/L或餐后2小时血糖7.8-11.0mmol/L。早期发现、早期干预可延缓或预防糖尿病发生。",
                "keywords": ["糖尿病", "血糖", "诊断", "糖化血红蛋白"],
                "source": "中国2型糖尿病防治指南2020"
            },
            {
                "id": "diabetes_002",
                "category": "慢病管理",
                "title": "糖尿病饮食管理",
                "content": "糖尿病饮食原则：1.控制总热量：根据体重、活动量计算；2.碳水化合物占50-60%，选择低GI食物；3.蛋白质占15-20%，优选鱼、禽、蛋、奶；4.脂肪占20-30%，限制饱和脂肪；5.增加膳食纤维：每日25-30g；6.定时定量进餐；7.限制精制糖和含糖饮料。建议少食多餐，细嚼慢咽。",
                "keywords": ["糖尿病", "饮食", "血糖控制", "GI"],
                "source": "中国糖尿病医学营养治疗指南"
            },
            {
                "id": "diabetes_003",
                "category": "用药指导",
                "title": "常用降糖药物",
                "content": "常用降糖药物：1.二甲双胍：一线用药，适合超重患者；2.磺脲类：如格列美脲，促进胰岛素分泌；3.DPP-4抑制剂：如西格列汀，低血糖风险小；4.SGLT-2抑制剂：如达格列净，有心肾保护作用；5.GLP-1受体激动剂：如利拉鲁肽，可减重；6.胰岛素：适合胰岛功能差者。用药需个体化，定期监测血糖。",
                "keywords": ["降糖药", "二甲双胍", "胰岛素", "SGLT-2"],
                "source": "临床用药指南"
            },
            
            # ==================== 心脏健康 ====================
            {
                "id": "heart_001",
                "category": "慢病管理",
                "title": "冠心病的预防",
                "content": "冠心病预防措施：1.控制血压：目标<140/90mmHg；2.控制血糖：糖化血红蛋白<7%；3.调节血脂：LDL-C<2.6mmol/L；4.戒烟：吸烟使冠心病风险增加2-4倍；5.健康饮食：地中海饮食模式；6.规律运动：每周150分钟中等强度运动；7.控制体重：BMI 18.5-24kg/m²；8.心理健康：避免长期压力。",
                "keywords": ["冠心病", "预防", "心血管", "动脉硬化"],
                "source": "中国心血管病预防指南"
            },
            {
                "id": "heart_002",
                "category": "急救知识",
                "title": "心绞痛的识别与处理",
                "content": "心绞痛识别：胸骨后压榨性疼痛，可放射至左肩、左臂，持续3-5分钟，休息或含服硝酸甘油后缓解。处理方法：1.立即停止活动，就地休息；2.舌下含服硝酸甘油0.5mg，5分钟可重复，最多3次；3.如15分钟不缓解，考虑心肌梗死，立即拨打120；4.保持镇静，避免紧张；5.有条件可吸氧。",
                "keywords": ["心绞痛", "胸痛", "硝酸甘油", "急救"],
                "source": "急救医学指南"
            },
            
            # ==================== 睡眠健康 ====================
            {
                "id": "sleep_001",
                "category": "健康指导",
                "title": "老年人睡眠问题",
                "content": "老年人睡眠特点：睡眠时间缩短（6-7小时），入睡困难，易醒，深睡眠减少。改善方法：1.规律作息：固定起床时间；2.睡前放松：温水泡脚、听轻音乐；3.避免刺激：睡前4小时不喝咖啡茶；4.适度运动：但睡前3小时避免剧烈运动；5.控制午睡：不超过30分钟；6.营造环境：安静、黑暗、适温。如持续失眠超过1个月，建议就医。",
                "keywords": ["睡眠", "失眠", "老年人", "睡眠质量"],
                "source": "老年医学指南"
            },
            
            # ==================== 运动指导 ====================
            {
                "id": "exercise_001",
                "category": "运动指导",
                "title": "老年人运动建议",
                "content": "老年人运动建议：1.有氧运动：快走、游泳、太极拳，每周150分钟；2.力量训练：弹力带、哑铃，每周2次；3.平衡训练：单脚站立、踮脚走，预防跌倒；4.柔韧性训练：拉伸、瑜伽。注意事项：运动前热身5-10分钟；运动强度以能说话但不能唱歌为宜；避免空腹运动；有心脏病者需医生评估后运动。",
                "keywords": ["运动", "老年人", "有氧运动", "力量训练"],
                "source": "老年人运动指南"
            },
            {
                "id": "exercise_002",
                "category": "运动指导",
                "title": "步数与健康",
                "content": "每日步数建议：老年人每日6000-8000步为宜。研究表明：每日7000步可降低50-70%的全因死亡风险。步行好处：改善心肺功能、控制血糖血压、增强骨密度、改善情绪。步行技巧：抬头挺胸、摆臂自然、步幅适中、呼吸均匀。建议分次完成，如早晚各走30分钟。",
                "keywords": ["步数", "走路", "运动量", "健康"],
                "source": "运动医学研究"
            },
            
            # ==================== 饮食营养 ====================
            {
                "id": "nutrition_001",
                "category": "饮食建议",
                "title": "老年人营养需求",
                "content": "老年人营养要点：1.蛋白质：每公斤体重1.0-1.2g，优选鱼、蛋、奶、豆；2.钙：每日1000-1200mg，预防骨质疏松；3.维生素D：每日600-800IU；4.膳食纤维：每日25-30g，预防便秘；5.水分：每日1500-1700ml；6.限盐：每日<6g；7.限油：每日25-30g。建议少食多餐，食物多样化。",
                "keywords": ["营养", "老年人", "蛋白质", "钙", "维生素"],
                "source": "中国居民膳食指南"
            },
            
            # ==================== 常见症状 ====================
            {
                "id": "symptom_001",
                "category": "症状识别",
                "title": "头晕的常见原因",
                "content": "老年人头晕常见原因：1.体位性低血压：起床太快导致；2.颈椎病：转头时加重；3.高血压：血压波动大时；4.低血糖：空腹或用药后；5.贫血：伴乏力、面色苍白；6.心律失常：伴心悸；7.脑供血不足：伴视物模糊。处理：头晕时立即坐下或躺下，避免跌倒。如频繁发作或伴其他症状，应及时就医检查。",
                "keywords": ["头晕", "眩晕", "低血压", "症状"],
                "source": "老年医学指南"
            },
            {
                "id": "symptom_002",
                "category": "急救知识",
                "title": "中风的早期识别",
                "content": "中风早期识别（FAST法则）：F-Face面部：让患者微笑，观察是否一侧面部下垂；A-Arm手臂：让患者举起双臂，观察是否一侧无力下垂；S-Speech言语：让患者说一句话，观察是否口齿不清；T-Time时间：发现以上任一症状，立即拨打120。中风黄金治疗时间为4.5小时内，越早治疗效果越好。",
                "keywords": ["中风", "脑卒中", "急救", "FAST"],
                "source": "脑卒中防治指南"
            },
            
            # ==================== 用药安全 ====================
            {
                "id": "medication_001",
                "category": "用药指导",
                "title": "老年人用药注意事项",
                "content": "老年人用药原则：1.从小剂量开始：老年人肝肾功能下降，药物代谢慢；2.避免多重用药：尽量控制在5种以内；3.定时服药：设置提醒，避免漏服或重复服用；4.注意药物相互作用：告知医生所有用药；5.监测不良反应：如头晕、乏力、食欲下降；6.不要自行停药或调整剂量；7.定期复查：评估疗效和安全性。",
                "keywords": ["用药", "老年人", "药物安全", "不良反应"],
                "source": "老年人安全用药指南"
            },
        ]
        
        # 添加到知识库
        for item_data in default_knowledge:
            item_data["created_at"] = datetime.now().isoformat()
            self.add_knowledge(KnowledgeItem(**item_data, embedding=None))
        
        print(f"✓ 初始化默认知识库: {len(default_knowledge)} 条")
    
    def add_knowledge(self, item: KnowledgeItem) -> bool:
        """
        添加知识条目
        
        Args:
            item: 知识条目
            
        Returns:
            是否添加成功
        """
        try:
            # 生成向量
            text = f"{item.title} {item.content}"
            embedding = self._encode_texts([text])[0]
            item.embedding = embedding
            
            # 添加到索引
            if FAISS_AVAILABLE:
                self.index.add(embedding.reshape(1, -1))
            else:
                self.index.add(embedding.reshape(1, -1), [item.id])
            
            # 存储条目
            self.knowledge_items[item.id] = item
            self.id_to_index[item.id] = len(self.id_to_index)
            
            return True
        except Exception as e:
            print(f"添加知识失败: {e}")
            return False
    
    def search(
        self,
        query: str,
        top_k: int = 5,
        category: Optional[str] = None,
        min_score: float = 0.3
    ) -> List[Tuple[KnowledgeItem, float]]:
        """
        搜索相关知识
        
        Args:
            query: 查询文本
            top_k: 返回结果数量
            category: 限定分类
            min_score: 最小相似度阈值
            
        Returns:
            [(知识条目, 相似度分数), ...]
        """
        if len(self.knowledge_items) == 0:
            return []
        
        # 查询向量化
        query_embedding = self._encode_texts([query])[0]
        
        # 搜索
        if FAISS_AVAILABLE:
            scores, indices = self.index.search(
                query_embedding.reshape(1, -1),
                min(top_k * 2, len(self.knowledge_items))  # 多取一些，后面过滤
            )
            scores = scores[0]
            indices = indices[0]
            
            # 获取结果
            results = []
            id_list = list(self.knowledge_items.keys())
            for score, idx in zip(scores, indices):
                if idx < 0 or idx >= len(id_list):
                    continue
                if score < min_score:
                    continue
                    
                item_id = id_list[idx]
                item = self.knowledge_items[item_id]
                
                # 分类过滤
                if category and item.category != category:
                    continue
                    
                results.append((item, float(score)))
                
                if len(results) >= top_k:
                    break
        else:
            scores, result_ids = self.index.search(query_embedding, top_k * 2)
            
            results = []
            for score, item_id in zip(scores, result_ids):
                if score < min_score:
                    continue
                if item_id not in self.knowledge_items:
                    continue
                    
                item = self.knowledge_items[item_id]
                
                if category and item.category != category:
                    continue
                    
                results.append((item, score))
                
                if len(results) >= top_k:
                    break
        
        return results
    
    def get_context_for_query(self, query: str, top_k: int = 3) -> str:
        """
        获取查询相关的知识上下文（用于 RAG）
        
        Args:
            query: 用户查询
            top_k: 返回的知识条目数量
            
        Returns:
            格式化的知识上下文
        """
        results = self.search(query, top_k=top_k)
        
        if not results:
            return ""
        
        context_parts = ["【相关医学知识参考】"]
        for i, (item, score) in enumerate(results, 1):
            context_parts.append(f"\n{i}. 【{item.category}】{item.title}")
            context_parts.append(f"   {item.content}")
            context_parts.append(f"   来源：{item.source}")
        
        return "\n".join(context_parts)
    
    def save(self):
        """保存知识库"""
        try:
            # 保存知识条目（不含 embedding）
            data = []
            for item in self.knowledge_items.values():
                item_dict = {
                    "id": item.id,
                    "category": item.category,
                    "title": item.title,
                    "content": item.content,
                    "keywords": item.keywords,
                    "source": item.source,
                    "created_at": item.created_at
                }
                data.append(item_dict)
            
            with open(self.knowledge_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            # 保存 FAISS 索引
            if FAISS_AVAILABLE:
                faiss.write_index(self.index, self.index_path)
            else:
                self.index.save(self.index_path)
            
            print(f"✓ 知识库已保存: {len(data)} 条")
            return True
        except Exception as e:
            print(f"保存知识库失败: {e}")
            return False
    
    def get_stats(self) -> Dict:
        """获取知识库统计信息"""
        categories = {}
        for item in self.knowledge_items.values():
            categories[item.category] = categories.get(item.category, 0) + 1
        
        return {
            "total_items": len(self.knowledge_items),
            "categories": categories,
            "embedding_dim": self.embedding_dim,
            "faiss_available": FAISS_AVAILABLE,
            "transformer_available": SENTENCE_TRANSFORMER_AVAILABLE
        }


# ============================================================================
# RAG 增强问答接口
# ============================================================================

# 全局知识库实例
_knowledge_base: Optional[HealthKnowledgeBase] = None


def get_knowledge_base() -> HealthKnowledgeBase:
    """获取知识库单例"""
    global _knowledge_base
    if _knowledge_base is None:
        _knowledge_base = HealthKnowledgeBase()
    return _knowledge_base


def rag_search(query: str, top_k: int = 3) -> str:
    """
    RAG 检索接口
    
    Args:
        query: 用户查询
        top_k: 返回知识条目数量
        
    Returns:
        相关知识上下文
    """
    kb = get_knowledge_base()
    return kb.get_context_for_query(query, top_k)


def rag_enhance_prompt(query: str, base_prompt: str) -> str:
    """
    RAG 增强系统提示词
    
    将检索到的知识注入到系统提示词中
    
    Args:
        query: 用户查询
        base_prompt: 基础系统提示词
        
    Returns:
        增强后的系统提示词
    """
    context = rag_search(query)
    
    if context:
        enhanced_prompt = f"""{base_prompt}

============================================================================
【RAG 知识检索结果】
============================================================================
{context}

请参考以上医学知识，结合用户的具体情况，提供专业、准确的健康建议。
============================================================================"""
        return enhanced_prompt
    
    return base_prompt


# ============================================================================
# 测试代码
# ============================================================================
if __name__ == "__main__":
    print("\n" + "="*60)
    print("RAG 知识库测试")
    print("="*60)
    
    # 初始化知识库
    kb = get_knowledge_base()
    
    # 显示统计信息
    stats = kb.get_stats()
    print(f"\n知识库统计:")
    print(f"  总条目数: {stats['total_items']}")
    print(f"  分类分布: {stats['categories']}")
    print(f"  向量维度: {stats['embedding_dim']}")
    print(f"  FAISS可用: {stats['faiss_available']}")
    
    # 测试搜索
    test_queries = [
        "血压高怎么办",
        "糖尿病饮食注意什么",
        "老年人失眠怎么改善",
        "每天走多少步合适",
        "头晕是什么原因"
    ]
    
    print("\n" + "-"*60)
    print("搜索测试:")
    print("-"*60)
    
    for query in test_queries:
        print(f"\n查询: {query}")
        results = kb.search(query, top_k=2)
        for item, score in results:
            print(f"  [{score:.3f}] {item.title}")
    
    # 测试 RAG 上下文生成
    print("\n" + "-"*60)
    print("RAG 上下文生成测试:")
    print("-"*60)
    
    context = rag_search("我血压有点高，需要注意什么")
    print(context)
    
    # 保存知识库
    kb.save()
    
    print("\n✓ 测试完成")
