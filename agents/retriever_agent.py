import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RetrieverAgent:
    """使用关键字匹配的轻量级检索器（无 ML 嵌入）"""
    def __init__(self):
        self.documents = []
        self.texts = []

    def index_documents(self, documents):
        """存储文档以进行基于关键字的检索"""
        try:
            self.documents = documents
            self.texts = []
            
            for doc in documents:
                # 尝试从“文本”或“内容”或“摘要”字段获取文本
                text = doc.get('text', '') or doc.get('content', '') or doc.get('summary', '')
                
                # 如果文本为空，也接受标题
                if not text:
                    text = doc.get('title', '')
                
                # 添加包含文本和标题组合的文档以实现更好的匹配
                if text.strip():
                    # 结合标题+文字以获得更好的关键词匹配
                    title = doc.get('title', '')
                    full_text = f"{title}. {text}" if title else text
                    self.texts.append(full_text)
            
            logger.info(f"Indexed {len(self.texts)} documents (from {len(documents)} total)")
            if len(self.texts) == 0 and documents:
                logger.warning(f"No valid texts found. Sample doc keys: {documents[0].keys() if documents else 'empty'}")
        except Exception as e:
            logger.error(f"Error indexing documents: {str(e)}")

    def retrieve(self, query, k=3):
        """简单的基于关键字的检索"""
        try:
            if not self.texts:
                return []
            
            # 根据关键词重叠对文本进行评分
            query_words = set(query.lower().split())
            scored_texts = []
            
            for i, text in enumerate(self.texts):
                text_words = set(text.lower().split())
                overlap = len(query_words & text_words)
                scored_texts.append((overlap, text))
            
            # 按分数排序并返回前k个
            scored_texts.sort(reverse=True, key=lambda x: x[0])
            results = [{"page_content": text} for score, text in scored_texts[:k] if score > 0]
            
            # 如果没有匹配，则返回所有文本
            if not results:
                results = [{"page_content": text} for text in self.texts[:k]]
            
            logger.info(f"Retrieved {len(results)} documents for query")
            return results
            
        except Exception as e:
            logger.error(f"Error retrieving documents: {str(e)}")
            return []