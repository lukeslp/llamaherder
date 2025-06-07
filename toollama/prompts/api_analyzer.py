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

@dataclass
class APIService:
    """Represents an API service"""
    name: str
    key: str
    category: str
    requires_payment: bool
    accessibility_features: List[str]
    documentation_url: Optional[str] = None

class APIAnalyzer:
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
        
        for category, keywords in categories.items():
            if any(keyword in name_lower for keyword in keywords):
                return category
        return "other"

    def analyze_accessibility_features(self, name: str, description: str = "") -> List[str]:
        """Analyze potential accessibility features of an API"""
        features = []
        text = f"{name} {description}".lower()
        
        if any(term in text for term in ["speech", "tts", "voice"]):
            features.append("text_to_speech")
        if any(term in text for term in ["alt", "image", "description"]):
            features.append("alt_text")
        if any(term in text for term in ["aria", "semantic"]):
            features.append("semantic_markup")
        if "audio" in text:
            features.append("audio_processing")
        if any(term in text for term in ["translate", "language"]):
            features.append("translation")
            
        return features

    def analyze_api_keys(self, api_data: List[Dict[str, str]]) -> None:
        """Analyze API keys from structured data"""
        for item in api_data:
            service_name = item.get("service", "")
            api_key = item.get("key", "")
            
            # Skip empty entries
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

    def generate_report(self) -> str:
        """Generate a markdown report of API analysis"""
        report = ["# API Services Analysis\n\n"]
        
        # Group by category
        categories: Dict[str, List[APIService]] = {}
        for service in self.services.values():
            if service.category not in categories:
                categories[service.category] = []
            categories[service.category].append(service)
        
        # Free APIs section
        report.append("## Free/Public APIs Available\n")
        for service in self.services.values():
            if not service.requires_payment:
                report.append(f"### {service.name}\n")
                if service.documentation_url:
                    report.append(f"Documentation: {service.documentation_url}\n")
                if service.accessibility_features:
                    report.append("Accessibility Features:\n")
                    for feature in service.accessibility_features:
                        report.append(f"- {feature.replace('_', ' ').title()}\n")
                report.append("\n")
        
        # Category breakdown
        for category, services in sorted(categories.items()):
            report.append(f"## {category.title()}\n")
            for service in sorted(services, key=lambda x: x.name):
                report.append(f"### {service.name}\n")
                report.append(f"Payment Required: {'Yes' if service.requires_payment else 'No'}\n")
                if service.accessibility_features:
                    report.append("Accessibility Features:\n")
                    for feature in service.accessibility_features:
                        report.append(f"- {feature.replace('_', ' ').title()}\n")
                report.append("\n")
        
        # Add recommendations
        report.append("## Recommendations\n\n")
        report.append("### High-Priority Free APIs for Accessibility:\n")
        report.append("1. Text-to-Speech Services:\n")
        report.append("   - Leverage available TTS APIs for audio output\n")
        report.append("   - Implement fallback options for different languages\n\n")
        report.append("2. Content Analysis:\n")
        report.append("   - Use Semantic Scholar for academic content\n")
        report.append("   - Implement Open Library for text content\n\n")
        report.append("3. Government Data:\n")
        report.append("   - Healthcare.gov API for health information\n")
        report.append("   - Federal Election Commission API for civic data\n\n")
        report.append("4. Media Processing:\n")
        report.append("   - Guardian and NYT APIs for news content\n")
        report.append("   - Archive.org for historical content\n\n")
        
        return "\n".join(report)

def extract_api_data_from_html(html_content: str) -> List[Dict[str, str]]:
    """Extract API data from HTML content"""
    soup = BeautifulSoup(html_content, 'html.parser')
    api_data = []
    
    # Find the table with API keys
    table = soup.find('table', class_='simple-table')
    if not table:
        return api_data
    
    for row in table.find_all('tr')[1:]:  # Skip header row
        cells = row.find_all('td')
        if len(cells) >= 2:
            service_name = cells[0].get_text(strip=True)
            api_key = cells[1].get_text(strip=True)
            
            if service_name and api_key:
                api_data.append({
                    "service": service_name,
                    "key": api_key
                })
    
    return api_data

def main():
    # This is the HTML content from the Notion export
    html_content = """
    <html><head><meta http-equiv="Content-Type" content="text/html; charset=utf-8"/><title>API Keys and Codes</title><style>
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
    
    print("API analysis complete. Check api_analysis.md for results.")

if __name__ == "__main__":
    main() 