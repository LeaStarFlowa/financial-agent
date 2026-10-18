"""雅虎财经综合股票代码数据库
该模块提供对全球市场主要股票的访问"""

# 美国主要证券交易所 - 最受欢迎的股票
US_STOCKS = {
    # FAANG/科技巨头
    "AAPL": "Apple Inc.",
    "MSFT": "Microsoft Corporation",
    "GOOGL": "Alphabet Inc. (Google) - Class A",
    "GOOG": "Alphabet Inc. (Google) - Class C",
    "AMZN": "Amazon.com Inc.",
    "META": "Meta Platforms Inc. (Facebook)",
    "NVDA": "NVIDIA Corporation",
    "TSLA": "Tesla Inc.",
    "NFLX": "Netflix Inc.",
    
    # 其他主要技术
    "ADBE": "Adobe Inc.",
    "CRM": "Salesforce Inc.",
    "ORCL": "Oracle Corporation",
    "CSCO": "Cisco Systems Inc.",
    "INTC": "Intel Corporation",
    "AMD": "Advanced Micro Devices Inc.",
    "QCOM": "QUALCOMM Incorporated",
    "IBM": "International Business Machines",
    "AVGO": "Broadcom Inc.",
    "TXN": "Texas Instruments Incorporated",
    "AMAT": "Applied Materials Inc.",
    "LRCX": "Lam Research Corporation",
    "KLAC": "KLA Corporation",
    "SNPS": "Synopsys Inc.",
    "CDNS": "Cadence Design Systems Inc.",
    "ASML": "ASML Holding N.V.",
    
    # 半导体
    "TSM": "Taiwan Semiconductor Manufacturing",
    "MU": "Micron Technology Inc.",
    "MRVL": "Marvell Technology Inc.",
    "NXPI": "NXP Semiconductors N.V.",
    "ON": "ON Semiconductor Corporation",
    
    # 社交媒体和娱乐
    "DIS": "The Walt Disney Company",
    "CMCSA": "Comcast Corporation",
    "T": "AT&T Inc.",
    "VZ": "Verizon Communications Inc.",
    "TMUS": "T-Mobile US Inc.",
    "SPOT": "Spotify Technology S.A.",
    "RBLX": "Roblox Corporation",
    "SNAP": "Snap Inc.",
    "PINS": "Pinterest Inc.",
    "TWTR": "Twitter Inc.",
    
    # 电子商务与支付
    "PYPL": "PayPal Holdings Inc.",
    "SQ": "Block Inc. (Square)",
    "SHOP": "Shopify Inc.",
    "EBAY": "eBay Inc.",
    "BABA": "Alibaba Group Holding Limited",
    "JD": "JD.com Inc.",
    "PDD": "Pinduoduo Inc.",
    "MELI": "MercadoLibre Inc.",
    
    # 电动汽车及汽车
    "F": "Ford Motor Company",
    "GM": "General Motors Company",
    "RIVN": "Rivian Automotive Inc.",
    "LCID": "Lucid Group Inc.",
    "NIO": "NIO Inc.",
    "LI": "Li Auto Inc.",
    "XPEV": "XPeng Inc.",
    "TM": "Toyota Motor Corporation",
    "HMC": "Honda Motor Co. Ltd.",
    
    # 金融与银行
    "JPM": "JPMorgan Chase & Co.",
    "BAC": "Bank of America Corporation",
    "WFC": "Wells Fargo & Company",
    "C": "Citigroup Inc.",
    "GS": "Goldman Sachs Group Inc.",
    "MS": "Morgan Stanley",
    "BLK": "BlackRock Inc.",
    "SCHW": "Charles Schwab Corporation",
    "AXP": "American Express Company",
    "V": "Visa Inc.",
    "MA": "Mastercard Incorporated",
    "COF": "Capital One Financial Corporation",
    
    # 医疗保健与制药
    "JNJ": "Johnson & Johnson",
    "UNH": "UnitedHealth Group Incorporated",
    "PFE": "Pfizer Inc.",
    "ABBV": "AbbVie Inc.",
    "TMO": "Thermo Fisher Scientific Inc.",
    "ABT": "Abbott Laboratories",
    "MRK": "Merck & Co. Inc.",
    "LLY": "Eli Lilly and Company",
    "AMGN": "Amgen Inc.",
    "GILD": "Gilead Sciences Inc.",
    "BMY": "Bristol-Myers Squibb Company",
    "CVS": "CVS Health Corporation",
    
    # 零售与消费品
    "WMT": "Walmart Inc.",
    "HD": "The Home Depot Inc.",
    "COST": "Costco Wholesale Corporation",
    "TGT": "Target Corporation",
    "LOW": "Lowe's Companies Inc.",
    "NKE": "Nike Inc.",
    "SBUX": "Starbucks Corporation",
    "MCD": "McDonald's Corporation",
    "KO": "The Coca-Cola Company",
    "PEP": "PepsiCo Inc.",
    
    # 活力
    "XOM": "Exxon Mobil Corporation",
    "CVX": "Chevron Corporation",
    "COP": "ConocoPhillips",
    "SLB": "Schlumberger Limited",
    "EOG": "EOG Resources Inc.",
    
    # 工业的
    "BA": "Boeing Company",
    "CAT": "Caterpillar Inc.",
    "GE": "General Electric Company",
    "MMM": "3M Company",
    "HON": "Honeywell International Inc.",
    "UPS": "United Parcel Service Inc.",
    "FDX": "FedEx Corporation",
    
    # 房地产与房地产投资信托基金
    "AMT": "American Tower Corporation",
    "PLD": "Prologis Inc.",
    "CCI": "Crown Castle Inc.",
    "EQIX": "Equinix Inc.",
    "SPG": "Simon Property Group Inc.",
    
    # 云与软件
    "NOW": "ServiceNow Inc.",
    "SNOW": "Snowflake Inc.",
    "DDOG": "Datadog Inc.",
    "CRWD": "CrowdStrike Holdings Inc.",
    "ZS": "Zscaler Inc.",
    "PANW": "Palo Alto Networks Inc.",
    "WDAY": "Workday Inc.",
    "TEAM": "Atlassian Corporation",
    "ZM": "Zoom Video Communications Inc.",
    "DOCU": "DocuSign Inc.",
    
    # 加密货币与金融科技
    "COIN": "Coinbase Global Inc.",
    "HOOD": "Robinhood Markets Inc.",
    "SOFI": "SoFi Technologies Inc.",
    "AFRM": "Affirm Holdings Inc.",
    
    # 生物技术
    "MRNA": "Moderna Inc.",
    "BNTX": "BioNTech SE",
    "REGN": "Regeneron Pharmaceuticals Inc.",
    "VRTX": "Vertex Pharmaceuticals Incorporated",
    "BIIB": "Biogen Inc.",
    "ILMN": "Illumina Inc.",
    
    # 媒体与娱乐
    "WBD": "Warner Bros. Discovery Inc.",
    "PARA": "Paramount Global",
    "NFLX": "Netflix Inc.",
    "ROKU": "Roku Inc.",
    
    # 半导体扩展
    "MPWR": "Monolithic Power Systems Inc.",
    "SWKS": "Skyworks Solutions Inc.",
    "QRVO": "Qorvo Inc.",
    "MKSI": "MKS Instruments Inc.",
    "ENTG": "Entegris Inc.",
    
    # 网络安全
    "FTNT": "Fortinet Inc.",
    "CHKP": "Check Point Software Technologies",
    "OKTA": "Okta Inc.",
    "S": "SentinelOne Inc.",
    
    # 电子商务延伸
    "ETSY": "Etsy Inc.",
    "W": "Wayfair Inc.",
    "CHWY": "Chewy Inc.",
    
    # 旅游与酒店业
    "ABNB": "Airbnb Inc.",
    "BKNG": "Booking Holdings Inc.",
    "EXPE": "Expedia Group Inc.",
    "MAR": "Marriott International Inc.",
    "HLT": "Hilton Worldwide Holdings Inc.",
    "CCL": "Carnival Corporation",
    "RCL": "Royal Caribbean Cruises Ltd.",
    "NCLH": "Norwegian Cruise Line Holdings",
    "DAL": "Delta Air Lines Inc.",
    "UAL": "United Airlines Holdings Inc.",
    "AAL": "American Airlines Group Inc.",
    "LUV": "Southwest Airlines Co.",
    
    # 食品及饮料
    "KHC": "The Kraft Heinz Company",
    "MDLZ": "Mondelez International Inc.",
    "GIS": "General Mills Inc.",
    "K": "Kellogg Company",
    "HSY": "The Hershey Company",
    "TSN": "Tyson Foods Inc.",
    "BUD": "Anheuser-Busch InBev SA/NV",
    "TAP": "Molson Coors Beverage Company",
    "STZ": "Constellation Brands Inc.",
    
    # 汽车扩展
    "STLA": "Stellantis N.V.",
    "MBLY": "Mobileye Global Inc.",
    
    # 医疗保健设备
    "ISRG": "Intuitive Surgical Inc.",
    "SYK": "Stryker Corporation",
    "EW": "Edwards Lifesciences Corporation",
    "BSX": "Boston Scientific Corporation",
    "MDT": "Medtronic plc",
    "DXCM": "DexCom Inc.",
    "PODD": "Insulet Corporation",
    "ZBH": "Zimmer Biomet Holdings Inc.",
    
    # 保险
    "BRK-B": "Berkshire Hathaway Inc.",
    "PGR": "The Progressive Corporation",
    "ALL": "The Allstate Corporation",
    "TRV": "The Travelers Companies Inc.",
    "MET": "MetLife Inc.",
    "PRU": "Prudential Financial Inc.",
    "AFL": "Aflac Incorporated",
    
    # 电信延伸
    "TMUS": "T-Mobile US Inc.",
    "DISH": "DISH Network Corporation",
    
    # 消费品
    "PG": "The Procter & Gamble Company",
    "CL": "Colgate-Palmolive Company",
    "KMB": "Kimberly-Clark Corporation",
    "EL": "The Estée Lauder Companies Inc.",
    "CLX": "The Clorox Company",
    
    # 服饰
    "LULU": "Lululemon Athletica Inc.",
    "UAA": "Under Armour Inc.",
    "CROX": "Crocs Inc.",
    "VFC": "V.F. Corporation",
    "RL": "Ralph Lauren Corporation",
    "TPR": "Tapestry Inc.",
    "CPRI": "Capri Holdings Limited",
    
    # 餐厅
    "YUM": "Yum! Brands Inc.",
    "QSR": "Restaurant Brands International",
    "CMG": "Chipotle Mexican Grill Inc.",
    "DPZ": "Domino's Pizza Inc.",
    "WEN": "The Wendy's Company",
    
    # 赌博
    "EA": "Electronic Arts Inc.",
    "TTWO": "Take-Two Interactive Software",
    "ATVI": "Activision Blizzard Inc.",
    "U": "Unity Software Inc.",
    
    # 乘车共享和出行
    "UBER": "Uber Technologies Inc.",
    "LYFT": "Lyft Inc.",
    
    # 房地产延伸
    "O": "Realty Income Corporation",
    "PSA": "Public Storage",
    "INVH": "Invitation Homes Inc.",
    "AVB": "AvalonBay Communities Inc.",
    "EQR": "Equity Residential",
    "VTR": "Ventas Inc.",
    "WELL": "Welltower Inc.",
    
    # 公用事业
    "NEE": "NextEra Energy Inc.",
    "DUK": "Duke Energy Corporation",
    "SO": "The Southern Company",
    "D": "Dominion Energy Inc.",
    "AEP": "American Electric Power",
    "EXC": "Exelon Corporation",
    "SRE": "Sempra Energy",
    "XEL": "Xcel Energy Inc.",
    
    # 材料
    "LIN": "Linde plc",
    "APD": "Air Products and Chemicals Inc.",
    "ECL": "Ecolab Inc.",
    "DD": "DuPont de Nemours Inc.",
    "DOW": "Dow Inc.",
    "NEM": "Newmont Corporation",
    "FCX": "Freeport-McMoRan Inc.",
    
    # 国防与航空航天
    "LMT": "Lockheed Martin Corporation",
    "RTX": "Raytheon Technologies Corporation",
    "NOC": "Northrop Grumman Corporation",
    "GD": "General Dynamics Corporation",
    "LHX": "L3Harris Technologies Inc.",
    "HII": "Huntington Ingalls Industries",
    
    # 建筑与工程
    "DE": "Deere & Company",
    "EMR": "Emerson Electric Co.",
    "ETN": "Eaton Corporation plc",
    "PH": "Parker-Hannifin Corporation",
    "ROK": "Rockwell Automation Inc.",
    
    # 废物管理
    "WM": "Waste Management Inc.",
    "RSG": "Republic Services Inc.",
    
    # 医疗器械
    "ABT": "Abbott Laboratories",
    "DHR": "Danaher Corporation",
    "A": "Agilent Technologies Inc.",
    "BAX": "Baxter International Inc.",
    
    # 制药扩展
    "NVO": "Novo Nordisk A/S",
    "AZN": "AstraZeneca PLC",
    "SNY": "Sanofi",
    "GSK": "GSK plc",
    "TAK": "Takeda Pharmaceutical Company",
}

# 亚洲市场
ASIAN_STOCKS = {
    # 韩国股票（KS = 韩国证券交易所）
    "005930.KS": "Samsung Electronics Co. Ltd.",
    "000660.KS": "SK Hynix Inc.",
    "035720.KS": "Kakao Corporation",
    "035420.KS": "NAVER Corporation",
    "051910.KS": "LG Chem Ltd.",
    "006400.KS": "Samsung SDI Co. Ltd.",
    "207940.KS": "Samsung Biologics Co. Ltd.",
    "003550.KS": "LG Corp.",
    "068270.KS": "Celltrion Inc.",
    "012330.KS": "Hyundai Mobis Co. Ltd.",
    
    # 日本股票（T = 东京证券交易所）
    "7203.T": "Toyota Motor Corporation",
    "6758.T": "Sony Group Corporation",
    "9984.T": "SoftBank Group Corp.",
    "6861.T": "Keyence Corporation",
    "7974.T": "Nintendo Co. Ltd.",
    "9433.T": "KDDI Corporation",
    "8306.T": "Mitsubishi UFJ Financial Group",
    "6902.T": "Denso Corporation",
    "9432.T": "Nippon Telegraph & Telephone",
    "6501.T": "Hitachi Ltd.",
    
    # 中国股票（HK=香港）
    "0700.HK": "Tencent Holdings Limited",
    "9988.HK": "Alibaba Group Holding Limited",
    "3690.HK": "Meituan",
    "1810.HK": "Xiaomi Corporation",
    "2318.HK": "Ping An Insurance",
    "0941.HK": "China Mobile Limited",
    "1398.HK": "Industrial and Commercial Bank of China",
    "9618.HK": "JD.com Inc.",
    
    # 印度股票（NS = NSE，BO = BSE）
    "RELIANCE.NS": "Reliance Industries Limited",
    "TCS.NS": "Tata Consultancy Services Limited",
    "INFY.NS": "Infosys Limited",
    "HDFCBANK.NS": "HDFC Bank Limited",
    "WIPRO.NS": "Wipro Limited",
    "ITC.NS": "ITC Limited",
    "BHARTIARTL.NS": "Bharti Airtel Limited",
    "ICICIBANK.NS": "ICICI Bank Limited",
    "SBIN.NS": "State Bank of India",
    "HINDUNILVR.NS": "Hindustan Unilever Limited",
    "LT.NS": "Larsen & Toubro Limited",
    "TATAMOTORS.NS": "Tata Motors Limited",
    "TATASTEEL.NS": "Tata Steel Limited",
    "SUNPHARMA.NS": "Sun Pharmaceutical Industries",
    "MARUTI.NS": "Maruti Suzuki India Limited",
    
    # 台股
    "2330.TW": "Taiwan Semiconductor Manufacturing",
    "2317.TW": "Hon Hai Precision Industry (Foxconn)",
    "2454.TW": "MediaTek Inc.",
    
    # 新加坡股票
    "D05.SI": "DBS Group Holdings Ltd",
    "O39.SI": "Oversea-Chinese Banking Corp",
    "U11.SI": "United Overseas Bank Ltd",
}

# 欧洲市场
EUROPEAN_STOCKS = {
    # 英国股票（L = 伦敦证券交易所）
    "BP.L": "BP plc",
    "HSBA.L": "HSBC Holdings plc",
    "SHEL.L": "Shell plc",
    "AZN.L": "AstraZeneca PLC",
    "GSK.L": "GSK plc",
    "ULVR.L": "Unilever PLC",
    "DGE.L": "Diageo plc",
    "RIO.L": "Rio Tinto Group",
    
    # 德国股票 (DE = XETRA)
    "SAP.DE": "SAP SE",
    "VOW3.DE": "Volkswagen AG",
    "SIE.DE": "Siemens AG",
    "ALV.DE": "Allianz SE",
    "BAS.DE": "BASF SE",
    "BAYN.DE": "Bayer AG",
    "BMW.DE": "Bayerische Motoren Werke AG",
    "DAI.DE": "Daimler AG",
    
    # 法国股票（PA = 巴黎）
    "MC.PA": "LVMH Moët Hennessy Louis Vuitton",
    "OR.PA": "L'Oréal S.A.",
    "SAN.PA": "Sanofi",
    "TTE.PA": "TotalEnergies SE",
    "AIR.PA": "Airbus SE",
    
    # 瑞士股票（SW = 瑞士交易所）
    "NESN.SW": "Nestlé S.A.",
    "NOVN.SW": "Novartis AG",
    "ROG.SW": "Roche Holding AG",
    "UHR.SW": "Swatch Group AG",
    "ABBN.SW": "ABB Ltd",
    "UBSG.SW": "UBS Group AG",
    
    # 荷兰
    "ASML.AS": "ASML Holding N.V.",
    "PHIA.AS": "Koninklijke Philips N.V.",
    "HEIA.AS": "Heineken N.V.",
    
    # 西班牙
    "TEF.MC": "Telefónica S.A.",
    "SAN.MC": "Banco Santander S.A.",
    "IBE.MC": "Iberdrola S.A.",
    
    # 意大利
    "RACE.MI": "Ferrari N.V.",
    "ENI.MI": "Eni S.p.A.",
    "ISP.MI": "Intesa Sanpaolo S.p.A.",
    
    # 瑞典
    "VOLV-B.ST": "Volvo AB",
    "ERIC-B.ST": "Telefonaktiebolaget LM Ericsson",
    
    # 丹麦
    "NOVO-B.CO": "Novo Nordisk A/S",
    "MAERSK-B.CO": "A.P. Møller - Mærsk A/S",
}

# 加拿大股票
CANADIAN_STOCKS = {
    "SHOP.TO": "Shopify Inc.",
    "RY.TO": "Royal Bank of Canada",
    "TD.TO": "Toronto-Dominion Bank",
    "ENB.TO": "Enbridge Inc.",
    "CNQ.TO": "Canadian Natural Resources",
    "BMO.TO": "Bank of Montreal",
    "CP.TO": "Canadian Pacific Railway",
    "BNS.TO": "Bank of Nova Scotia",
    "CM.TO": "Canadian Imperial Bank of Commerce",
    "TRP.TO": "TC Energy Corporation",
    "SU.TO": "Suncor Energy Inc.",
    "CNR.TO": "Canadian National Railway",
    "BCE.TO": "BCE Inc.",
    "T.TO": "TELUS Corporation",
    "ABX.TO": "Barrick Gold Corporation",
}

    # 澳洲股票
AUSTRALIAN_STOCKS = {
    "CBA.AX": "Commonwealth Bank of Australia",
    "BHP.AX": "BHP Group Limited",
    "CSL.AX": "CSL Limited",
    "WBC.AX": "Westpac Banking Corporation",
    "NAB.AX": "National Australia Bank Limited",
    "ANZ.AX": "Australia and New Zealand Banking Group",
    "WES.AX": "Wesfarmers Limited",
    "WOW.AX": "Woolworths Group Limited",
    "FMG.AX": "Fortescue Metals Group Limited",
    "MQG.AX": "Macquarie Group Limited",
}# 市场指数和 ETF
INDICES_AND_ETFS = {
    # 美国主要指数
    "^GSPC": "S&P 500",
    "^DJI": "Dow Jones Industrial Average",
    "^IXIC": "NASDAQ Composite",
    "^RUT": "Russell 2000",
    "^VIX": "CBOE Volatility Index",
    
    # 热门ETF
    "SPY": "SPDR S&P 500 ETF Trust",
    "QQQ": "Invesco QQQ Trust",
    "IWM": "iShares Russell 2000 ETF",
    "DIA": "SPDR Dow Jones Industrial Average ETF",
    "VTI": "Vanguard Total Stock Market ETF",
    "VOO": "Vanguard S&P 500 ETF",
    "VEA": "Vanguard FTSE Developed Markets ETF",
    "VWO": "Vanguard FTSE Emerging Markets ETF",
    "AGG": "iShares Core U.S. Aggregate Bond ETF",
    "BND": "Vanguard Total Bond Market ETF",
    "GLD": "SPDR Gold Shares",
    "SLV": "iShares Silver Trust",
    "USO": "United States Oil Fund",
    "TLT": "iShares 20+ Year Treasury Bond ETF",
    "HYG": "iShares iBoxx $ High Yield Corporate Bond ETF",
    "LQD": "iShares iBoxx $ Investment Grade Corporate Bond ETF",
    "EEM": "iShares MSCI Emerging Markets ETF",
    "EFA": "iShares MSCI EAFE ETF",
    "XLF": "Financial Select Sector SPDR Fund",
    "XLE": "Energy Select Sector SPDR Fund",
    "XLK": "Technology Select Sector SPDR Fund",
    "XLV": "Health Care Select Sector SPDR Fund",
    "XLI": "Industrial Select Sector SPDR Fund",
    "XLP": "Consumer Staples Select Sector SPDR Fund",
    "XLY": "Consumer Discretionary Select Sector SPDR Fund",
    "XLU": "Utilities Select Sector SPDR Fund",
    "XLB": "Materials Select Sector SPDR Fund",
    "XLRE": "Real Estate Select Sector SPDR Fund",
    "XLC": "Communication Services Select Sector SPDR Fund",
    "ARKK": "ARK Innovation ETF",
    "ARKG": "ARK Genomic Revolution ETF",
    "ARKW": "ARK Next Generation Internet ETF",
    "ARKF": "ARK Fintech Innovation ETF",
    "ARKG": "ARK Genomic Revolution ETF",
    
    # 国际ETF
    "IEMG": "iShares Core MSCI Emerging Markets ETF",
    "IXUS": "iShares Core MSCI Total International Stock ETF",
    "VXUS": "Vanguard Total International Stock ETF",
    "ACWI": "iShares MSCI ACWI ETF",
    "VT": "Vanguard Total World Stock ETF",
    
    # 债券ETF
    "VCIT": "Vanguard Intermediate-Term Corporate Bond ETF",
    "VCSH": "Vanguard Short-Term Corporate Bond ETF",
    "MUB": "iShares National Muni Bond ETF",
    "BNDX": "Vanguard Total International Bond ETF",
    
    # 商品ETF
    "GDX": "VanEck Gold Miners ETF",
    "GDXJ": "VanEck Junior Gold Miners ETF",
    "PSLV": "Sprott Physical Silver Trust",
    "PPLT": "Aberdeen Standard Physical Platinum Shares ETF",
    "DBC": "Invesco DB Commodity Index Tracking Fund",
    "CORN": "Teucrium Corn Fund",
    "WEAT": "Teucrium Wheat Fund",
    
    # 房地产ETF
    "VNQ": "Vanguard Real Estate ETF",
    "IYR": "iShares U.S. Real Estate ETF",
    "SCHH": "Schwab U.S. REIT ETF",
    
    # 股息ETF
    "VYM": "Vanguard High Dividend Yield ETF",
    "SCHD": "Schwab U.S. Dividend Equity ETF",
    "DGRO": "iShares Core Dividend Growth ETF",
    "DVY": "iShares Select Dividend ETF",
    
    # 成长型ETF
    "VUG": "Vanguard Growth ETF",
    "IVW": "iShares S&P 500 Growth ETF",
    "SCHG": "Schwab U.S. Large-Cap Growth ETF",
    
    # 价值ETF
    "VTV": "Vanguard Value ETF",
    "IVE": "iShares S&P 500 Value ETF",
    "SCHV": "Schwab U.S. Large-Cap Value ETF",
    
    # 小盘ETF
    "IJR": "iShares Core S&P Small-Cap ETF",
    "VB": "Vanguard Small-Cap ETF",
    "SCHA": "Schwab U.S. Small-Cap ETF",
    
    # 中盘ETF
    "IJH": "iShares Core S&P Mid-Cap ETF",
    "VO": "Vanguard Mid-Cap ETF",
    "SCHM": "Schwab U.S. Mid-Cap ETF",
}

# 加密货币（可在雅虎财经上找到）
CRYPTO = {
    "BTC-USD": "Bitcoin USD",
    "ETH-USD": "Ethereum USD",
    "BNB-USD": "Binance Coin USD",
    "XRP-USD": "XRP USD",
    "ADA-USD": "Cardano USD",
    "DOGE-USD": "Dogecoin USD",
    "SOL-USD": "Solana USD",
    "DOT-USD": "Polkadot USD",
    "MATIC-USD": "Polygon USD",
    "AVAX-USD": "Avalanche USD",
    "LINK-USD": "Chainlink USD",
    "UNI-USD": "Uniswap USD",
    "LTC-USD": "Litecoin USD",
    "ATOM-USD": "Cosmos USD",
    "XLM-USD": "Stellar USD",
    "ALGO-USD": "Algorand USD",
    "HBAR-USD": "Hedera USD",
    "APT-USD": "Aptos USD",
    "OP-USD": "Optimism USD",
    "ARB-USD": "Arbitrum USD",
}

# 合并所有股票
ALL_STOCKS = {
    **US_STOCKS,
    **ASIAN_STOCKS,
    **EUROPEAN_STOCKS,
    **CANADIAN_STOCKS,
    **AUSTRALIAN_STOCKS,
    **INDICES_AND_ETFS,
    **CRYPTO,
}

# 有组织显示的类别
CATEGORIES = {
    "🇺🇸 美国科技巨头": ["AAPL", "MSFT", "GOOGL", "AMZN", "META", "NVDA", "TSLA", "NFLX"],
    "💻 半导体": ["TSM", "NVDA", "INTC", "AMD", "QCOM", "MU", "AVGO", "TXN", "ASML", "AMAT", "LRCX"],
    "🚗 电动车与汽车": ["TSLA", "RIVN", "LCID", "NIO", "LI", "XPEV", "F", "GM", "TM", "HMC"],
    "🏦 金融与银行": ["JPM", "BAC", "GS", "MS", "V", "MA", "AXP", "SCHW", "BLK", "C", "WFC"],
    "🏥 医疗与制药": ["JNJ", "UNH", "PFE", "ABBV", "TMO", "LLY", "MRNA", "BNTX", "MRK", "GILD"],
    "🛒 零售与消费": ["WMT", "AMZN", "HD", "COST", "TGT", "NKE", "SBUX", "MCD", "LOW", "TJX"],
    "☁️ 云计算与软件": ["CRM", "NOW", "SNOW", "DDOG", "CRWD", "ZS", "PANW", "WDAY", "ADBE", "ORCL"],
    "✈️ 旅游与酒店": ["ABNB", "BKNG", "MAR", "HLT", "DAL", "UAL", "CCL", "RCL"],
    "🎮 游戏与娱乐": ["RBLX", "EA", "TTWO", "ATVI", "U", "DIS", "NFLX"],
    "🌏 亚洲科技与市场": ["005930.KS", "TSM", "BABA", "0700.HK", "7203.T", "6758.T", "9984.T"],
    "🇮🇳 印度市场": ["RELIANCE.NS", "TCS.NS", "INFY.NS", "HDFCBANK.NS", "ICICIBANK.NS", "WIPRO.NS"],
    "🌍 欧洲市场": ["SAP.DE", "ASML", "NESN.SW", "MC.PA", "AZN.L", "NOVN.SW", "SHEL.L"],
    "📊 美国主要 ETF": ["SPY", "QQQ", "VTI", "VOO", "IWM", "DIA", "VEA", "VWO"],
    "💎 行业 ETF": ["XLF", "XLE", "XLK", "XLV", "XLI", "XLP", "XLY", "XLU"],
    "📈 成长与价值 ETF": ["VUG", "IVW", "VTV", "IVE", "ARKK", "ARKW"],
    "₿ 主要加密货币": ["BTC-USD", "ETH-USD", "BNB-USD", "SOL-USD", "XRP-USD", "ADA-USD"],
    "⚡ 能源与公用事业": ["XOM", "CVX", "COP", "SLB", "NEE", "DUK", "SO"],
    "🏭 工业与国防": ["BA", "CAT", "GE", "HON", "LMT", "RTX", "NOC"],
    "💳 金融科技与支付": ["PYPL", "SQ", "COIN", "HOOD", "SOFI", "AFRM", "V", "MA"],
    "🍔 食品与饮料": ["KO", "PEP", "SBUX", "MCD", "YUM", "CMG", "KHC"],
    "🏠 房地产": ["AMT", "PLD", "CCI", "EQIX", "O", "VNQ"],
    "🛡️ 网络安全": ["CRWD", "PANW", "ZS", "FTNT", "OKTA", "CHKP"],
}

def get_stock_display_name(symbol):
    """获取股票代码的显示名称"""
    if symbol in ALL_STOCKS:
        return f"{symbol} - {ALL_STOCKS[symbol]}"
    return symbol

def search_stocks(query):
    """按代码或名称搜索股票"""
    query = query.lower()
    results = []
    for symbol, name in ALL_STOCKS.items():
        if query in symbol.lower() or query in name.lower():
            results.append((symbol, name))
    return results

def get_category_stocks(category):
    """获取指定类别的股票"""
    if category in CATEGORIES:
        return [(symbol, ALL_STOCKS.get(symbol, symbol)) for symbol in CATEGORIES[category]]
    return []
