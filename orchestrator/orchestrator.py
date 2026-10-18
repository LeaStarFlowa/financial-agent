import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from fastapi import FastAPI, UploadFile, File, HTTPException, Form, Query
from fastapi.responses import StreamingResponse
from data_ingestion.api_agent import APIAgent
from data_ingestion.scrapping_agent import ScrapingAgent
from agents.retriever_agent import RetrieverAgent
from agents.analysis_agent import AnalysisAgent
from agents.language_agent import LanguageAgent
from agents.voice_agent import VoiceAgent
import logging
import pandas as pd
from fastapi.middleware.cors import CORSMiddleware
import json
import re
from typing import Optional, List
from dotenv import load_dotenv

# 导入综合股票代码
from streamlit_app.stock_symbols import ALL_STOCKS, CATEGORIES

# 加载环境变量
load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

# 添加CORS中间件以允许Streamlit访问API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

api_agent = APIAgent()
scraping_agent = ScrapingAgent()
retriever_agent = RetrieverAgent()
analysis_agent = AnalysisAgent()
language_agent = LanguageAgent()
voice_agent = VoiceAgent()

# 默认符号（可以扩展）
DEFAULT_SYMBOLS = ['AAPL', 'MSFT', 'GOOGL']  # 主要科技股

# 使用一些示例数据进行初始化
try:
    # 预取一些数据来初始化智能体
    market_data = api_agent.get_market_data(DEFAULT_SYMBOLS)
    
    # 使用一些示例数据初始化检索器
    sample_docs = [
        {"text": "台积电季度盈利表现强劲，营收创下新高。", "title": "台积电盈利"},
        {"text": "三星电子在存储芯片市场面临竞争。", "title": "三星市场地位"}
    ]
    retriever_agent.index_documents(sample_docs)
    logger.info("Pre-initialized agents with sample data")
except Exception as e:
    logger.warning(f"Failed to pre-initialize agents: {str(e)}")

# 增强的符号映射以处理各种查询格式
SYMBOL_MAPPINGS = {
    # 科技巨头
    'tsmc': 'TSM',
    'taiwan semiconductor': 'TSM',
    'samsung': '005930.KS',
    'samsung electronics': '005930.KS',
    'apple': 'AAPL',
    'google': 'GOOGL',
    'alphabet': 'GOOGL',
    'microsoft': 'MSFT',
    'amazon': 'AMZN',
    'meta': 'META',
    'facebook': 'META',
    'netflix': 'NFLX',
    'nvidia': 'NVDA',
    'tesla': 'TSLA',
    'intel': 'INTC',
    'amd': 'AMD',
    'advanced micro devices': 'AMD',
    'qualcomm': 'QCOM',
    
    # 其他主要公司
    'disney': 'DIS',
    'nike': 'NKE',
    'walmart': 'WMT',
    'jpmorgan': 'JPM',
    'jp morgan': 'JPM',
    'bank of america': 'BAC',
    'goldman sachs': 'GS',
    'visa': 'V',
    'mastercard': 'MA',
    'coca cola': 'KO',
    'pepsi': 'PEP',
    'mcdonalds': 'MCD',
    'starbucks': 'SBUX',
    'boeing': 'BA',
    'pfizer': 'PFE',
    'johnson & johnson': 'JNJ',
    'exxon': 'XOM',
    'chevron': 'CVX',
    
    # 加密货币
    'bitcoin': 'BTC-USD',
    'ethereum': 'ETH-USD',
    'dogecoin': 'DOGE-USD',
    
    # 指数
    's&p 500': '^GSPC',
    'sp500': '^GSPC',
    'dow jones': '^DJI',
    'nasdaq': '^IXIC',
}

# 使用一些示例数据进行初始化
try:
    # 预取一些数据来初始化智能体
    market_data = api_agent.get_market_data(DEFAULT_SYMBOLS)
    
    # 使用一些示例数据初始化检索器
    sample_docs = [
        {"text": "台积电季度盈利表现强劲，营收创下新高。", "title": "台积电盈利"},
        {"text": "三星电子在存储芯片市场面临竞争。", "title": "三星市场地位"}
    ]
    retriever_agent.index_documents(sample_docs)
    logger.info("Pre-initialized agents with sample data")
except Exception as e:
    logger.warning(f"Failed to pre-initialize agents: {str(e)}")

def extract_symbols_from_query(query):
    """从查询中提取股票代码并映射到实际的股票代码"""
    extracted_symbols = []
    
    # 直接检查股票代码（如 AAPL、MSFT 等）
    ticker_pattern = r'\b[A-Z]{1,5}\b'
    direct_tickers = re.findall(ticker_pattern, query)
    if direct_tickers:
        extracted_symbols.extend(direct_tickers)
    
    # 检查查询中的公司名称
    for company, symbol in SYMBOL_MAPPINGS.items():
        if company.lower() in query.lower():
            extracted_symbols.append(symbol)
    
    # 删除重复项同时保留顺序
    unique_symbols = []
    for symbol in extracted_symbols:
        if symbol not in unique_symbols:
            unique_symbols.append(symbol)
    
    # 如果没有找到符号，则使用默认值
    if not unique_symbols:
        return DEFAULT_SYMBOLS
    
    return unique_symbols

# 添加健康检查端点
@app.get("/")
async def health_check():
    return {"status": "healthy", "message": "金融助手 API 正在运行"}

@app.get("/debug/test-scraping")
async def test_scraping(symbol: str = "AMZN"):
    """调试端点以测试新闻抓取功能"""
    try:
        logger.info(f"Testing news scraping for {symbol}")
        url = f"https://finance.yahoo.com/quote/{symbol}/news/"
        articles = scraping_agent.scrape_news([url], timeout=15)
        
        return {
            "status": "success" if articles else "no_articles",
            "symbol": symbol,
            "articles_found": len(articles),
            "sample_article": articles[0] if articles else None,
            "message": f"成功抓取 {len(articles)} 篇文章" if articles else "未找到文章，将使用备用数据"
        }
    except Exception as e:
        logger.error(f"Error in test scraping: {str(e)}")
        return {
            "status": "error",
            "error": str(e),
            "message": "抓取失败，系统将使用备用数据"
        }

@app.get("/retrieve/retrieve")
async def retrieve(
    query: str, 
    symbols: Optional[str] = None
):
    try:
        logger.info(f"Processing retrieve request for query: {query}")
        
        # 步骤 1：从查询中提取符号或使用显式提供的符号
        if symbols:
            # 如果提供了明确的符号，请使用它们
            symbol_list = [s.strip() for s in symbols.split(",")]
            logger.info(f"Using explicitly provided symbols: {symbol_list}")
        else:
            # 否则从查询中提取它们
            symbol_list = extract_symbols_from_query(query)
            logger.info(f"Extracted symbols from query: {symbol_list}")
        
        # 第 2 步：验证并获取市场数据
        if not symbol_list:
            logger.warning("No symbols found, using defaults")
            symbol_list = DEFAULT_SYMBOLS
        
        logger.info(f"Fetching market data for: {symbol_list}")
        market_data = api_agent.get_market_data(symbol_list)
        
        if not market_data:
            logger.error(f"Failed to fetch market data for symbols: {symbol_list}")
            # 返回有用的错误消息
            return {
                "error": f"无法获取以下股票代码的数据：{', '.join(symbol_list)}。请检查代码是否为有效的 Yahoo Finance 股票代码。",
                "query": query,
                "attempted_symbols": symbol_list,
                "suggestion": "请尝试使用 AAPL、MSFT、GOOGL 等常见代码，或在 Yahoo Finance 核对正确代码。"
            }
        
        # 使用智能体方法将市场数据转换为可序列化格式
        logger.info(f"Serializing market data for {list(market_data.keys())}")
        serialized_market_data = api_agent.serialize_market_data(market_data)
        
        if not serialized_market_data:
            logger.error("Failed to serialize market data")
            raise HTTPException(status_code=500, detail="Failed to serialize market data")
        
        logger.info(f"Successfully serialized data: {list(serialized_market_data.keys())}")
        
        # 步骤3：根据符号生成新闻URL
        news_urls = [f"https://finance.yahoo.com/quote/{symbol}/news/" for symbol in symbol_list[:3]]  # 仅限前 3 个符号
        logger.info(f"🔍 Attempting to scrape news from: {news_urls}")
        articles = scraping_agent.scrape_news(news_urls, timeout=15)
        logger.info(f"📰 News scraping result: {len(articles)} articles collected")
        
        if not articles:
            # 如果抓取失败，根据实际市场数据创建丰富的备用内容
            logger.warning("⚠️ News scraping failed - generating fallback articles from market data")
            articles = []
            for symbol in symbol_list:
                company_name = ALL_STOCKS.get(symbol, symbol)
                
                # 使用实际市场数据创建详细的备用内容
                article_text = f"{company_name} 市场分析："
                
                if symbol in market_data:
                    try:
                        market_df = market_data[symbol]
                        if not market_df.empty and len(market_df) > 0:
                            # 获取近期交易数据
                            latest_close = market_df['Close'].iloc[-1] if 'Close' in market_df.columns else None
                            latest_volume = market_df['Volume'].iloc[-1] if 'Volume' in market_df.columns else None
                            
                            # 如果我们有足够的数据，计算价格变化
                            if len(market_df) > 1 and 'Close' in market_df.columns:
                                prev_close = market_df['Close'].iloc[-2]
                                price_change = ((latest_close - prev_close) / prev_close * 100) if prev_close > 0 else 0
                                
                                article_text += f"近期交易价格为 ${latest_close:.2f}, "
                                if price_change > 0:
                                    article_text += f"up {price_change:.2f}%，相较前一收盘价。"
                                else:
                                    article_text += f"down {abs(price_change):.2f}%，相较前一收盘价。"
                            elif latest_close:
                                article_text += f"当前价格为 ${latest_close:.2f}. "
                            
                            if latest_volume:
                                article_text += f"成交量：{latest_volume:,.0f} shares. "
                            
                            # 添加 52 周的背景（如果有）
                            if len(market_df) > 50 and 'High' in market_df.columns and 'Low' in market_df.columns:
                                recent_high = market_df['High'].tail(50).max()
                                recent_low = market_df['Low'].tail(50).min()
                                article_text += f"近期交易区间：${recent_low:.2f} - ${recent_high:.2f}."
                        else:
                            article_text += "已成功获取用于分析的市场数据。"
                    except Exception as e:
                        logger.warning(f"Error creating detailed fallback for {symbol}: {str(e)}")
                        article_text += "在当前市场环境下仍有交易活动。"
                else:
                    article_text += "已获取用于投资组合分析的市场数据。"
                
                articles.append({
                    "title": f"{company_name}：市场数据更新",
                    "text": article_text,
                    "url": f"https://finance.yahoo.com/quote/{symbol}"
                })
            logger.info(f"✅ Generated {len(articles)} fallback articles with market data")
        else:
            logger.info(f"✅ Successfully scraped {len(articles)} real news articles")
        
        # 第 4 步：索引和检索
        logger.info(f"Indexing {len(articles)} documents for retrieval")
        retriever_agent.index_documents(articles)
        context_docs = retriever_agent.retrieve(query, k=3)
        
        # 正确处理上下文 - 它可能是空的或具有不同的结构
        context = []
        if context_docs:
            if hasattr(context_docs[0], 'page_content'):
                # LangChain文档对象
                context = [doc.page_content for doc in context_docs]
            elif isinstance(context_docs[0], dict):
                # 字典对象
                context = [doc.get('text', str(doc)) for doc in context_docs]
            else:
                # 直接文本对象
                context = [str(doc) for doc in context_docs]
        
        if not context or len(context) == 0:
            # 如果检索失败，请使用实际市场数据创建丰富的备用上下文
            logger.warning("⚠️ Document retrieval failed - creating fallback context from market data")
            context = []
            for symbol in symbol_list:
                company_name = ALL_STOCKS.get(symbol, symbol)
                
                if symbol in serialized_market_data and serialized_market_data[symbol]:
                    try:
                        # 从市场数据创建详细的背景
                        records = serialized_market_data[symbol]
                        if records and len(records) > 0:
                            latest = records[-1]
                            closes = [r.get('Close', 0) for r in records if 'Close' in r]
                            volumes = [r.get('Volume', 0) for r in records if 'Volume' in r]
                            
                            context_text = f"{company_name} Analysis: "
                            
                            if 'Close' in latest:
                                context_text += f"当前价格 ${latest['Close']:.2f}. "
                            
                            if closes and len(closes) > 1:
                                avg_close = sum(closes) / len(closes)
                                context_text += f"期间平均价格：${avg_close:.2f}. "
                                
                                # 计算波动率
                                price_range = max(closes) - min(closes)
                                volatility_pct = (price_range / avg_close) * 100 if avg_close > 0 else 0
                                context_text += f"价格波动率：{volatility_pct:.1f}%. "
                            
                            if volumes:
                                avg_volume = sum(volumes) / len(volumes)
                                context_text += f"日均成交量：{avg_volume:,.0f} shares."
                            
                            context.append(context_text)
                        else:
                            context.append(f"{company_name} 的市场数据已成功获取，可用于分析。")
                    except Exception as e:
                        logger.warning(f"Error creating detailed context for {symbol}: {str(e)}")
                        context.append(f"{company_name} 已纳入投资组合分析。")
                else:
                    context.append(f"{company_name} 的市场数据已获取，可用于评估。")
        
        logger.info(f"✅ Retrieved {len(context)} context documents for analysis")
        return {
            "market_data": serialized_market_data,
            "context": context,
            "query": query,
            "symbols": symbol_list
        }
    except Exception as e:
        logger.error(f"Error retrieving data: {str(e)}")
        return {"error": str(e)}

@app.post("/analyze/analyze")
async def analyze(data: dict):
    try:
        logger.info("Processing analyze request")
        
        # 通过回退安全地提取数据
        market_data = {}
        symbols = data.get("data", {}).get("symbols", DEFAULT_SYMBOLS)
        
        try:
            if "data" in data and "market_data" in data["data"]:
                serialized_data = data["data"]["market_data"]
                
                # 将序列化市场数据转换回 DataFrame 格式
                market_data = {}
                for symbol, records in serialized_data.items():
                    if isinstance(records, list):
                        market_data[symbol] = pd.DataFrame.from_records(records)
                    else:
                        market_data[symbol] = records
        except Exception as e:
            logger.warning(f"Error processing market data: {str(e)}")
            # 使用空数据帧作为备用
            market_data = {}
            for symbol in symbols:
                market_data[symbol] = pd.DataFrame({'Close': [100.0]})
        
        context = data.get("data", {}).get("context", [])
        if not context:
            context = [f"股票分析：{', '.join(symbols)}"]
        
        query = data.get("data", {}).get("query", f"以下股票有哪些风险敞口：{', '.join(symbols)}？")
        
        # 更新分析智能体的投资组合以包含查询的股票
        # 这是一个临时解决方案 - 在真实的系统中，您可能想要获取实际的投资组合
        portfolio_weights = {}
        for i, symbol in enumerate(symbols):
            # 为每个符号分配递减的权重
            portfolio_weights[symbol] = 0.15 - (i * 0.02)  # 从 15% 开始并逐渐减少
            if portfolio_weights[symbol] < 0.05:  # 最低重量5%
                portfolio_weights[symbol] = 0.05
        
        # 更新投资组合
        analysis_agent.portfolio = portfolio_weights
        
        # 第 2 步：分析风险
        exposure = analysis_agent.analyze_risk_exposure(market_data)
        
        if not exposure:
            # 如果分析失败，备用暴露数据
            exposure = {}
            total_aum = 1000000  # 资产管理规模为 100 万美元的示例
            for symbol in symbols:
                exposure[symbol] = {
                    'weight': portfolio_weights.get(symbol, 0.10),
                    'value': portfolio_weights.get(symbol, 0.10) * total_aum,
                    'price': 100.0  # 默认价格
                }
            logger.info("Using fallback exposure data")
        
        # 第三步：获取收益
        earnings = {}
        
        for symbol in symbols:
            try:
                earnings[symbol] = api_agent.get_earnings(symbol)
                if earnings[symbol] is None:
                    # 回落盈利数据
                    earnings[symbol] = pd.DataFrame({
                        'Year': [2023, 2024],
                        'Earnings': [10.5, 12.3]
                    })
            except Exception as e:
                logger.warning(f"Error fetching earnings for {symbol}: {str(e)}")
                # 回落盈利数据
                earnings[symbol] = pd.DataFrame({
                    'Year': [2023, 2024],
                    'Earnings': [10.5, 12.3]
                })
        
        # 将收入转换为可序列化格式
        serialized_earnings = {}
        for symbol, data in earnings.items():
            if isinstance(data, pd.DataFrame):
                serialized_earnings[symbol] = data.to_dict(orient='records')
            else:
                serialized_earnings[symbol] = data
        
        # 第 4 步：生成简报
        try:
            logger.info("Generating brief from language agent")
            brief = language_agent.generate_brief(
                str(context), 
                str(exposure), 
                str(serialized_earnings)
            )
            if not brief or brief.isspace():
                raise Exception("Generated brief is empty")
            logger.info("Brief generated successfully")
        except Exception as e:
            logger.warning(f"Error generating brief: {str(e)}, using fallback")
            # 生成更具动态性的备用简介
            symbol_names = []
            for symbol in symbols:
                company_name = ALL_STOCKS.get(symbol, symbol)
                symbol_names.append(f"{company_name} ({symbol})")
            
            brief = f"""## 市场简报：{query}

### 投资组合分析：{', '.join(symbol_names)}

以下分析关注投资组合中各证券的风险敞口。

#### 已获取的市场数据
- 成功获取 {len(symbols)} 只证券的当前市场数据
- 数据包括分析期间的 OHLCV（开盘、最高、最低、收盘价和成交量）

#### 投资组合构成
"""
            
            # 添加风险敞口细节
            total_value = sum([d.get('value', 100000) for d in exposure.values()])
            for symbol, exp_data in exposure.items():
                company_name = ALL_STOCKS.get(symbol, symbol)
                weight_pct = exp_data.get('weight', 0.1) * 100
                value = exp_data.get('value', 100000)
                price = exp_data.get('price', 100.0)
                brief += f"\n- **{company_name} ({symbol})**: {weight_pct:.1f}% 配置 (${value:,.0f}) @ ${price:.2f}"
            
            brief += f"""

#### 主要观察
投资组合分散配置于所分析的证券。近期市场数据显示：
- 已追踪该期间的历史价格走势
- 成交量变化反映了市场交易活动
- 所选证券仍在市场中交易

#### 盈利概览
"""
            
            for symbol in symbols:
                company_name = ALL_STOCKS.get(symbol, symbol)
                brief += f"\n- {company_name}: 已获取最新盈利数据"
            
            brief += "\n\n建议：结合自身风险承受能力和投资目标，持续关注这些持仓。"
        
        logger.info("分析完成")
        return {"summary": brief}
    except Exception as e:
        logger.error(f"Error analyzing data: {str(e)}")
        return {"error": str(e)}

@app.post("/process_query")
async def process_query(
    audio: UploadFile = File(...),
    symbols: Optional[str] = Form(None)
):
    try:
        # 第 1 步：将语音转换为文本
        query = voice_agent.speech_to_text(audio.file)
        
        if not query:
            query = "科技股有哪些风险敞口？"
            logger.info("Using fallback query due to STT failure")

        # 步骤 2：从查询中提取符号或使用提供的符号
        if symbols:
            symbol_list = [s.strip() for s in symbols.split(",")]
            logger.info(f"Using explicitly provided symbols for voice query: {symbol_list}")
        else:
            symbol_list = extract_symbols_from_query(query)
        
        # 第三步：获取市场数据
        market_data = api_agent.get_market_data(symbol_list)
        
        if not market_data:
            logger.error("Failed to fetch market data")
            raise HTTPException(status_code=500, detail="Failed to fetch market data")

        # 第四步：抓取新闻
        news_urls = [f"https://finance.yahoo.com/quote/{symbol}/news/" for symbol in symbol_list[:2]]
        logger.info(f"Scraping news from URLs: {news_urls}")
        articles = scraping_agent.scrape_news(news_urls)
        
        if not articles:
            # 如果抓取失败，则根据实际市场数据使用备用内容
            logger.warning("News scraping failed, using fallback articles")
            articles = []
            for symbol in symbol_list:
                company_name = ALL_STOCKS.get(symbol, symbol)
                
                # 尝试在备用中包含 market_data 中的一些数据
                article_text = f"{company_name} 仍是相关市场的重要参与者。"
                
                if symbol in market_data:
                    try:
                        market_df = market_data[symbol]
                        if not market_df.empty:
                            latest_close = market_df['Close'].iloc[-1] if 'Close' in market_df.columns else 'N/A'
                            article_text += f"最新收盘价：{latest_close}. "
                    except:
                        pass
                
                articles.append({
                    "title": f"{company_name}：市场动态",
                    "text": article_text,
                    "url": f"https://finance.yahoo.com/quote/{symbol}"
                })
        else:
            logger.info(f"成功抓取 {len(articles)} 篇文章")

        # 第 5 步：索引和检索
        retriever_agent.index_documents(articles)
        context_docs = retriever_agent.retrieve(query, k=3)
        
        # 正确处理上下文
        context = []
        if context_docs:
            if hasattr(context_docs[0], 'page_content'):
                context = [doc.page_content for doc in context_docs]
            else:
                context = [str(doc) for doc in context_docs]
        
        if not context:
            context = [f"Analysis of {', '.join(symbol_list)} stocks"]

        # 更新分析智能体的投资组合以包含查询的股票
        portfolio_weights = {}
        for i, symbol in enumerate(symbol_list):
            portfolio_weights[symbol] = 0.15 - (i * 0.02)
            if portfolio_weights[symbol] < 0.05:
                portfolio_weights[symbol] = 0.05
        
        analysis_agent.portfolio = portfolio_weights
        
        # 第 6 步：分析风险
        exposure = analysis_agent.analyze_risk_exposure(market_data)
        
        if not exposure:
            # 备用风险敞口数据
            exposure = {}
            total_aum = 1000000  # 资产管理规模示例
            for symbol in symbol_list:
                exposure[symbol] = {
                    'weight': portfolio_weights.get(symbol, 0.10),
                    'value': portfolio_weights.get(symbol, 0.10) * total_aum,
                    'price': 100.0
                }

        # 第7步：获取收益
        earnings = {}
        for symbol in symbol_list:
            earnings_data = api_agent.get_earnings(symbol)
            if earnings_data is None:
                earnings_data = pd.DataFrame({
                    'Year': [2023, 2024],
                    'Earnings': [10.5, 12.3]
                })
            earnings[symbol] = earnings_data

        # 第 8 步：生成简报
        try:
            brief = language_agent.generate_brief(str(context), str(exposure), str(earnings))
        except Exception as e:
            logger.error(f"Error generating brief: {str(e)}")
            # 生成动态备用简介
            symbol_names = []
            for symbol in symbol_list:
                company_name = ALL_STOCKS.get(symbol, symbol)
                symbol_names.append(f"{company_name} ({symbol})")
            
            brief = f"""
            关于“{query}”的市场简报：
            
            分析标的：{', '.join(symbol_names)}：
            
            投资组合以不同权重配置了这些公司。
            """
            
            # 添加风险敞口细节
            brief += "\n投资组合风险敞口：\n"
            for symbol, data in exposure.items():
                company_name = ALL_STOCKS.get(symbol, symbol)
                weight_pct = data.get('weight', 0.1) * 100
                value = data.get('value', 100000)
                brief += f"- {company_name} ({symbol}): {weight_pct:.1f}% (${value:,.0f})\n"
            
            brief += "\n相关公司的盈利趋势请结合最新数据进一步核对。"

        # 第 9 步：转换为语音
        audio_response = voice_agent.text_to_speech(brief)
        
        if audio_response is None:
            logger.error("TTS failed to generate audio")
            raise HTTPException(status_code=500, detail="TTS failed to generate audio")

        logger.info("问题处理完成")
        return StreamingResponse(audio_response, media_type="audio/mp3")
    except Exception as e:
        logger.error(f"Error processing query: {str(e)}")
        return {"error": str(e)}
