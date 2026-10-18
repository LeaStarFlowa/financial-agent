"""适用于低内存环境的简单检索器，无需 ML 嵌入"""
import logging
from difflib import SequenceMatcher

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SimpleRetrieverAgent:
    def __init__(self):
        self.documents = []

    def index_documents(self, documents):
        """存储没有嵌入的文档"""
        try:
            self.documents = documents
            logger.info(f"Indexed {len(documents)} documents")
        except Exception as e:
            logger.error(f"Error indexing documents: {str(e)}")

    def retrieve(self, query, k=3):
        """简单的基于关键字的检索"""
        try:
            if not self.documents:
                return []
            
            # 根据关键词重叠对文档进行评分
            scored_docs = []
            query_words = set(query.lower().split())
            
            for doc in self.documents:
                text = doc.get('text', '').lower()
                title = doc.get('title', '').lower()
                
                # 计算匹配的单词数
                text_words = set(text.split())
                title_words = set(title.split())
                
                text_overlap = len(query_words & text_words)
                title_overlap = len(query_words & title_words) * 2  # 体重头衔更高
                
                score = text_overlap + title_overlap
                scored_docs.append((score, doc['text']))
            
            # 按分数排序并返回前k个
            scored_docs.sort(reverse=True, key=lambda x: x[0])
            results = [doc[1] for doc in scored_docs[:k]]
            
            logger.info(f"Retrieved {len(results)} documents for query")
            return results
            
        except Exception as e:
            logger.error(f"Error retrieving documents: {str(e)}")
            return []
