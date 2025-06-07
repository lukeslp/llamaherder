# Code Snippets from toollama/soon/tools_pending/unprocessed/dev_eyahoo_finance.py

File: `toollama/soon/tools_pending/unprocessed/dev_eyahoo_finance.py`  
Language: Python  
Extracted: 2025-06-07 05:15:48  

## Snippet 1
Lines 1-22

```Python
"""
title: Yahoo Finance Stock and Crypto Analyzer with Historical Data
description: A comprehensive stock and cryptocurrency analysis tool using Yahoo Finance data, including historical price analysis and AI news sentiment.
author: AI Assistant
author_url: https://github.com/johnongit
funding_url: https://github.com/open-webui
version: 0.4.0
license: MIT
requirements: yfinance, pandas, numpy, aiohttp, asyncio, transformers
"""

import yfinance as yf
import pandas as pd
import numpy as np
import aiohttp
import asyncio
from transformers import pipeline
from pydantic import BaseModel
from typing import Dict, Any, List, Union, Callable, Awaitable
from functools import lru_cache

# Helper functions
```

## Snippet 2
Lines 30-34

```Python
async def _async_sentiment_analysis(
    content: str, model
) -> Dict[str, Union[str, float]]:
    result = model(content)[0]
    return {"sentiment": result["label"], "confidence": result["score"]}
```

## Snippet 3
Lines 40-43

```Python
def _get_asset_info(ticker: str) -> Dict[str, Any]:
    asset = yf.Ticker(ticker)
    info = asset.info
```

## Snippet 4
Lines 44-68

```Python
if info.get("quoteType") == "CRYPTOCURRENCY":
        return {
            "name": info.get("name", "N/A"),
            "symbol": info.get("symbol", "N/A"),
            "market_cap": info.get("marketCap", 0),
            "circulating_supply": info.get("circulatingSupply", 0),
            "max_supply": info.get("maxSupply", 0),
            "24h_volume": info.get("volume24Hr", 0),
            "7d_change": info.get("sevenDayAvgChangePercent", 0),
            "is_crypto": True,
        }
    else:
        return {
            "name": info.get("longName", "N/A"),
            "symbol": info.get("symbol", "N/A"),
            "sector": info.get("sector", "N/A"),
            "industry": info.get("industry", "N/A"),
            "market_cap": info.get("marketCap", 0),
            "pe_ratio": info.get("trailingPE", 0),
            "dividend_yield": info.get("dividendYield", 0),
            "beta": info.get("beta", 0),
            "52_week_high": info.get("fiftyTwoWeekHigh", 0),
            "52_week_low": info.get("fiftyTwoWeekLow", 0),
            "is_crypto": False,
        }
```

## Snippet 5
Lines 71-80

```Python
def _get_current_price(ticker: str) -> Dict[str, float]:
    asset = yf.Ticker(ticker)
    data = asset.history(period="1d")
    return {
        "current_price": data["Close"].iloc[-1],
        "open": data["Open"].iloc[-1],
        "high": data["High"].iloc[-1],
        "low": data["Low"].iloc[-1],
        "volume": data["Volume"].iloc[-1],
    }
```

## Snippet 6
Lines 83-87

```Python
def _get_asset_news(ticker: str) -> List[Dict[str, Any]]:
    asset = yf.Ticker(ticker)
    news = asset.news

    formatted_news = []
```

## Snippet 7
Lines 88-98

```Python
for item in news:
        formatted_item = {
            "title": item["title"],
            "publisher": item["publisher"],
            "link": item["link"],
            "published_time": item["providerPublishTime"],
            "summary": item.get("summary", "No summary available."),
        }
        formatted_news.append(formatted_item)

    return formatted_news
```

## Snippet 8
Lines 101-104

```Python
def _get_historical_data(ticker: str, period: str = "1y") -> pd.DataFrame:
    asset = yf.Ticker(ticker)
    history = asset.history(period=period)
    return history
```

## Snippet 9
Lines 107-124

```Python
def _analyze_historical_data(df: pd.DataFrame) -> Dict[str, Any]:
    analysis = {}

    # Calculate simple moving averages
    df["SMA50"] = df["Close"].rolling(window=50).mean()
    df["SMA200"] = df["Close"].rolling(window=200).mean()

    # Calculate price change and volatility
    df["Daily_Return"] = df["Close"].pct_change()

    analysis["price_change"] = (df["Close"].iloc[-1] / df["Close"].iloc[0] - 1) * 100
    analysis["volatility"] = (
        df["Daily_Return"].std() * np.sqrt(252) * 100
    )  # Annualized volatility

    # Trend analysis
    current_price = df["Close"].iloc[-1]
    analysis["trend_sma50"] = (
```

## Snippet 10
Lines 129-138

```Python
)

    # Highest and lowest prices
    analysis["highest_price"] = df["High"].max()
    analysis["lowest_price"] = df["Low"].min()

    # Average volume
    analysis["avg_volume"] = df["Volume"].mean()

    return analysis
```

## Snippet 11
Lines 141-149

```Python
async def _async_gather_asset_data(ticker: str) -> Dict[str, Any]:
    asset_info = _get_asset_info(ticker)
    current_price = _get_current_price(ticker)
    news_items = _get_asset_news(ticker)
    historical_data = _get_historical_data(ticker)
    historical_analysis = _analyze_historical_data(historical_data)

    model = _get_sentiment_model()
    sentiment_tasks = [
```

## Snippet 12
Lines 151-162

```Python
]
    sentiments = await asyncio.gather(*sentiment_tasks)

    sentiment_results = [
        {
            "title": news_items[i]["title"],
            "publisher": news_items[i]["publisher"],
            "link": news_items[i]["link"],
            "published_time": news_items[i]["published_time"],
            "sentiment": sentiment["sentiment"],
            "confidence": sentiment["confidence"],
        }
```

## Snippet 13
Lines 164-171

```Python
]

    return {
        "asset_info": asset_info,
        "current_price": current_price,
        "sentiments": sentiment_results,
        "historical_analysis": historical_analysis,
    }
```

## Snippet 14
Lines 174-195

```Python
def _get_rsi_macd(symbol="BTC-USD", period="1mo", interval="1d"):
    ticker = yf.Ticker(symbol)
    data = ticker.history(period=period, interval=interval)
    close_prices = data["Close"]

    # Calculate RSI
    delta = close_prices.diff()
    gain = delta.where(delta > 0, 0)
    loss = -delta.where(delta < 0, 0)
    avg_gain = gain.rolling(window=14).mean()
    avg_loss = loss.rolling(window=14).mean()
    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))

    # Calculate MACD
    ema_12 = close_prices.ewm(span=12, adjust=False).mean()
    ema_26 = close_prices.ewm(span=26, adjust=False).mean()
    macd_line = ema_12 - ema_26
    signal_line = macd_line.ewm(span=9, adjust=False).mean()
    macd_hist = macd_line - signal_line

    # Format output
```

## Snippet 15
Lines 196-210

```Python
output = f"Results for {symbol} over period {period} with interval {interval}:\n\n"
    output += f"Latest RSI: {rsi.iloc[-1]:.2f}\n"
    output += f"Latest MACD: {macd_line.iloc[-1]:.2f}\n"
    output += f"Latest MACD Signal: {signal_line.iloc[-1]:.2f}\n"
    output += f"Latest MACD Histogram: {macd_hist.iloc[-1]:.2f}\n\n"
    output += "RSI Evolution:\n"
    output += f"{rsi.tail(10).to_string(header=False)}\n\n"
    output += "MACD Evolution:\n"
    output_df = pd.DataFrame(
        {"MACD": macd_line, "Signal": signal_line, "Histogram": macd_hist},
        index=macd_line.index,
    )
    output += f"{output_df.tail(10).to_string(index=True)}"

    return output
```

## Snippet 16
Lines 213-219

```Python
def _compile_report(
    data: Dict[str, Any], price_history: pd.DataFrame, tech_data: str
) -> str:
    info = data["asset_info"]
    price = data["current_price"]
    historical = data["historical_analysis"]
```

## Snippet 17
Lines 222-229

```Python
Cryptocurrency Analysis Report for {name} ({symbol})

        Basic Information:
        Market Cap: ${market_cap:,.0f}
        Circulating Supply: {circulating_supply:,.0f}

        Current Trading Information:
        Current Price: ${current_price:.2f}
```

## Snippet 18
Lines 230-261

```Python
24h Range: ${low:.2f} - ${high:.2f}
        24h Volume: {volume:,.0f}

        Historical Analysis:
        Price Change (1 year): {price_change:.2f}%
        Annualized Volatility: {volatility:.2f}%
        50-day SMA Trend: {trend_sma50}
        200-day SMA Trend: {trend_sma200}
        Highest Price (1 year): ${highest_price:.2f}
        Lowest Price (1 year): ${lowest_price:.2f}
        Average Daily Volume: {avg_volume:,.0f}
        Price history: {price_history}
        Technical data: {tech_data}
        """.format(
            name=info["name"],
            symbol=info["symbol"],
            market_cap=info["market_cap"],
            circulating_supply=info["circulating_supply"],
            current_price=price["current_price"],
            low=price["low"],
            high=price["high"],
            volume=price["volume"],
            price_change=historical["price_change"],
            volatility=historical["volatility"],
            trend_sma50=historical["trend_sma50"],
            trend_sma200=historical["trend_sma200"],
            highest_price=historical["highest_price"],
            lowest_price=historical["lowest_price"],
            avg_volume=historical["avg_volume"],
            price_history=price_history.to_string(),
            tech_data=tech_data,
        )
```

## Snippet 19
Lines 264-272

```Python
Stock Analysis Report for {name} ({symbol})

        Basic Information:
        Sector: {sector}
        Industry: {industry}
        Market Cap: ${market_cap:,.0f}

        Current Trading Information:
        Current Price: ${current_price:.2f}
```

## Snippet 20
Lines 273-279

```Python
Day's Range: ${low:.2f} - ${high:.2f}
        Volume: {volume:,.0f}

        Key Financial Metrics:
        P/E Ratio: {pe_ratio}
        Dividend Yield: {dividend_yield:.2%}
        Beta: {beta}
```

## Snippet 21
Lines 280-314

```Python
52 Week Range: ${week_low:.2f} - ${week_high:.2f}

        Historical Analysis:
        Price Change (1 year): {price_change:.2f}%
        Annualized Volatility: {volatility:.2f}%
        50-day SMA Trend: {trend_sma50}
        200-day SMA Trend: {trend_sma200}
        Highest Price (1 year): ${highest_price:.2f}
        Lowest Price (1 year): ${lowest_price:.2f}
        Average Daily Volume: {avg_volume:,.0f}

        """.format(
            name=info["name"],
            symbol=info["symbol"],
            sector=info["sector"],
            industry=info["industry"],
            market_cap=info["market_cap"],
            current_price=price["current_price"],
            low=price["low"],
            high=price["high"],
            volume=price["volume"],
            pe_ratio=info["pe_ratio"],
            dividend_yield=info["dividend_yield"],
            beta=info["beta"],
            week_low=info["52_week_low"],
            week_high=info["52_week_high"],
            price_change=historical["price_change"],
            volatility=historical["volatility"],
            trend_sma50=historical["trend_sma50"],
            trend_sma200=historical["trend_sma200"],
            highest_price=historical["highest_price"],
            lowest_price=historical["lowest_price"],
            avg_volume=historical["avg_volume"],
        )
```

## Snippet 22
Lines 316-321

```Python
for item in data["sentiments"]:
        report += """
        Title: {title}
        Publisher: {publisher}
        Link: {url}
        Published Time: {published_time}
```

## Snippet 23
Lines 322-331

```Python
Sentiment: {sentiment} (Confidence: {confidence:.2f})

        """.format(
            title=item["title"],
            publisher=item["publisher"],
            url=item["link"],
            published_time=item["published_time"],
            sentiment=item["sentiment"],
            confidence=item["confidence"],
        )
```

## Snippet 24
Lines 332-334

```Python
print("report")
    print(report)
    return report
```

## Snippet 25
Lines 344-350

```Python
async def analyze_asset(
        self,
        ticker: str,
        __user__: dict = {},
        __event_emitter__: Callable[[Any], Awaitable[None]] = None,
    ) -> str:
        """
```

## Snippet 26
Lines 353-382

```Python
:param ticker: The asset ticker symbol (e.g., "AAPL" for Apple Inc. or "BTC-USD" for Bitcoin).
        :return: A comprehensive analysis report of the asset as a formatted string.
        """
        await __event_emitter__(
            {
                "type": "status",
                "data": {"description": "Initializing analysis", "done": False},
            }
        )

        await __event_emitter__(
            {
                "type": "status",
                "data": {"description": "Retrieving asset data", "done": False},
            }
        )
        price_history = _get_historical_data(ticker)
        tech_data = _get_rsi_macd(ticker)

        data = await _async_gather_asset_data(ticker)

        await __event_emitter__(
            {
                "type": "status",
                "data": {"description": "Compiling asset report", "done": False},
            }
        )
        report = _compile_report(data, price_history, tech_data)

        last_price = data["current_price"]["current_price"]
```

## Snippet 27
Lines 383-387

```Python
asset_type = "cryptocurrency" if data["asset_info"]["is_crypto"] else "stock"
        await __event_emitter__(
            {
                "type": "status",
                "data": {
```

## Snippet 28
Lines 388-392

```Python
"description": "Finished creating report for {0} - latest price: ${1:.4f}".format(
                        asset_type,
                        last_price,
                    ),
                    "done": True,
```

