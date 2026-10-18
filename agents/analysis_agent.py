import pandas as pd
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AnalysisAgent:
    def __init__(self):
        self.portfolio = {'TSM': 0.12, '005930.KS': 0.10}  # 示例：台积电、三星

    def analyze_risk_exposure(self, market_data):
        """根据投资组合和市场数据分析风险敞口。
        
        参数：
            market_data：带有符号键和 DataFrame 值的字典
            
        返回：
            包含暴露数据的字典，如果失败则为空字典"""
        try:
            total_aum = 1000000  # 资产管理规模示例
            exposure = {}
            
            logger.info(f"Analyzing risk exposure for portfolio: {list(self.portfolio.keys())}")
            logger.info(f"Market data available for: {list(market_data.keys())}")
            
            for symbol, weight in self.portfolio.items():
                try:
                    if symbol in market_data:
                        market_df = market_data[symbol]
                        
                        # 处理 DataFrame 或其他数据类型
                        if isinstance(market_df, pd.DataFrame):
                            if market_df.empty:
                                logger.warning(f"Empty DataFrame for {symbol}")
                                price = 100.0  # 回退价格
                            else:
                                # 尝试获取最新收盘价
                                if 'Close' in market_df.columns:
                                    price = float(market_df['Close'].iloc[-1])
                                elif 'close' in market_df.columns:
                                    price = float(market_df['close'].iloc[-1])
                                else:
                                    # 使用第一个数字列作为备用
                                    numeric_cols = market_df.select_dtypes(include=['float64', 'int64']).columns
                                    if len(numeric_cols) > 0:
                                        price = float(market_df[numeric_cols[0]].iloc[-1])
                                    else:
                                        logger.warning(f"No numeric columns for {symbol}")
                                        price = 100.0
                        else:
                            logger.warning(f"Unexpected data type for {symbol}: {type(market_df)}")
                            price = 100.0
                        
                        exposure[symbol] = {
                            'weight': weight,
                            'value': weight * total_aum,
                            'price': price
                        }
                        logger.info(f"Exposure for {symbol}: weight={weight:.2%}, price=${price:.2f}")
                    else:
                        logger.warning(f"Symbol {symbol} not in market data")
                        # 还是按默认价格添加
                        exposure[symbol] = {
                            'weight': weight,
                            'value': weight * total_aum,
                            'price': 100.0
                        }
                        
                except Exception as e:
                    logger.error(f"Error processing {symbol}: {str(e)}")
                    exposure[symbol] = {
                        'weight': weight,
                        'value': weight * total_aum,
                        'price': 100.0
                    }
            
            logger.info(f"Risk exposure analysis complete: {len(exposure)} positions")
            return exposure
            
        except Exception as e:
            logger.error(f"Error analyzing risk exposure: {str(e)}", exc_info=True)
            return {}
