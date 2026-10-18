import os
import logging

import requests

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class LanguageAgent:
    def __init__(self):
        """使用阿里云 Model Studio 初始化语言智能体。
        设置 DASHSCOPE_API_KEY 环境变量以使用 Qwen。
        如果 API 密钥不可用，则返回结构化模板。"""
        self.qwen_api_key = os.getenv("DASHSCOPE_API_KEY")
        self.qwen_model = os.getenv("QWEN_MODEL", "qwen3.7-plus")
        self.qwen_base_url = os.getenv(
            "DASHSCOPE_BASE_URL",
            "https://ws-f14xp0oolria4eps.cn-beijing.maas.aliyuncs.com/compatible-mode/v1",
        ).rstrip("/")
        self.use_qwen = bool(self.qwen_api_key)

        if self.use_qwen:
            logger.info("Qwen API configured successfully")
        else:
            logger.info("DASHSCOPE_API_KEY not found, using structured template")

    def generate_brief(self, context, exposure, earnings):
        """使用 Qwen API 或结构化模板生成市场简报。"""
        try:
            # 如果有的话，首先尝试 Qwen
            if self.use_qwen:
                return self._generate_with_qwen(context, exposure, earnings)
            else:
                # 将结构化模板与真实的雅虎财经数据结合使用
                logger.info("Generating brief with structured template")
                return self._generate_fallback_brief(context, exposure, earnings)
        except Exception as e:
            logger.error(f"Error generating brief: {str(e)}")
            return self._generate_fallback_brief(context, exposure, earnings)
    
    def _generate_with_qwen(self, context, exposure, earnings):
        """通过 DashScope API 使用 Qwen 生成市场简报。"""
        prompt = f"""你是一名专业的金融分析师。请根据以下来自 Yahoo Finance 的实时数据，使用简体中文撰写市场分析报告：

市场背景：
{context}

投资组合风险敞口：
{exposure}

盈利数据：
{earnings}

报告应包含：
1. 核心摘要
2. 当前持仓（列出实际价格和价值）
3. 盈利分析与增长趋势
4. 风险评估
5. 主要洞察与建议

请使用清晰、专业的 Markdown 格式，并引用数据中的具体数字。内容简明且信息充分。"""

        response = requests.post(
            f"{self.qwen_base_url}/chat/completions",
            headers={
                "Authorization": f"Bearer {self.qwen_api_key}",
                "Content-Type": "application/json",
            },
            json={
                "model": self.qwen_model,
                "messages": [{"role": "user", "content": prompt}],
            },
            timeout=45,
        )
        response.raise_for_status()
        content = response.json()["choices"][0]["message"]["content"]

        if content:
            logger.info("Successfully generated brief with Qwen API")
            return content

        logger.warning("Qwen returned an empty response, using fallback")
        return self._generate_fallback_brief(context, exposure, earnings)
    
    def _generate_fallback_brief(self, context, exposure, earnings):
        """使用实际的雅虎财经数据生成专业简报"""
        try:
            import re
            import ast
            from datetime import datetime
            
            # 解析风险敞口数据以提取真实值
            exposure_data = {}
            if isinstance(exposure, dict):
                exposure_data = exposure
            elif isinstance(exposure, str):
                try:
                    exposure_data = ast.literal_eval(exposure)
                except:
                    pass
            
            # 解析盈利数据
            earnings_data = {}
            if isinstance(earnings, dict):
                earnings_data = earnings
            elif isinstance(earnings, str):
                try:
                    earnings_data = ast.literal_eval(earnings)
                except:
                    pass
            
            # 使用实际的雅虎财经数据创建专业简报
            brief = "# 📊 市场分析报告\n"
            brief += f"*生成时间：{datetime.now().strftime('%Y-%m-%d %H:%M')}*\n\n"
            brief += "---\n\n"
            
            # 投资组合概览
            if exposure_data:
                symbols = list(exposure_data.keys())
                brief += f"## 投资组合概览\n\n"
                brief += f"**分析标的：** {', '.join(symbols)}\n\n"
                
                # 投资组合总价值
                total_value = sum([exp.get('value', 0) for exp in exposure_data.values()])
                brief += f"### 投资组合总价值： **${total_value:,.2f}**\n\n"
                
                # 展示基于 Yahoo Finance 数据的各项持仓
                brief += "## 持仓详情\n\n"
                for symbol, exp in exposure_data.items():
                    weight = exp.get('weight', 0) * 100
                    value = exp.get('value', 0)
                    price = exp.get('price', 0)
                    
                    brief += f"### 📈 {symbol}\n\n"
                    brief += f"| 指标 | 数值 |\n"
                    brief += f"|--------|-------|\n"
                    brief += f"| **当前价格** | ${price:.2f} |\n"
                    brief += f"| **持仓权重** | {weight:.1f}% |\n"
                    brief += f"| **持仓价值** | ${value:,.2f} |\n"
                    
                    # 添加收益分析（如果有）
                    if symbol in earnings_data:
                        earnings_info = earnings_data[symbol]
                        if isinstance(earnings_info, list) and len(earnings_info) > 0:
                            brief += f"\n**盈利表现：**\n\n"
                            
                            # 按年份排序
                            sorted_earnings = sorted(earnings_info, key=lambda x: x.get('Year', 0), reverse=True)
                            
                            # 显示近年
                            for i, period in enumerate(sorted_earnings[:4]):
                                year = period.get('Year', 'N/A')
                                earnings_val = period.get('Earnings', 0)
                                brief += f"- **{year}:** ${earnings_val/1e9:.2f}B\n"
                            
                            # 有多年数据时计算增长率
                            if len(sorted_earnings) >= 2:
                                latest = sorted_earnings[0].get('Earnings', 0)
                                previous = sorted_earnings[1].get('Earnings', 0)
                                if previous > 0:
                                    growth = ((latest - previous) / previous) * 100
                                    brief += f"\n**同比增长率：** {growth:+.1f}%\n"
                    
                    brief += "\n"
                
                # 市场背景
                if context:
                    context_str = str(context)
                    if len(context_str) > 10:  # 包含有效内容
                        brief += "## 市场背景\n\n"
                        # 清理上下文
                        if isinstance(context, list):
                            for ctx in context:
                                brief += f"• {ctx}\n"
                        else:
                            brief += f"{context_str[:500]}\n"
                        brief += "\n"
                
                # 风险评估
                brief += "## 风险评估\n\n"
                if len(symbols) == 1:
                    symbol = symbols[0]
                    weight_val = list(exposure_data.values())[0].get('weight', 0)*100
                    brief += f"⚠️ **集中度风险：** 投资组合集中于 {symbol} "
                    brief += f"，配置比例为 {weight_val:.1f}%。\n\n"
                    brief += "**建议：** 考虑分散投资以降低单只股票的风险。"
                    brief += "多元化投资组合通常将单项持仓控制在 5% 至 10%。\n"
                else:
                    brief += f"✅ **分散程度：** 投资组合覆盖 {len(symbols)} 项持仓。\n\n"
                    brief += "**配置比例：**\n"
                    for symbol, exp in exposure_data.items():
                        weight = exp.get('weight', 0) * 100
                        brief += f"- {symbol}: {weight:.1f}%\n"
                
                brief += "\n---\n\n"
                brief += "*数据来源：Yahoo Finance（实时）*\n"
                brief += "*提示：历史表现不代表未来结果；以上内容仅供参考。*"
                
            else:
                brief += "⚠️ **暂无投资组合数据**\n\n"
                brief += "请确认问题中填写了正确的股票代码。"
            
            logger.info("Generated professional brief with real Yahoo Finance data")
            return brief
            
        except Exception as e:
            logger.error(f"Error generating fallback brief: {str(e)}")
            return f"生成市场简报时出错：{str(e)}\n\n请使用具体股票代码重试。"
