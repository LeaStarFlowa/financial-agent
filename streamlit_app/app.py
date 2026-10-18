import streamlit as st
import requests
import io
import logging
import json
import os
import pandas as pd
import matplotlib.pyplot as plt
import sys
from pathlib import Path
from stock_symbols import ALL_STOCKS, CATEGORIES, get_stock_display_name, search_stocks

# 将父目录添加到导入智能体的路径
parent_dir = str(Path(__file__).parent.parent)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from agents.prediction_agent import PredictionAgent
from agents.graphing_agent import GraphingAgent

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 初始化智能体
prediction_agent = PredictionAgent()
graphing_agent = GraphingAgent()

# 根据环境确定API URL
# 在 Streamlit Cloud 上：在 Secrets 中设置 API_URL
# 本地：使用 localhost:8000
try:
    # 首先尝试从 Streamlit Secrets 中获取（Streamlit Cloud）
    API_URL = st.secrets.get("API_URL", os.environ.get("API_URL", "http://localhost:8000"))
except Exception:
    # 如果机密不可用，则回退到环境变量
    API_URL = os.environ.get("API_URL", "http://localhost:8000")

# 调试：记录正在使用的 API URL
st.sidebar.text(f"API: {API_URL}")

st.title("🧠 晨间市场简报助手")
st.markdown("""
**AI 驱动的专业市场洞察，覆盖 460 多只全球股票！**

获取全球主要交易所股票的综合财务分析：
🇺🇸 美国市场 | 🌏 亚洲市场 | 🌍 欧洲市场 | 📊 ETF | ₿ 加密货币

在侧边栏选择股票，然后在下方提出问题！
""")

# 数据源信息
st.info("""
📊 **数据来源：** 通过 Yahoo Finance API 获取实时市场数据
🤖 **AI 分析：** 多智能体系统评估投资组合风险
⚡ **提示：** 云端部署时，新闻抓取可能使用结合市场统计数据的备用内容
""")

# 显示当前API端点（对于调试有用）

# 选股功能
st.sidebar.header("📈 股票选择")
st.sidebar.markdown("**可从 400 多只全球股票、ETF 和加密货币中选择！**")

# 选型方法
selection_method = st.sidebar.radio(
    "选择方式：",
    ["按类别浏览", "按名称或代码搜索", "输入自定义代码"]
)

selected_stocks = []
selected_symbols = []

if selection_method == "按类别浏览":
    # 基于类别的选择
    selected_category = st.sidebar.selectbox("选择类别", list(CATEGORIES.keys()))
    
    # 获取该类别的股票
    category_stocks = CATEGORIES[selected_category]
    stock_options = [get_stock_display_name(symbol) for symbol in category_stocks]
    
    selected_stocks = st.sidebar.multiselect(
        f"从以下类别选择股票：{selected_category}",
        stock_options,
        help="选择一只或多只股票进行分析"
    )
    
    # 提取符号
    selected_symbols = [stock.split(" - ")[0] for stock in selected_stocks]

elif selection_method == "按名称或代码搜索":
    # 基于搜索的选择
    search_query = st.sidebar.text_input(
        "🔍 搜索股票",
        placeholder="输入公司名称或股票代码（例如 Apple、MSFT、Tesla）",
        help="搜索 400 多只股票"
    )
    
    if search_query:
        search_results = search_stocks(search_query)
        
        if search_results:
            st.sidebar.success(f"找到 {len(search_results)} 个结果！")
            
            # 将结果显示为选择框
            result_options = [f"{symbol} - {name}" for symbol, name in search_results[:20]]  # 限制为 20 个结果
            
            selected_stocks = st.sidebar.multiselect(
                "从搜索结果中选择",
                result_options,
                help="选择一只或多只股票"
            )
            
            # 提取符号
            selected_symbols = [stock.split(" - ")[0] for stock in selected_stocks]
        else:
            st.sidebar.warning("未找到股票，请尝试其他关键词。")
            
elif selection_method == "输入自定义代码":
    # 手动输入任何股票
    st.sidebar.info("💡 输入任意 Yahoo Finance 股票代码")
    custom_symbols_input = st.sidebar.text_input(
        "输入股票代码",
        placeholder="例如 AAPL、MSFT、TSM",
        help="输入一个或多个代码，多个代码用逗号分隔"
    )
    
    if custom_symbols_input:
        # 解析逗号分隔的符号
        selected_symbols = [s.strip().upper() for s in custom_symbols_input.split(",") if s.strip()]
        selected_stocks = [get_stock_display_name(symbol) for symbol in selected_symbols]
        
        st.sidebar.success(f"已选择：{', '.join(selected_symbols)}")

# 显示所选股票的详细信息
if selected_symbols:
    st.sidebar.markdown("### ✅ 已选股票：")
    for symbol in selected_symbols:
        company_name = ALL_STOCKS.get(symbol, "自定义代码")
        if company_name != "自定义代码":
            st.sidebar.text(f"• {symbol} - {company_name}")
        else:
            st.sidebar.text(f"• {symbol}")
    
    st.sidebar.markdown(f"**共选择 {len(selected_symbols)} 只股票**")
    
    # 准备选定股票的查询
    stock_query = f"分析 {', '.join(selected_symbols)}，当前市场状况和风险敞口如何？"
else:
    stock_query = ""
    st.sidebar.info("👆 请先在上方选择要分析的股票")

# 显示可用股票数量
st.sidebar.markdown("---")
st.sidebar.info(f"📊 可选股票总数：{len(ALL_STOCKS)}")
st.sidebar.caption("美国 248 | 亚洲 49 | 欧洲 40 | ETF 98 | 加密货币 20")

# 快速参考指南
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

# 默认情况下包含所选股票的文本查询输入
st.markdown("### 💬 提出问题")

# 示例查询
with st.expander("💡 示例问题"):
    st.markdown("""
    - "分析 AAPL、MSFT 和 GOOGL，当前市场趋势如何？"
    - "比较三星（005930.KS）和台积电的表现"
    - "我的加密货币投资组合有哪些风险敞口？BTC-USD、ETH-USD"
    - "欧洲科技股表现如何？SAP.DE、ASML"
    - "请简要分析 SPY 和 QQQ ETF 的市场情况"
    - "比较特斯拉与传统汽车制造商"
    - "半导体股票近期表现如何？"
    """)

query = st.text_input(
    "请输入市场分析问题：",
    value=stock_query if stock_query else "今天科技股有哪些风险敞口？",
    help="可询问个股、市场趋势或投资组合风险"
)

if st.button("生成简报"):
    with st.spinner("正在处理问题……"):
        try:
            # 检查 FastAPI 是否可达
            try:
                st.info(f"🔗 正在连接：{API_URL}")
                logger.info(f"Attempting to connect to {API_URL}")
                
                health_check = requests.get(f"{API_URL}/", timeout=10)
                if health_check.status_code != 200:
                    st.error(f"无法连接 FastAPI 服务：{health_check.status_code} - {health_check.text}")
                    logger.error(f"FastAPI health check failed: {health_check.status_code} - {health_check.text}")
                else:
                    st.success("✅ 已连接后端！")
                    logger.info("FastAPI server is healthy")
                    
                    # 第 1 步：检索带有明确符号的相关文档（如果选择）
                    logger.info(f"Sending retrieve request with query: {query}")
                    
                    # 将选定的符号添加为查询参数（如果存在）
                    params = {"query": query}
                    if selected_symbols:
                        params["symbols"] = ",".join(selected_symbols)
                        st.info(f"正在分析指定股票：{', '.join(selected_symbols)}")
                    
                    retrieve_response = requests.get(f"{API_URL}/retrieve/retrieve", params=params, timeout=30)
                    logger.info(f"Retrieve response status: {retrieve_response.status_code}")
                    
                    if retrieve_response.status_code != 200:
                        st.error(f"数据检索失败，状态码：{retrieve_response.status_code}")
                        logger.error(f"Retrieval failed: {retrieve_response.status_code} - {retrieve_response.text}")
                        
                        # 添加详细错误信息
                        try:
                            error_details = retrieve_response.json()
                            if "error" in error_details:
                                st.code(f"错误详情：{error_details['error']}")
                        except:
                            st.code(f"原始响应：{retrieve_response.text[:500]}...")
                    else:
                        retrieve_data = retrieve_response.json()
                        logger.info(f"Retrieved data successfully")
                        
                        if "error" in retrieve_data:
                            st.error(f"❌ {retrieve_data['error']}")
                            logger.error(f"数据检索错误：{retrieve_data['error']}")
                            
                            # 显示有用的建议
                            if "attempted_symbols" in retrieve_data:
                                st.warning(f"获取失败的代码：{', '.join(retrieve_data['attempted_symbols'])}")
                            if "suggestion" in retrieve_data:
                                st.info(f"💡 {retrieve_data['suggestion']}")
                            
                            # 显示有效符号示例
                            st.markdown("### 有效股票代码示例：")
                            st.markdown("""
                            - **美国科技股：** AAPL, MSFT, GOOGL, AMZN, TSLA, NVDA
                            - **金融：** JPM, BAC, V, MA, GS
                            - **亚洲：** TSM, 005930.KS, 0700.HK, RELIANCE.NS
                            - **加密货币：** BTC-USD, ETH-USD, SOL-USD
                            - **ETF：** SPY, QQQ, VOO
                            """)
                        else:
                            # 如果我们选择了符号，请确保它们位于数据中
                            if selected_symbols:
                                retrieve_data["symbols"] = selected_symbols
                            
                            # 显示分析的股票
                            symbols = retrieve_data.get("symbols", [])
                            if symbols:
                                st.info(f"📊 正在分析股票：{', '.join(symbols)}")
                            
                            # 检查我们是否有真实的市场数据
                            market_data_available = bool(retrieve_data.get("market_data", {}))
                            context_available = bool(retrieve_data.get("context", []))
                            
                            if market_data_available:
                                st.success(f"✅ 已加载实时市场数据，涉及 {len(retrieve_data.get('market_data', {}))} 只股票")
                            
                            # 显示一些检索到的数据以供验证
                            with st.expander("📈 查看检索数据"):
                                st.write("**问题：**", retrieve_data.get("query"))
                                st.write("**涵盖市场：**", list(retrieve_data.get("market_data", {}).keys()))
                                st.write("**上下文来源数：**", len(retrieve_data.get("context", [])))
                                
                                # 显示示例上下文
                                contexts = retrieve_data.get("context", [])
                                if contexts:
                                    st.write("**上下文示例：**")
                                    for i, ctx in enumerate(contexts[:2], 1):
                                        # 显示每个上下文的前 200 个字符
                                        ctx_preview = ctx[:200] + "..." if len(ctx) > 200 else ctx
                                        st.text(f"{i}. {ctx_preview}")
                            
                            # 第二步：分析并总结
                            st.info("正在生成市场简报……")
                            analyze_response = requests.post(
                                f"{API_URL}/analyze/analyze", 
                                json={"data": retrieve_data},
                                timeout=60
                            )
                            logger.info(f"分析 response status: {analyze_response.status_code}")
                            
                            if analyze_response.status_code != 200:
                                st.error(f"分析失败，状态码：{analyze_response.status_code}")
                                logger.error(f"Analysis failed: {analyze_response.status_code} - {analyze_response.text}")
                                
                                # 添加详细错误信息
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
                                    logger.error(f"分析错误：{analyze_data['error']}")
                                else:
                                    # 显示市场简报
                                    st.subheader("市场简报：")
                                    st.markdown(analyze_data["summary"])
                                    
                                    # 如果分析 2 只或更多股票，请显示比较
                                    if len(selected_symbols) >= 2:
                                        st.divider()
                                        st.subheader("📊 股票并排比较")
                                        
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
                                    
                                    # ===== 收益和增长趋势可视化部分 =====
                                    st.divider()
                                    st.subheader("📊 年度盈利与增长分析")
                                    
                                    # 获取收益数据并创建预测
                                    earnings_data_dict = {}
                                    growth_data_dict = {}
                                    
                                    try:
                                        with st.spinner("正在生成盈利预测和增长趋势分析……"):
                                            for symbol in selected_symbols:
                                                try:
                                                    # 尝试从后台获取收益数据
                                                    earnings_response = requests.get(
                                                        f"{API_URL}/get_earnings",
                                                        params={"symbol": symbol},
                                                        timeout=15
                                                    )
                                                    
                                                    if earnings_response.status_code == 200:
                                                        earnings_json = earnings_response.json()
                                                        if "earnings" in earnings_json and earnings_json["earnings"]:
                                                            # 转换为数据帧
                                                            earnings_df = pd.DataFrame(earnings_json["earnings"])
                                                            
                                                            # 生成预测
                                                            earnings_with_pred = prediction_agent.predict_earnings(
                                                                earnings_df, symbol, years_to_predict=2
                                                            )
                                                            if earnings_with_pred is not None:
                                                                earnings_data_dict[symbol] = earnings_with_pred
                                                                
                                                                # 获取增长率预测
                                                                growth_with_pred = prediction_agent.predict_growth_rate(
                                                                    earnings_df, symbol, years_to_predict=2
                                                                )
                                                                if growth_with_pred is not None:
                                                                    growth_data_dict[symbol] = growth_with_pred
                                                except Exception as e:
                                                    logger.warning(f"Could not get earnings for {symbol}: {str(e)}")
                                                    continue
                                        
                                        # 如果我们有数据，则显示可视化
                                        if earnings_data_dict:
                                            st.info(f" 已生成预测，涉及 {len(earnings_data_dict)} 只股票")
                                            
                                            # 为不同的可视化类型创建选项卡
                                            tab1, tab2, tab3 = st.tabs([
                                                "📈 盈利趋势",
                                                "📊 增长率",
                                                "🔄 综合分析"
                                            ])
                                            
                                            with tab1:
                                                st.markdown("#### 年度盈利比较（历史与预测）")
                                                st.caption("蓝色线条为历史盈利，橙色虚线为 AI 预测")
                                                
                                                try:
                                                    fig_earnings = graphing_agent.create_yearly_earnings_comparison(
                                                        earnings_data_dict,
                                                        title="年度盈利比较：历史与预测"
                                                    )
                                                    if fig_earnings:
                                                        st.pyplot(fig_earnings)
                                                        
                                                        # 添加解释
                                                        with st.expander("📝 如何阅读此图"):
                                                            st.markdown("""
                                                            - **蓝色线条（圆点）**: 实际历史盈利
                                                            - **橙色虚线（方块）**: AI 预测的未来盈利
                                                            - **竖向间隔**: 历史数据与预测数据的分界点
                                                            
                                                            预测基于历史趋势的多项式回归分析。
                                                            """)
                                                except Exception as e:
                                                    logger.error(f"Error creating earnings chart: {str(e)}")
                                                    st.warning(f"无法生成盈利图表：{str(e)}")
                                            
                                            with tab2:
                                                st.markdown("#### 同比增长趋势（历史与预测）")
                                                st.caption("以 0% 为基准展示增长率")
                                                
                                                try:
                                                    fig_growth = graphing_agent.create_growth_trend_comparison(
                                                        growth_data_dict,
                                                        title="同比增长趋势：历史与预测"
                                                    )
                                                    if fig_growth:
                                                        st.pyplot(fig_growth)
                                                        
                                                        # 添加解释
                                                        with st.expander("📝 如何阅读此图"):
                                                            st.markdown("""
                                                            - **蓝色线条（圆点）**: 历史增长率
                                                            - **橙色虚线（方块）**: 预测增长率
                                                            - **0% 黑色基准线**: 零增长参考线
                                                            
                                                            正值表示盈利增长，负值表示盈利下降。
                                                            """)
                                                except Exception as e:
                                                    logger.error(f"Error creating growth chart: {str(e)}")
                                                    st.warning(f"无法生成增长图表：{str(e)}")
                                            
                                            with tab3:
                                                st.markdown("#### 盈利与增长综合分析")
                                                st.caption("同时展示盈利和增长指标")
                                                
                                                try:
                                                    fig_combined = graphing_agent.create_combined_earnings_and_growth(
                                                        earnings_data_dict,
                                                        growth_data_dict,
                                                        title="综合分析"
                                                    )
                                                    if fig_combined:
                                                        st.pyplot(fig_combined)
                                                        
                                                        # 添加解释
                                                        with st.expander("📝 如何阅读此图"):
                                                            st.markdown("""
                                                            **上方图表：盈利**
                                                            - 展示各期盈利的绝对值
                                                            - 用于评估公司规模及盈利能力
                                                            
                                                            **下方图表：增长趋势**
                                                            - 展示同比变化百分比
                                                            - 用于评估公司的增长势头
                                                            
                                                            两张图均以实线表示历史数据，以虚线表示预测数据。
                                                            """)
                                                except Exception as e:
                                                    logger.error(f"Error creating combined chart: {str(e)}")
                                                    st.warning(f"无法生成综合图表：{str(e)}")
                                            
                                            # 显示对照表
                                            st.divider()
                                            st.markdown("#### 📊 关键指标比较表")
                                            
                                            try:
                                                comparison_table = graphing_agent.create_comparison_table(
                                                    selected_symbols,
                                                    earnings_data_dict,
                                                    growth_data_dict
                                                )
                                                if comparison_table is not None and not comparison_table.empty:
                                                    st.dataframe(comparison_table, use_container_width=True)
                                                    
                                                    # 添加数据下载按钮
                                                    csv = comparison_table.to_csv(index=False)
                                                    st.download_button(
                                                        label="📥 下载比较数据（CSV）",
                                                        data=csv,
                                                        file_name=f"earnings_analysis_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.csv",
                                                        mime="text/csv"
                                                    )
                                            except Exception as e:
                                                logger.error(f"Error creating comparison table: {str(e)}")
                                                st.warning(f"无法生成比较表：{str(e)}")
                                        else:
                                            st.info("💡 所选股票暂无盈利数据，新上市公司或数据不足时可能出现这种情况。")
                                    
                                    except Exception as e:
                                        logger.error(f"Error in earnings analysis section: {str(e)}")
                                        st.warning(f"盈利分析出现问题：{str(e)}")
                                
            except requests.exceptions.ConnectionError:
                st.error(f"FastAPI 服务正在连接 Render；如果等待过久，请尝试在本地运行。")
                logger.error(f"Connection error: Failed to connect to FastAPI server at {API_URL}")
        except Exception as e:
            st.error(f"处理问题失败：{str(e)}")
            logger.error(f"Exception in query processing: {str(e)}")

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
                
            response = requests.post(f"{API_URL}/process_query", files=files, data=data, stream=True)
            logger.info(f"Audio process_query response status: {response.status_code}")
            
            if response.status_code == 200:
                audio_bytes = io.BytesIO(response.content)
                st.audio(audio_bytes, format="audio/mp3")
                st.success("语音问题处理完成！")
            else:
                try:
                    error_msg = response.json().get("error", "未知错误")
                    st.error(f"音频处理错误：{error_msg}")
                    logger.error(f"音频处理错误：{error_msg}")
                except:
                    st.error(f"音频处理失败，状态码：{response.status_code}")
                    logger.error(f"音频处理失败，状态码：{response.status_code}")
        except requests.exceptions.ConnectionError:
            st.error(f"FastAPI 服务正在连接 Render；如果等待过久，请尝试在本地运行。")
            logger.error(f"Connection error: Failed to connect to FastAPI server at {API_URL}")
        except Exception as e:
            st.error(f"处理语音问题失败：{str(e)}")
            logger.error(f"Exception in audio query processing: {str(e)}")

# 添加一个部分来解释应用程序的工作原理
with st.expander("ℹ️ 应用工作原理"):
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

# 添加一个部分来解释如何调试应用程序
with st.expander("🔧 故障排查"):
    st.write("""
    ### 常见问题

    1. **无法连接 FastAPI**：确认后端运行在正确端口，例如：
       `uvicorn orchestrator.orchestrator:app --host 0.0.0.0 --port 8000`
    2. **云端部署无响应**：确认 Streamlit 与 FastAPI 服务都已启动。
    3. **服务器错误（500）**：查看 FastAPI 服务日志。
    4. **JSON 序列化错误**：检查 pandas DataFrame 的转换结果。
    5. **查询结果为空**：检查股票代码，建议直接输入 AAPL 等代码。
    """)