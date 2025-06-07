# Code Snippets from toollama/API/api-tools/tools/finance/analyzer.py

File: `toollama/API/api-tools/tools/finance/analyzer.py`  
Language: Python  
Extracted: 2025-06-07 05:19:38  

## Snippet 1
Lines 1-5

```Python
from typing import Dict, Any, Optional
import aiohttp
import json
from ...base import BaseTool
```

## Snippet 2
Lines 9-15

```Python
def __init__(self):
        super().__init__()
        self.base_urls = {
            'stock': 'https://query1.finance.yahoo.com/v8/finance/chart/',
            'crypto': 'https://api.coingecko.com/api/v3/simple/price'
        }
```

## Snippet 3
Lines 16-30

```Python
async def analyze_stock(self, symbol: str) -> Dict[str, Any]:
        """
        Analyze a stock symbol using Yahoo Finance data.

        Args:
            symbol (str): The stock symbol to analyze

        Returns:
            Dict[str, Any]: Analysis results including price and basic metrics
        """
        url = f"{self.base_urls['stock']}{symbol}"

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
```

## Snippet 4
Lines 31-33

```Python
if response.status != 200:
                        return {
                            'success': False,
```

## Snippet 5
Lines 41-43

```Python
if not result:
                        return {
                            'success': False,
```

## Snippet 6
Lines 47-61

```Python
meta = result.get('meta', {})
                    indicators = result.get('indicators', {})
                    quote = indicators.get('quote', [{}])[0]

                    return {
                        'success': True,
                        'data': {
                            'symbol': symbol,
                            'currency': meta.get('currency'),
                            'exchange': meta.get('exchangeName'),
                            'price': {
                                'current': meta.get('regularMarketPrice'),
                                'previous_close': meta.get('previousClose'),
                                'open': meta.get('chartPreviousClose')
                            },
```

## Snippet 7
Lines 68-74

```Python
except Exception as e:
            self.logger.error(f"Error analyzing stock {symbol}: {str(e)}")
            return {
                'success': False,
                'error': f'Analysis failed: {str(e)}'
            }
```

## Snippet 8
Lines 75-95

```Python
async def analyze_crypto(self, symbol: str) -> Dict[str, Any]:
        """
        Analyze a cryptocurrency using CoinGecko data.

        Args:
            symbol (str): The cryptocurrency symbol to analyze

        Returns:
            Dict[str, Any]: Analysis results including price and market data
        """
        params = {
            'ids': symbol.lower(),
            'vs_currencies': 'usd',
            'include_market_cap': 'true',
            'include_24hr_vol': 'true',
            'include_24hr_change': 'true'
        }

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(self.base_urls['crypto'], params=params) as response:
```

## Snippet 9
Lines 96-98

```Python
if response.status != 200:
                        return {
                            'success': False,
```

## Snippet 10
Lines 105-107

```Python
if not crypto_data:
                        return {
                            'success': False,
```

## Snippet 11
Lines 111-121

```Python
return {
                        'success': True,
                        'data': {
                            'symbol': symbol,
                            'price_usd': crypto_data.get('usd'),
                            'market_cap_usd': crypto_data.get('usd_market_cap'),
                            'volume_24h_usd': crypto_data.get('usd_24h_vol'),
                            'price_change_24h': crypto_data.get('usd_24h_change')
                        }
                    }
```

## Snippet 12
Lines 122-128

```Python
except Exception as e:
            self.logger.error(f"Error analyzing crypto {symbol}: {str(e)}")
            return {
                'success': False,
                'error': f'Analysis failed: {str(e)}'
            }
```

## Snippet 13
Lines 129-142

```Python
async def execute(self, **kwargs) -> Dict[str, Any]:
        """
        Execute the finance analyzer tool.

        Args:
            asset_type (str): Type of asset to analyze ('stock' or 'crypto')
            symbol (str): The asset symbol to analyze

        Returns:
            Dict[str, Any]: Analysis results
        """
        asset_type = kwargs.get('asset_type')
        symbol = kwargs.get('symbol')
```

## Snippet 14
Lines 143-148

```Python
if not asset_type or not symbol:
            return {
                'success': False,
                'error': 'Missing asset_type or symbol'
            }
```

## Snippet 15
Lines 151-158

```Python
elif asset_type.lower() == 'crypto':
            return await self.analyze_crypto(symbol)
        else:
            return {
                'success': False,
                'error': f'Unsupported asset type: {asset_type}'
            }
```

## Snippet 16
Lines 168-180

```Python
def parameters(self) -> Dict[str, Dict[str, Any]]:
        return {
            "asset_type": {
                "type": "string",
                "description": "Type of asset to analyze ('stock' or 'crypto')",
                "required": True
            },
            "symbol": {
                "type": "string",
                "description": "The asset symbol to analyze",
                "required": True
            }
        }
```

