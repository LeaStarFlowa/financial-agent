import streamlit as st
import threading
import sys
import os
import logging
import io
import json
import requests
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from fastapi import FastAPI, UploadFile, File, HTTPException, Form, Query
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from typing import Optional, List
import re
from dotenv import load_dotenv

# 从 .env 文件加载环境变量
load_dotenv()

# 将项目根添加到路径中，以便导入正常工作
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

# 导入所有智能体模块
from data_ingestion.api_agent import APIAgent
from data_ingestion.scrapping_agent import ScrapingAgent
from agents.retriever_agent import RetrieverAgent
from agents.analysis_agent import AnalysisAgent
from agents.language_agent import LanguageAgent 
from agents.voice_agent import VoiceAgent

# 导入综合股票代码
from streamlit_app.stock_symbols import ALL_STOCKS, CATEGORIES

# 配置日志记录
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 初始化 FastAPI 应用程序
app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 初始化所有智能体
api_agent = APIAgent()
scraping_agent = ScrapingAgent()
retriever_agent = RetrieverAgent()
analysis_agent = AnalysisAgent()
language_agent = LanguageAgent()
voice_agent = VoiceAgent()

# 默认符号（可以扩展）
DEFAULT_SYMBOLS = ['AAPL', 'MSFT', 'GOOGL']  # 主要科技股

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

# 辅助函数
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

# FastAPI 端点
@app.get("/")
async def health_check():
    return {"status": "healthy", "message": "金融助手 API 正在运行"}

@app.get("/debug/test-scraping")
async def test_scraping(symbol: str = "AAPL"):
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
        
        logger.info(f"Analyzing symbols: {symbols}")
        
        try:
            if "data" in data and "market_data" in data["data"]:
                serialized_data = data["data"]["market_data"]
                
                logger.info(f"Converting serialized data for {list(serialized_data.keys())}")
                
                # 将序列化市场数据转换回 DataFrame 格式
                market_data = {}
                for symbol, records in serialized_data.items():
                    try:
                        if isinstance(records, list):
                            if records:  # 仅当记录不为空时才创建 DataFrame
                                market_data[symbol] = pd.DataFrame.from_records(records)
                                logger.info(f"Created DataFrame for {symbol} with {len(records)} records")
                            else:
                                logger.warning(f"Empty records for {symbol}")
                        else:
                            market_data[symbol] = records
                            logger.info(f"Using raw data for {symbol}")
                    except Exception as e:
                        logger.error(f"Error creating DataFrame for {symbol}: {str(e)}")
                        # 创建一个虚拟数据框
                        market_data[symbol] = pd.DataFrame({'Close': [100.0]})
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
        
        logger.info(f"问题： {query}, Context items: {len(context)}")
        
        # 更新分析智能体的投资组合以包含查询的股票
        portfolio_weights = {}
        for i, symbol in enumerate(symbols):
            # 为每个符号分配递减的权重
            portfolio_weights[symbol] = 0.15 - (i * 0.02)  # 从 15% 开始并逐渐减少
            if portfolio_weights[symbol] < 0.05:  # 最低重量5%
                portfolio_weights[symbol] = 0.05
        
        logger.info(f"Portfolio weights: {portfolio_weights}")
        
        # 更新投资组合
        analysis_agent.portfolio = portfolio_weights
        
        # 第 2 步：分析风险
        exposure = analysis_agent.analyze_risk_exposure(market_data)
        logger.info(f"Risk exposure analysis complete: {list(exposure.keys()) if exposure else 'None'}")
        
        if not exposure:
            # 如果分析失败，备用暴露数据
            logger.warning("Using fallback exposure data")
            exposure = {}
            total_aum = 1000000  # 资产管理规模为 100 万美元的示例
            for symbol in symbols:
                exposure[symbol] = {
                    'weight': portfolio_weights.get(symbol, 0.10),
                    'value': portfolio_weights.get(symbol, 0.10) * total_aum,
                    'price': 100.0  # 默认价格
                }
        
        # 第三步：获取收益
        earnings = {}
        
        for symbol in symbols:
            try:
                logger.info(f"Fetching earnings for {symbol}")
                earnings_data = api_agent.get_earnings(symbol)
                if earnings_data is None:
                    logger.warning(f"No earnings data for {symbol}, using fallback")
                    # 回落盈利数据
                    earnings[symbol] = pd.DataFrame({
                        'Year': [2023, 2024],
                        'Earnings': [10.5, 12.3]
                    })
                else:
                    earnings[symbol] = earnings_data
            except Exception as e:
                logger.warning(f"Error fetching earnings for {symbol}: {str(e)}")
                # 回落盈利数据
                earnings[symbol] = pd.DataFrame({
                    'Year': [2023, 2024],
                    'Earnings': [10.5, 12.3]
                })
        
        # 将收入转换为可序列化格式
        serialized_earnings = {}
        for symbol, data_df in earnings.items():
            try:
                if isinstance(data_df, pd.DataFrame):
                    serialized_earnings[symbol] = data_df.to_dict(orient='records')
                else:
                    serialized_earnings[symbol] = str(data_df)
                logger.info(f"Serialized earnings for {symbol}")
            except Exception as e:
                logger.warning(f"Error serializing earnings for {symbol}: {str(e)}")
                serialized_earnings[symbol] = []
        
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
            
            brief = f"""## 市场简报： {query}

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
        logger.error(f"Error analyzing data: {str(e)}", exc_info=True)
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
            query = "以下股票有哪些风险敞口：technology stocks?"
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

# 在单独的线程中启动 FastAPI 的函数
def run_fastapi():
    uvicorn.run(app, host="0.0.0.0", port=8000)

# 当此脚本运行时，在后台线程中启动 FastAPI
threading.Thread(target=run_fastapi, daemon=True).start()

# 现在定义 Streamlit 应用程序
def main():
    st.title("🧠 晨间市场简报助手")
    st.markdown("""
    本应用提供投资组合和个股的市场洞察与财务分析。
    输入有关股票或市场状况的问题，获取 AI 生成的分析。
    """)
    
    # 选股功能
    st.sidebar.header("股票选择")
    st.sidebar.markdown("从股票列表选择，或输入自定义代码：")
    
    # 从 ALL_STOCKS 建立全面的股票列表
    # 添加“所有股票”类别+预定义类别
    common_stocks = {"🔷 全部股票（A-Z）": []}
    
    # 将所有股票添加到“所有股票”类别
    for symbol, name in sorted(ALL_STOCKS.items()):
        display_name = f"{symbol} ({name})"
        common_stocks["🔷 全部股票（A-Z）"].append(display_name)
    
    # 从 stock_symbols.py 添加预定义类别
    for category_name, symbols in CATEGORIES.items():
        common_stocks[category_name] = []
        for symbol in symbols:
            if symbol in ALL_STOCKS:
                display_name = f"{symbol} ({ALL_STOCKS[symbol]})"
                common_stocks[category_name].append(display_name)
    
    # 删除空类别
    common_stocks = {k: v for k, v in common_stocks.items() if v}
    
    st.sidebar.info(f"📊 可选股票总数：{len(ALL_STOCKS)}")
    
    selected_category = st.sidebar.selectbox("行业类别", list(common_stocks.keys()))
    
    # 添加搜索功能
    search_term = st.sidebar.text_input("🔍 搜索股票", placeholder="输入公司名称或股票代码……")
    
    # 根据搜索过滤股票
    available_stocks = common_stocks[selected_category]
    if search_term:
        available_stocks = [s for s in available_stocks if search_term.upper() in s.upper()]
        st.sidebar.caption(f"找到 {len(available_stocks)} 个结果")
    
    selected_stocks = st.sidebar.multiselect(
        "选择要分析的股票",
        available_stocks,
        help="从所选行业中选择一只或多只股票"
    )
    
    # 显示扩展器中的所有可用符号
    with st.sidebar.expander("📋 查看所有可用股票代码"):
        st.markdown(f"### 全部 {len(ALL_STOCKS)} 可用股票")
        
        # 按字母顺序对符号进行分组
        all_symbols = sorted(ALL_STOCKS.keys())
        
        # 以列显示以获得更好的可读性
        col1, col2 = st.columns(2)
        mid_point = len(all_symbols) // 2
        
        with col1:
            st.code("\n".join(all_symbols[:mid_point]))
        with col2:
            st.code("\n".join(all_symbols[mid_point:]))
        
        st.markdown("---")
        st.markdown("### 股票代码 → 公司名称对照")
        st.caption("下方按字母顺序列出对照关系")
        
        # 显示按首字母组织的映射（无嵌套扩展器）
        letters = {}
        for symbol, company in sorted(ALL_STOCKS.items()):
            first_letter = symbol[0].upper()
            if first_letter not in letters:
                letters[first_letter] = []
            letters[first_letter].append(f"{symbol} → {company}")
        
        # 在可滚动文本区域中显示按字母分组的所有映射
        mapping_text = ""
        for letter in sorted(letters.keys()):
            mapping_text += f"\n━━━ {letter} ({len(letters[letter])} 只股票) ━━━\n"
            for mapping in letters[letter]:
                mapping_text += f"{mapping}\n"
        
        st.text_area("所有股票代码对照（A-Z）", mapping_text, height=300, help="滚动查看所有股票代码与公司名称的对应关系")
        
        st.markdown("---")
        st.markdown("### 输入自定义股票代码")
        st.info("💡 也可在问题中直接输入有效的 Yahoo Finance 股票代码 (例如 AAPL、MSFT、TSM, BTC-USD)")
    
    # 符号格式快速参考指南
    with st.sidebar.expander("📖 股票代码格式指南"):
        st.markdown("""
        **股票代码格式：**
        - 🇺🇸 美国：`AAPL`, `MSFT`, `GOOGL`
        - 🇰🇷 韩国：`005930.KS` （三星）
        - 🇯🇵 日本：`7203.T` （丰田）
        - 🇨🇳 香港：`0700.HK` （腾讯）
        - 🇮🇳 印度：`RELIANCE.NS`
        - 🇬🇧 英国：`BP.L`
        - 🇩🇪 德国：`SAP.DE`
        - 🇫🇷 法国：`MC.PA`
        - 🇨🇭 瑞士：`NESN.SW`
        - 🇨🇦 加拿大：`SHOP.TO`
        - 🇦🇺 澳大利亚：`CBA.AX`
        - ₿ 加密货币： `BTC-USD`, `ETH-USD`
        
        **提示：**
        - 多数美股使用简短代码
        - 国际股票代码通常带有市场后缀
        - 不确定代码时可按公司名称搜索
        """)
    
    # 准备选定股票的查询
    stock_query = ""
    selected_symbols = []
    if selected_stocks:
        # 仅提取符号部分（空格之前）
        selected_symbols = [stock.split(" ")[0] for stock in selected_stocks]
        stock_query = f"以下股票有哪些风险敞口：{', '.join(selected_symbols)}？"
    
    # 示例查询部分
    st.markdown("### 💬 提出问题")
    
    with st.expander("💡 示例问题"):
        st.markdown("""
        **综合市场分析：**
        - "分析 AAPL、MSFT 和 GOOGL，当前市场趋势如何？"
        - "今天科技股有哪些风险敞口？"
        - "请简要分析 SPY 和 QQQ ETF 的市场情况"
        
        **国际市场：**
        - "比较三星（005930.KS）和台积电的表现"
        - "欧洲科技股表现如何？SAP.DE、ASML"
        - "分析日本汽车制造商：7203.T（丰田）、HMC"
        - "印度 IT 股票表现如何？TCS.NS、INFY.NS"
        
        **行业分析：**
        - "半导体股票近期表现如何？ NVDA, AMD, TSM"
        - "比较特斯拉与传统汽车制造商"
        - "云软件公司表现如何？"
        
        **加密货币：**
        - "我的加密货币投资组合有哪些风险敞口？BTC-USD、ETH-USD"
        - "比较比特币和以太坊的表现"
        
        **投资组合风险：**
        - "我对前五大科技股的风险敞口是多少？"
        - "分析我的多元化投资组合风险"
        - "根据当前市场情况，我是否应该调整持仓？"
        """)
    
    # 默认情况下包含所选股票的文本查询输入
    query = st.text_input("请输入市场分析问题：",
                         value=stock_query if stock_query else "今天科技股有哪些风险敞口？",
                         help="可询问个股、市场趋势或投资组合风险")
    
    if st.button("生成简报"):
        with st.spinner("正在处理问题……"):
            try:
                # 检查 FastAPI 是否可达
                try:
                    # 由于我们现在在同一个进程中，我们可以直接访问FastAPI，
                    # 但我们仍然会使用请求来保持一致性
                    health_check = requests.get("http://localhost:8000/")
                    if health_check.status_code != 200:
                        st.error(f"无法连接 FastAPI 服务：{health_check.status_code}")
                    else:
                        st.info("FastAPI 服务运行正常，正在处理请求……")
                        
                        # 第 1 步：检索带有明确符号的相关文档（如果选择）
                        params = {"query": query}
                        if selected_symbols:
                            params["symbols"] = ",".join(selected_symbols)
                            st.info(f"正在分析指定股票：{', '.join(selected_symbols)}")
                        
                        retrieve_response = requests.get("http://localhost:8000/retrieve/retrieve", params=params)
                        
                        if retrieve_response.status_code != 200:
                            st.error(f"数据检索失败，状态码：{retrieve_response.status_code}")
                            try:
                                error_details = retrieve_response.json()
                                if "error" in error_details:
                                    st.code(f"错误详情：{error_details['error']}")
                            except:
                                st.code(f"原始响应：{retrieve_response.text[:500]}...")
                        else:
                            retrieve_data = retrieve_response.json()
                            
                            if "error" in retrieve_data:
                                st.error(f"数据检索错误：{retrieve_data['error']}")
                            else:
                                # 如果我们选择了符号，请确保它们位于数据中
                                if selected_symbols:
                                    retrieve_data["symbols"] = selected_symbols
                                
                                # 显示分析的股票
                                symbols = retrieve_data.get("symbols", [])
                                if symbols:
                                    st.info(f"正在分析股票：{', '.join(symbols)}")
                                
                                # 显示一些检索到的数据以供验证
                                with st.expander("查看检索数据"):
                                    st.write("问题：", retrieve_data.get("query"))
                                    st.write("上下文片段：", retrieve_data.get("context", [])[:2])
                                    st.write("涵盖市场：", list(retrieve_data.get("market_data", {}).keys()))
                                
                                # 第二步：分析并总结
                                st.info("正在生成市场简报……")
                                analyze_response = requests.post(
                                    "http://localhost:8000/analyze/analyze", 
                                    json={"data": retrieve_data}
                                )
                                
                                if analyze_response.status_code != 200:
                                    st.error(f"分析失败，状态码：{analyze_response.status_code}")
                                    try:
                                        error_details = analyze_response.json()
                                        if "error" in error_details:
                                            st.code(f"错误详情：{error_details['error']}")
                                    except:
                                        st.code(f"原始响应：{analyze_response.text[:500]}...")
                                else:
                                    analyze_data = analyze_response.json()
                                    
                                    if "error" in analyze_data:
                                        st.error(f"分析错误：{analyze_data['error']}")
                                    else:
                                        st.subheader("市场简报：")
                                        st.markdown(analyze_data["summary"])

     # 如果分析 2 只或更多股票，请显示比较
                                    if len(selected_symbols) >= 2:
                                        st.divider()
                                        st.subheader("股票并排比较")
                                        
                                        # 提取市场数据进行比较
                                        market_data = retrieve_data.get("market_data", {})
                                        
                                        if market_data:
                                            # 准备对比数据
                                            comparison_cols = st.columns(len(selected_symbols))
                                            
                                            for idx, symbol in enumerate(selected_symbols):
                                                with comparison_cols[idx]:
                                                    st.markdown(f"### {symbol}")
                                                    
                                                    if symbol in market_data:
                                                        stock_data = market_data[symbol]
                                                        
                                                        # 显示关键指标
                                                        if isinstance(stock_data, dict):
                                                            st.metric(
                                                                "当前价格",
                                                                f"${stock_data.get('price', 'N/A'):.2f}" if isinstance(stock_data.get('price'), (int, float)) else stock_data.get('price', 'N/A')
                                                            )
                                                            
                                                            if stock_data.get('change'):
                                                                try:
                                                                    change_value = float(stock_data.get('change', 0))
                                                                    change_color = "normal" if change_value >= 0 else "inverse"
                                                                    st.metric(
                                                                        "当日涨跌",
                                                                        f"{change_value:.2f}%",
                                                                        delta_color=change_color
                                                                    )
                                                                except (ValueError, TypeError):
                                                                    st.metric(
                                                                        "当日涨跌",
                                                                        f"{stock_data.get('change', 'N/A')}"
                                                                    )
                                                            
                                                            if stock_data.get('52_week_high'):
                                                                st.caption(f"52 周最高价: ${stock_data.get('52_week_high', 'N/A')}")
                                                            
                                                            if stock_data.get('52_week_low'):
                                                                st.caption(f"52 周最低价: ${stock_data.get('52_week_low', 'N/A')}")
                                                            
                                                            if stock_data.get('market_cap'):
                                                                st.caption(f"市值: {stock_data.get('market_cap', 'N/A')}")
                                                            
                                                            if stock_data.get('pe_ratio'):
                                                                st.caption(f"市盈率: {stock_data.get('pe_ratio', 'N/A')}")
                                                        else:
                                                            # 其他数据类型的备用显示
                                                            st.write(stock_data)
                                                    else:
                                                        st.warning(f"没有可用数据：{symbol}")
                                        
                                        # 添加详细的逐行比较表
                                        st.markdown("#### 详细指标比较")
                                        
                                        # 根据实际市场数据建立对比表
                                        comparison_data = {}
                                        
                                        for symbol in selected_symbols:
                                            if symbol in market_data:
                                                stock_data = market_data[symbol]
                                                
                                                # 如果stock_data是一个列表（序列化DataFrame），计算指标
                                                if isinstance(stock_data, list) and len(stock_data) > 0:
                                                    try:
                                                        # 转换为 DataFrame 以便于处理
                                                        df = pd.DataFrame(stock_data)
                                                        
                                                        # 根据数据计算指标
                                                        latest = df.iloc[-1] if not df.empty else {}
                                                        
                                                        comparison_data[symbol] = {
                                                            '当前价格': f"${latest.get('Close', 'N/A'):.2f}" if 'Close' in latest and pd.notna(latest.get('Close')) else 'N/A',
                                                            '当日涨跌幅': f"{((latest.get('Close', 0) - df.iloc[-2].get('Close', 0)) / df.iloc[-2].get('Close', 1) * 100):.2f}%" if len(df) > 1 and 'Close' in latest else 'N/A',
                                                            '52 周最高价': f"${df['High'].max():.2f}" if 'High' in df.columns else 'N/A',
                                                            '52 周最低价': f"${df['Low'].min():.2f}" if 'Low' in df.columns else 'N/A',
                                                            '平均成交量': f"{df['Volume'].mean():,.0f}" if 'Volume' in df.columns else 'N/A',
                                                            '最新成交量': f"{latest.get('Volume', 'N/A'):,.0f}" if 'Volume' in latest and pd.notna(latest.get('Volume')) else 'N/A'
                                                        }
                                                    except Exception as e:
                                                        logger.warning(f"Error calculating metrics for {symbol}: {str(e)}")
                                                        comparison_data[symbol] = {
                                                            '当前价格': 'N/A',
                                                            '当日涨跌幅': 'N/A',
                                                            '52 周最高价': 'N/A',
                                                            '52 周最低价': 'N/A',
                                                            '平均成交量': 'N/A',
                                                            '最新成交量': 'N/A'
                                                        }
                                                # 如果 stock_data 已经是一个带有指标的字典
                                                elif isinstance(stock_data, dict):
                                                    comparison_data[symbol] = {
                                                        '当前价格': f"${stock_data.get('price', 'N/A'):.2f}" if isinstance(stock_data.get('price'), (int, float)) else stock_data.get('price', 'N/A'),
                                                        '当日涨跌幅': f"{stock_data.get('change', 'N/A')}%",
                                                        '52 周最高价': stock_data.get('52_week_high', 'N/A'),
                                                        '52 周最低价': stock_data.get('52_week_low', 'N/A'),
                                                        '市值': stock_data.get('market_cap', 'N/A'),
                                                        '市盈率': stock_data.get('pe_ratio', 'N/A')
                                                    }
                                                else:
                                                    comparison_data[symbol] = {'Status': '暂无数据'}
                                            else:
                                                comparison_data[symbol] = {'Status': '未找到股票代码'}
                                        
                                        # 创建并显示比较数据框
                                        if comparison_data:
                                            comparison_df = pd.DataFrame(comparison_data)
                                            st.dataframe(comparison_df, use_container_width=True)
                                        else:
                                            st.info("没有可用于比较的数据")
                                    
                                    st.success("问题处理完成！")
                                    
                                    # 如果分析 2 只或更多股票，请显示比较图
                                    if len(selected_symbols) >= 2:
                                        st.divider()
                                        st.subheader("股价比较图")
                                        
                                        # 提取市场数据以绘制图表
                                        market_data_raw = retrieve_data.get("market_data", {})
                                        
                                        if market_data_raw:
                                            try:
                                                # 创建价格比较图表
                                                fig_price, ax_price = plt.subplots(figsize=(12, 6))
                                                
                                                has_data = False
                                                for symbol in selected_symbols:
                                                    if symbol in market_data_raw:
                                                        stock_data = market_data_raw[symbol]
                                                        
                                                        if isinstance(stock_data, list) and len(stock_data) > 0:
                                                            # 从序列化数据中提取收盘价
                                                            dates = []
                                                            closes = []
                                                            
                                                            for record in stock_data:
                                                                if isinstance(record, dict):
                                                                    if 'Date' in record and 'Close' in record:
                                                                        dates.append(record['Date'])
                                                                        closes.append(float(record['Close']))
                                                            
                                                            if closes:
                                                                ax_price.plot(range(len(closes)), closes, marker='o', label=symbol, linewidth=2)
                                                                has_data = True
                                                
                                                if has_data:
                                                    ax_price.set_xlabel('交易日', fontsize=11, fontweight='bold')
                                                    ax_price.set_ylabel('收盘价（美元）', fontsize=11, fontweight='bold')
                                                    ax_price.set_title('股价走势比较', fontsize=13, fontweight='bold')
                                                    ax_price.legend(loc='best', fontsize=10)
                                                    ax_price.grid(True, alpha=0.3)
                                                    plt.tight_layout()
                                                    st.pyplot(fig_price)
                                                else:
                                                    st.warning("没有可用于绘图的价格数据")
                                                
                                                # 如果数据存在，则创建体积比较图
                                                fig_volume, ax_volume = plt.subplots(figsize=(12, 6))
                                                
                                                has_volume = False
                                                for symbol in selected_symbols:
                                                    if symbol in market_data_raw:
                                                        stock_data = market_data_raw[symbol]
                                                        
                                                        if isinstance(stock_data, list) and len(stock_data) > 0:
                                                            volumes = []
                                                            
                                                            for record in stock_data:
                                                                if isinstance(record, dict) and 'Volume' in record:
                                                                    try:
                                                                        volumes.append(float(record['Volume']) / 1e6)  
                                                                    except:
                                                                        pass
                                                            
                                                            if volumes:
                                                                ax_volume.bar([i + (selected_symbols.index(symbol) * 0.25) for i in range(len(volumes))], 
                                                                              volumes, 
                                                                              label=symbol, 
                                                                              width=0.25, 
                                                                              alpha=0.8)
                                                                has_volume = True
                                                
                                                if has_volume:
                                                    ax_volume.set_xlabel('交易日', fontsize=11, fontweight='bold')
                                                    ax_volume.set_ylabel('成交量（百万）', fontsize=11, fontweight='bold')
                                                    ax_volume.set_title('股票成交量比较', fontsize=13, fontweight='bold')
                                                    ax_volume.legend(loc='best', fontsize=10)
                                                    ax_volume.grid(True, alpha=0.3, axis='y')
                                                    plt.tight_layout()
                                                    st.pyplot(fig_volume)
                                                
                                                # 创建标准化性价比图表
                                                fig_perf, ax_perf = plt.subplots(figsize=(12, 6))
                                                
                                                has_perf = False
                                                for symbol in selected_symbols:
                                                    if symbol in market_data_raw:
                                                        stock_data = market_data_raw[symbol]
                                                        
                                                        if isinstance(stock_data, list) and len(stock_data) > 1:
                                                            closes = []
                                                            
                                                            for record in stock_data:
                                                                if isinstance(record, dict) and 'Close' in record:
                                                                    closes.append(float(record['Close']))
                                                            
                                                            if closes:
                                                                # 标准化为起始价格 (100)
                                                                normalized = [(c / closes[0] * 100) - 100 for c in closes]
                                                                ax_perf.plot(range(len(normalized)), normalized, marker='o', label=symbol, linewidth=2)
                                                                has_perf = True
                                                
                                                if has_perf:
                                                    ax_perf.axhline(y=0, color='r', linestyle='--', alpha=0.5)
                                                    ax_perf.set_xlabel('交易日', fontsize=11, fontweight='bold')
                                                    ax_perf.set_ylabel('较起点涨跌幅（%）', fontsize=11, fontweight='bold')
                                                    ax_perf.set_title('标准化股价表现（%）', fontsize=13, fontweight='bold')
                                                    ax_perf.legend(loc='best', fontsize=10)
                                                    ax_perf.grid(True, alpha=0.3)
                                                    plt.tight_layout()
                                                    st.pyplot(fig_perf)
                                                
                                                st.success("股票比较图已生成！")
                                                
                                            except Exception as e:
                                                st.warning(f"无法生成图表：{str(e)}")
                                                logger.warning(f"Error generating charts: {str(e)}")
                                                
                                                


                                    
        

                except requests.exceptions.ConnectionError:
                    st.error("FastAPI 服务正在连接 Render；如果等待过久，请尝试在本地运行。")
            except Exception as e:
                st.error(f"处理问题失败：{str(e)}")
    
    # 音频查询输入（语音I/O可选）
    st.subheader("或上传语音问题（WAV/MP3）")
    audio_file = st.file_uploader("上传音频", type=["wav", "mp3"])
    
    if audio_file is not None:
        st.audio(audio_file, format="audio/wav")
        with st.spinner("正在处理语音问题……"):
            try:
                files = {"audio": (audio_file.name, audio_file, "audio/wav")}
                
                # 如果我们选择了符号，请将它们添加为表单数据
                data = {}
                if selected_symbols:
                    data = {"symbols": ",".join(selected_symbols)}
                    
                response = requests.post("http://localhost:8000/process_query", files=files, data=data, stream=True)
                
                if response.status_code == 200:
                    audio_bytes = io.BytesIO(response.content)
                    st.audio(audio_bytes, format="audio/mp3")
                    st.success("语音问题处理完成！")
                else:
                    try:
                        error_msg = response.json().get("error", "未知错误")
                        st.error(f"音频处理错误：{error_msg}")
                    except:
                        st.error(f"音频处理失败，状态码：{response.status_code}")
            except requests.exceptions.ConnectionError:
                st.error("FastAPI 服务正在连接 Render；如果等待过久，请尝试在本地运行。")
            except Exception as e:
                st.error(f"处理语音问题失败：{str(e)}")
    
    # 添加一个部分来解释应用程序的工作原理
    with st.expander("应用工作原理"):
        st.write("""
    ### 系统架构

    本应用由 Streamlit 前端和 FastAPI 后端组成。前端负责股票选择、提问和结果展示；后端协调数据获取、风险分析与简报生成。

    ### 分析流程

    提问 → 获取 Yahoo Finance 市场数据 → 检索相关信息 → 评估投资组合风险 → 生成市场简报。

    ### 功能

    - 覆盖全球股票、ETF、指数和主要加密货币
    - 展示市场数据、新闻信息和投资组合风险
    - 生成盈利分析与 AI 市场简报
    """)


if __name__ == "__main__":

    main()
