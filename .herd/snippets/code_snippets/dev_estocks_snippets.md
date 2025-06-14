# Code Snippets from toollama/soon/tools_pending/unprocessed/dev_estocks.py

File: `toollama/soon/tools_pending/unprocessed/dev_estocks.py`  
Language: Python  
Extracted: 2025-06-07 05:15:40  

## Snippet 1
Lines 1-34

```Python
"""
title: Stock Market Helper
description: A comprehensive stock analysis tool that gathers data from Finnhub API and compiles a detailed report.
author: Pyotr Growpotkin
author_url: https://github.com/christ-offer/
github: https://github.com/christ-offer/open-webui-tools
funding_url: https://github.com/open-webui
version: 0.0.9
license: MIT
requirements: finnhub-python
"""

import finnhub
import requests
import aiohttp
import asyncio
from transformers import pipeline, AutoTokenizer, AutoModelForSequenceClassification
import torch
from bs4 import BeautifulSoup
from pydantic import BaseModel
from datetime import datetime, timedelta
from typing import (
    Dict,
    Any,
    List,
    Union,
    Generator,
    Iterator,
    Tuple,
    Optional,
    Callable,
    Awaitable,
)
from functools import lru_cache
```

## Snippet 2
Lines 44-48

```Python
def _get_sentiment_model():
    model_name = "mrm8488/distilroberta-finetuned-financial-news-sentiment-analysis"
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForSequenceClassification.from_pretrained(model_name)
    return tokenizer, model
```

## Snippet 3
Lines 51-59

```Python
def _get_basic_info(client: finnhub.Client, ticker: str) -> Dict[str, Any]:
    """
    Fetch comprehensive company information from Finnhub API.
    """
    profile = client.company_profile2(symbol=ticker)
    basic_financials = client.company_basic_financials(ticker, "all")
    peers = client.company_peers(ticker)

    return {"profile": profile, "basic_financials": basic_financials, "peers": peers}
```

## Snippet 4
Lines 62-75

```Python
def _get_current_price(client: finnhub.Client, ticker: str) -> Dict[str, float]:
    """
    Fetch current price and daily change from Finnhub API.
    """
    quote = client.quote(ticker)
    return {
        "current_price": quote["c"],
        "change": quote["dp"],
        "change_amount": quote["d"],
        "high": quote["h"],
        "low": quote["l"],
        "open": quote["o"],
        "previous_close": quote["pc"],
    }
```

## Snippet 5
Lines 78-88

```Python
def _get_company_news(client: finnhub.Client, ticker: str) -> List[Dict[str, str]]:
    """
    Fetch recent news articles about the company from Finnhub API.
    Returns a list of dictionaries containing news item details.
    """
    end_date = datetime.now()
    start_date = end_date - timedelta(days=7)
    news = client.company_news(ticker, _format_date(start_date), _format_date(end_date))

    news_items = news[:10]  # Get the first 10 news items
```

## Snippet 6
Lines 92-95

```Python
async def _async_web_scrape(session: aiohttp.ClientSession, url: str) -> str:
    """
    Scrape and process a web page using r.jina.ai
```

## Snippet 7
Lines 96-114

```Python
:param session: The aiohttp ClientSession to use for the request.
    :param url: The URL of the web page to scrape.
    :return: The scraped and processed content without the Links/Buttons section, or an error message.
    """
    jina_url = f"https://r.jina.ai/{url}"

    headers = {
        "X-No-Cache": "true",
        "X-With-Images-Summary": "true",
        "X-With-Links-Summary": "true",
    }

    try:
        async with session.get(jina_url, headers=headers) as response:
            response.raise_for_status()
            content = await response.text()

        # Extract content and remove Links/Buttons section as its too many tokens
        links_section_start = content.rfind("Images:")
```

## Snippet 8
Lines 115-119

```Python
if links_section_start != -1:
            content = content[:links_section_start].strip()

        return content
```

## Snippet 9
Lines 125-142

```Python
async def _async_sentiment_analysis(content: str) -> Dict[str, Union[str, float]]:
    tokenizer, model = _get_sentiment_model()

    inputs = tokenizer(content, return_tensors="pt", truncation=True, max_length=512)

    with torch.no_grad():
        outputs = model(**inputs)

    probabilities = torch.nn.functional.softmax(outputs.logits, dim=-1)
    sentiment_scores = probabilities.tolist()[0]

    # Update sentiment labels to match the new model's output
    sentiments = ["Neutral", "Positive", "Negative"]
    sentiment = sentiments[sentiment_scores.index(max(sentiment_scores))]

    confidence = max(sentiment_scores)

    return {"sentiment": sentiment, "confidence": confidence}
```

## Snippet 10
Lines 146-153

```Python
async def _async_gather_stock_data(
    client: finnhub.Client, ticker: str
) -> Dict[str, Any]:
    basic_info = _get_basic_info(client, ticker)
    current_price = _get_current_price(client, ticker)
    news_items = _get_company_news(client, ticker)

    async with aiohttp.ClientSession() as session:
```

## Snippet 11
Lines 159-165

```Python
]
    sentiments = await asyncio.gather(*sentiment_tasks)

    sentiment_results = [
        {
            "url": news_items[i]["url"],
            "title": news_items[i]["title"],
```

## Snippet 12
Lines 172-178

```Python
]

    return {
        "basic_info": basic_info,
        "current_price": current_price,
        "sentiments": sentiment_results,
    }
```

## Snippet 13
Lines 181-191

```Python
def _compile_report(data: Dict[str, Any]) -> str:
    """
    Compile gathered data into a comprehensive structured report.
    """
    profile = data["basic_info"]["profile"]
    financials = data["basic_info"]["basic_financials"]
    metrics = financials["metric"]
    peers = data["basic_info"]["peers"]
    price_data = data["current_price"]

    report = f"""
```

## Snippet 14
Lines 192-195

```Python
Comprehensive Stock Analysis Report for {profile['name']} ({profile['ticker']})

    Basic Information:
    Industry: {profile.get('finnhubIndustry', 'N/A')}
```

## Snippet 15
Lines 197-204

```Python
Share Outstanding: {profile.get('shareOutstanding', 'N/A'):,.0f} M
    Country: {profile.get('country', 'N/A')}
    Exchange: {profile.get('exchange', 'N/A')}
    IPO Date: {profile.get('ipo', 'N/A')}

    Current Trading Information:
    Current Price: ${price_data['current_price']:.2f}
    Daily Change: {price_data['change']:.2f}% (${price_data['change_amount']:.2f})
```

## Snippet 16
Lines 205-224

```Python
Day's Range: ${price_data['low']:.2f} - ${price_data['high']:.2f}
    Open: ${price_data['open']:.2f}
    Previous Close: ${price_data['previous_close']:.2f}

    Key Financial Metrics:
    52 Week High: ${financials['metric'].get('52WeekHigh', 'N/A')}
    52 Week Low: ${financials['metric'].get('52WeekLow', 'N/A')}
    P/E Ratio: {financials['metric'].get('peBasicExclExtraTTM', 'N/A')}
    EPS (TTM): ${financials['metric'].get('epsBasicExclExtraItemsTTM', 'N/A')}
    Return on Equity: {financials['metric'].get('roeRfy', 'N/A')}%
    Debt to Equity: {financials['metric'].get('totalDebtToEquityQuarterly', 'N/A')}
    Current Ratio: {financials['metric'].get('currentRatioQuarterly', 'N/A')}
    Dividend Yield: {financials['metric'].get('dividendYieldIndicatedAnnual', 'N/A')}%

    Peer Companies: {', '.join(peers[:5])}

    Detailed Financial Analysis:

    1. Valuation Metrics:
    P/E Ratio: {metrics.get('peBasicExclExtraTTM', 'N/A')}
```

## Snippet 17
Lines 228-231

```Python
- Interpretation: {'High' if metrics.get('pbQuarterly', 0) > 3 else 'Moderate' if 1 <= metrics.get('pbQuarterly', 0) <= 3 else 'Low'}

    2. Profitability Metrics:
    Return on Equity: {metrics.get('roeRfy', 'N/A')}%
```

## Snippet 18
Lines 235-238

```Python
- Interpretation: {'Excellent' if metrics.get('netProfitMarginTTM', 0) > 20 else 'Good' if 10 <= metrics.get('netProfitMarginTTM', 0) <= 20 else 'Average' if 5 <= metrics.get('netProfitMarginTTM', 0) < 10 else 'Poor'}

    3. Liquidity and Solvency:
    Current Ratio: {metrics.get('currentRatioQuarterly', 'N/A')}
```

## Snippet 19
Lines 242-245

```Python
- Interpretation: {'Low leverage' if metrics.get('totalDebtToEquityQuarterly', 0) < 0.5 else 'Moderate leverage' if 0.5 <= metrics.get('totalDebtToEquityQuarterly', 0) <= 1 else 'High leverage'}

    4. Dividend Analysis:
    Dividend Yield: {metrics.get('dividendYieldIndicatedAnnual', 'N/A')}%
```

## Snippet 20
Lines 266-270

```Python
Sentiment Analysis: {item['sentiment']} (Confidence: {item['confidence']:.2f})

    """
    # Content Preview: {item['content'][:500]}...
    return report
```

## Snippet 21
Lines 274-277

```Python
class UserValves(BaseModel):
        FINNHUB_API_KEY: str = ""
        pass
```

## Snippet 22
Lines 281-287

```Python
async def compile_stock_report(
        self,
        ticker: str,
        __user__: dict = {},
        __event_emitter__: Callable[[Any], Awaitable[None]] = None,
    ) -> str:
        """
```

## Snippet 23
Lines 290-298

```Python
This function gathers various data points including:
        - Basic company information (industry, market cap, etc.)
        - Current trading information (price, daily change, etc.)
        - Key financial metrics (P/E ratio, EPS, ROE, etc.)
        - List of peer companies
        - Recent news articles with sentiment analysis using FinBERT

        The gathered data is then compiled into a structured, easy-to-read report.
```

## Snippet 24
Lines 299-335

```Python
:param ticker: The stock ticker symbol (e.g., "AAPL" for Apple Inc.).
        :return: A comprehensive analysis report of the stock as a formatted string.
        """
        await __event_emitter__(
            {
                "type": "status",
                "data": {"description": "Initializing client", "done": False},
            }
        )
        self.client = finnhub.Client(api_key=__user__["valves"].FINNHUB_API_KEY)
        await __event_emitter__(
            {
                "type": "status",
                "data": {"description": "Retrieving stock data", "done": False},
            }
        )
        data = await _async_gather_stock_data(self.client, ticker)
        await __event_emitter__(
            {
                "type": "status",
                "data": {"description": "Compiling stock report", "done": False},
            }
        )
        report = _compile_report(data)
        # Get lastest price from data
        last_price = data["current_price"]["current_price"]
        await __event_emitter__(
            {
                "type": "status",
                "data": {
                    "description": "Finished creating report - latest price: "
                    + str(last_price),
                    "done": True,
                },
            }
        )
        return report
```

