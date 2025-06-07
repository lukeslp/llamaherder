# Code Snippets from toollama/prompts/api_analyzer.py

File: `toollama/prompts/api_analyzer.py`  
Language: Python  
Extracted: 2025-06-07 05:11:03  

## Snippet 1
Lines 1-18

```Python
#!/usr/bin/env python3
"""
API Key Analyzer
==============

This script analyzes available API keys and matches them with bot categories,
focusing on accessibility features and free/public APIs that can be leveraged.

Author: Luke Steuber
License: MIT
"""

import json
from typing import Dict, List, Optional
from dataclasses import dataclass
from bs4 import BeautifulSoup
import re
```

## Snippet 2
Lines 20-28

```Python
class APIService:
    """Represents an API service"""
    name: str
    key: str
    category: str
    requires_payment: bool
    accessibility_features: List[str]
    documentation_url: Optional[str] = None
```

## Snippet 3
Lines 30-52

```Python
def __init__(self):
        self.services: Dict[str, APIService] = {}
        self.free_apis = {
            "semantic_scholar": "https://api.semanticscholar.org/",
            "arxiv": "https://arxiv.org/help/api/",
            "unpaywall": "https://unpaywall.org/products/api",
            "open_library": "https://openlibrary.org/developers/api",
            "gutendex": "https://gutendex.com/",
            "courtlistener": "https://www.courtlistener.com/api/",
            "federal_election": "https://api.open.fec.gov/",
            "healthcare_gov": "https://www.healthcare.gov/developers/",
            "open_food_facts": "https://world.openfoodfacts.org/data",
            "google_scholar": "https://scholar.google.com/",
            "github": "https://api.github.com/",
            "reddit": "https://www.reddit.com/dev/api/",
            "news_api": "https://newsapi.org/",
            "guardian": "https://open-platform.theguardian.com/",
            "nyt": "https://developer.nytimes.com/apis",
            "wayback_machine": "https://archive.org/help/wayback_api.php",
            "free_dictionary": "https://dictionaryapi.dev/",
            "open_trivia": "https://opentdb.com/api_config.php",
        }
```

## Snippet 4
Lines 53-67

```Python
def categorize_api(self, name: str) -> str:
        """Categorize an API based on its name and known patterns"""
        name_lower = name.lower()

        categories = {
            "accessibility": ["text to speech", "tts", "alt", "aria", "screen reader", "voice", "speech"],
            "research": ["scholar", "research", "academic", "arxiv", "library", "dictionary"],
            "healthcare": ["health", "medical", "clinical", "therapy", "food"],
            "education": ["education", "learning", "teaching", "trivia"],
            "media": ["media", "audio", "video", "image", "news", "guardian", "nyt"],
            "development": ["api", "code", "git", "dev", "github"],
            "analysis": ["analysis", "data", "processing", "stats"],
            "government": ["gov", "federal", "election", "court"],
        }
```

## Snippet 5
Lines 73-75

```Python
def analyze_accessibility_features(self, name: str, description: str = "") -> List[str]:
        """Analyze potential accessibility features of an API"""
        features = []
```

## Snippet 6
Lines 86-90

```Python
if any(term in text for term in ["translate", "language"]):
            features.append("translation")

        return features
```

## Snippet 7
Lines 93-97

```Python
for item in api_data:
            service_name = item.get("service", "")
            api_key = item.get("key", "")

            # Skip empty entries
```

## Snippet 8
Lines 98-113

```Python
if not service_name or not api_key:
                continue

            category = self.categorize_api(service_name)
            requires_payment = service_name.lower() not in self.free_apis
            accessibility_features = self.analyze_accessibility_features(service_name)

            self.services[service_name] = APIService(
                name=service_name,
                key=api_key,
                category=category,
                requires_payment=requires_payment,
                accessibility_features=accessibility_features,
                documentation_url=self.free_apis.get(service_name.lower())
            )
```

## Snippet 9
Lines 114-119

```Python
def generate_report(self) -> str:
        """Generate a markdown report of API analysis"""
        report = ["# API Services Analysis\n\n"]

        # Group by category
        categories: Dict[str, List[APIService]] = {}
```

## Snippet 10
Lines 121-124

```Python
if service.category not in categories:
                categories[service.category] = []
            categories[service.category].append(service)
```

## Snippet 11
Lines 164-167

```Python
report.append("   - Archive.org for historical content\n\n")

        return "\n".join(report)
```

## Snippet 12
Lines 168-174

```Python
def extract_api_data_from_html(html_content: str) -> List[Dict[str, str]]:
    """Extract API data from HTML content"""
    soup = BeautifulSoup(html_content, 'html.parser')
    api_data = []

    # Find the table with API keys
    table = soup.find('table', class_='simple-table')
```

## Snippet 13
Lines 180-183

```Python
if len(cells) >= 2:
            service_name = cells[0].get_text(strip=True)
            api_key = cells[1].get_text(strip=True)
```

## Snippet 14
Lines 184-189

```Python
if service_name and api_key:
                api_data.append({
                    "service": service_name,
                    "key": api_key
                })
```

## Snippet 15
Lines 192-195

```Python
def main():
    # This is the HTML content from the Notion export
    html_content = """
    <html><head><meta http-equiv="Content-Type" content="text/html; charset=utf-8"/><title>API Keys and Codes</title><style>
```

## Snippet 16
Lines 196-211

```Python
/* ... [HTML content from your message] ... */
    </style></head><body><article id="60606a0c-1620-4eeb-93e0-a9d425280b90" class="page sans"><header><div class="page-header-icon undefined"><span class="icon">🔑</span></div><h1 class="page-title">API Keys and Codes</h1><p class="page-description"></p><table class="properties"><tbody></tbody></table></header><div class="page-body"><table id="28bbb7e2-ec5f-420d-85c0-099f0b429a5b" class="simple-table"><tbody>
    """

    # Extract API data from HTML
    api_data = extract_api_data_from_html(html_content)

    # Analyze APIs
    analyzer = APIAnalyzer()
    analyzer.analyze_api_keys(api_data)

    # Generate and save report
    report = analyzer.generate_report()
    with open("api_analysis.md", 'w', encoding='utf-8') as f:
        f.write(report)
```

