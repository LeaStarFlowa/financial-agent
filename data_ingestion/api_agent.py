import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
import logging
import json

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class APIAgent:
    def __init__(self):
        self.cache = {}

    def get_market_data(self, symbols, start_date=None, end_date=None):
        """通过适当的错误处理和日期解析从雅虎财经获取市场数据。
        
        参数：
            符号：要获取的股票符号列表
            start_date：开始日期（YYYY-MM-DD 格式或 None 表示 30 天前）
            end_date：结束日期（YYYY-MM-DD 格式或今天无）
            
        返回：
            带有符号键和 DataFrame 值的字典，如果全部失败则为空字典"""
        try:
            # 正确解析日期
            if not end_date:
                end_date = datetime.now().strftime('%Y-%m-%d')
            if not start_date:
                start_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')

            logger.info(f"Fetching market data for {symbols} from {start_date} to {end_date}")
            
            data = {}
            failed_symbols = []
            
            for symbol in symbols:
                try:
                    if symbol not in self.cache:
                        logger.info(f"Fetching data for {symbol}...")
                        ticker = yf.Ticker(symbol)
                        hist = ticker.history(start=start_date, end=end_date)
                        
                        if hist.empty:
                            logger.warning(f"No data returned for {symbol}")
                            failed_symbols.append(symbol)
                            continue
                        
                        # 重置索引以使日期成为一列，以便于序列化
                        hist = hist.reset_index()
                        hist['Date'] = hist['Date'].astype(str)
                        self.cache[symbol] = hist
                        logger.info(f"Successfully cached {symbol}: {len(hist)} rows")
                    
                    data[symbol] = self.cache[symbol]
                    
                except Exception as e:
                    logger.error(f"Error fetching data for {symbol}: {str(e)}")
                    failed_symbols.append(symbol)
                    continue
            
            if failed_symbols:
                logger.warning(f"Failed to fetch data for: {failed_symbols}")
            
            if not data:
                logger.error(f"Failed to fetch data for any symbols: {symbols}")
                return {}
            
            logger.info(f"Successfully fetched market data for {list(data.keys())}")
            return data
            
        except Exception as e:
            logger.error(f"Error in get_market_data: {str(e)}", exc_info=True)
            return {}

    def get_earnings(self, symbol):
        """使用损益表获取给定代码的收益数据。
        
        参数：
            代码： 股票代码
            
        返回：
            收益数据框，如果失败则无"""
        try:
            logger.info(f"Fetching earnings/income statement for {symbol}...")
            ticker = yf.Ticker(symbol)
            
            # 尝试获取损益表（新API）
            try:
                income_stmt = ticker.income_stmt
                if income_stmt is not None and not income_stmt.empty:
                    # 提取净利润行（如果有）
                    if 'Net Income' in income_stmt.index:
                        net_income = income_stmt.loc['Net Income']
                        # 转换为包含“年份”和“收入”列的 DataFrame
                        earnings_df = pd.DataFrame({
                            'Year': net_income.index.year if hasattr(net_income.index, 'year') else range(len(net_income)),
                            'Earnings': net_income.values
                        })
                        logger.info(f"Successfully fetched income statement for {symbol}")
                        return earnings_df
            except Exception as e:
                logger.warning(f"Could not fetch income_stmt for {symbol}: {str(e)}")
            
            # 尝试将财务作为备用
            try:
                financials = ticker.financials
                if financials is not None and not financials.empty:
                    if 'Net Income' in financials.index:
                        net_income = financials.loc['Net Income']
                        earnings_df = pd.DataFrame({
                            'Year': net_income.index.year if hasattr(net_income.index, 'year') else range(len(net_income)),
                            'Earnings': net_income.values
                        })
                        logger.info(f"Successfully fetched financials for {symbol}")
                        return earnings_df
            except Exception as e:
                logger.warning(f"Could not fetch financials for {symbol}: {str(e)}")
            
            logger.warning(f"No earnings/financial data found for {symbol}")
            return None
            
        except Exception as e:
            logger.error(f"Error fetching earnings for {symbol}: {str(e)}")
            return None
    
    def serialize_market_data(self, data):
        """将市场数据 DataFrame 转换为 JSON 可序列化格式。
        
        参数：
            data：带有符号键和 DataFrame 值的字典
            
        返回：
            具有符号键和可序列化数据的字典"""
        try:
            serialized = {}
            for symbol, df in data.items():
                if isinstance(df, pd.DataFrame):
                    # 转换为记录格式
                    records = df.to_dict(orient='records')
                    # 确保所有值都是 JSON 可序列化的
                    serialized_records = []
                    for record in records:
                        serialized_record = {}
                        for key, value in record.items():
                            if pd.isna(value):
                                serialized_record[key] = None
                            elif isinstance(value, (int, float, str, bool, type(None))):
                                serialized_record[key] = value
                            else:
                                # 将其他类型转换为字符串
                                serialized_record[key] = str(value)
                        serialized_records.append(serialized_record)
                    serialized[symbol] = serialized_records
                else:
                    serialized[symbol] = str(df)
            
            return serialized
        except Exception as e:
            logger.error(f"Error serializing market data: {str(e)}", exc_info=True)
            return {}