from newspaper import Article
import yfinance as yf
import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ScrapingAgent:
    def __init__(self):
        pass

    def scrape_news(self, urls, timeout=10):
        """获取新闻文章。首先尝试从 URL 中提取符号并使用 yfinance，
        如果需要的话，然后再退回到报纸上。
        
        参数：
            urls：URL 列表（可以是雅虎财经报价页面或文章 URL）
            timeout：抓取操作的超时时间（以秒为单位）
            
        返回：
            包含标题、文本、url 和发布日期的文章词典列表"""
        try:
            articles = []
            
            for url in urls:
                # 尝试从雅虎财经报价 URL 中提取符号
                # 格式：https://finance.yahoo.com/quote/SYMBOL/news/
                if 'finance.yahoo.com/quote/' in url:
                    try:
                        symbol = url.split('/quote/')[1].split('/')[0]
                        logger.info(f"Extracting news for {symbol} using yfinance API")
                        
                        ticker = yf.Ticker(symbol)
                        news_items = ticker.news
                        
                        if news_items:
                            for item in news_items[:5]:  # 限制为 5 篇最新文章
                                # 使用摘要或标题，或从可用字段创建
                                text = item.get('summary', '') or item.get('title', '')
                                title = item.get('title', 'Market Update')
                                
                                # 确保我们有实际内容
                                if not text or len(text.strip()) < 10:
                                    text = f"{title}. Market activity for {symbol}."
                                
                                articles.append({
                                    'title': title,
                                    'text': text,
                                    'url': item.get('link', url),
                                    'publish_date': datetime.fromtimestamp(item.get('providerPublishTime', 0)) if item.get('providerPublishTime') else None
                                })
                            logger.info(f"✅ Fetched {len(news_items[:5])} news articles for {symbol} via yfinance")
                            continue
                        else:
                            logger.warning(f"No news items returned from yfinance for {symbol}")
                    except Exception as e:
                        logger.warning(f"Could not fetch news via yfinance for {url}: {str(e)}")
                
                # 回退到报纸抓取直接文章 URL
                try:
                    article = Article(url)
                    article.download()
                    article.parse()
                    
                    if article.text and len(article.text.strip()) > 50:
                        articles.append({
                            'title': article.title or 'Market Article',
                            'text': article.text,
                            'url': url,
                            'publish_date': article.publish_date
                        })
                        logger.info(f"✅ Scraped article via newspaper: {article.title}")
                    else:
                        logger.warning(f"Article text too short or empty from {url}")
                except Exception as e:
                    logger.warning(f"Could not scrape {url} via newspaper: {str(e)}")
            
            if articles:
                logger.info(f"✅ Total articles collected: {len(articles)}")
            else:
                logger.warning("⚠️ No articles were collected from any source - will use fallback")
            
            return articles
            
        except Exception as e:
            logger.error(f"❌ Error in scrape_news: {str(e)}")
            return []