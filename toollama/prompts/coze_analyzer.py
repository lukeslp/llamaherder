#!/usr/bin/env python3
"""
Coze History Analyzer
====================

This script analyzes a Coze bot history export file, extracting and organizing:
- Bot prompts
- Tool configurations
- Workflows
- API information

Features:
- Extracts and evaluates prompts for each bot
- Analyzes tool configurations and API integrations
- Generates improved versions of prompts with accessibility considerations
- Creates organized documentation structure

Author: Luke Steuber
License: MIT
"""

import json
import os
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from datetime import datetime
import re

@dataclass
class PromptAnalysis:
    """Represents analysis of a single prompt"""
    original_text: str
    bot_name: str
    bot_description: str
    evaluation: str
    improvements: List[str]
    accessibility_notes: List[str]

@dataclass
class ToolAnalysis:
    """Represents analysis of a tool configuration"""
    tool_name: str
    description: str
    bot_name: str
    configuration: Dict[str, Any]
    api_endpoints: List[str]
    usage_notes: List[str]

@dataclass
class BotCategory:
    """Represents a category of bots"""
    name: str
    description: str
    bots: List[str]
    accessibility_score: int = 0
    accessibility_features: List[str] = None

    def __post_init__(self):
        if self.accessibility_features is None:
            self.accessibility_features = []

class CozeAnalyzer:
    """Main class for analyzing Coze export data"""
    
    def __init__(self, export_path: str):
        """Initialize with path to export file"""
        self.export_path = export_path
        self.output_dir = "coze_analysis"
        self.categories = {
            "accessibility": BotCategory("Accessibility", "Bots focused on accessibility features and support", []),
            "research": BotCategory("Research", "Academic and research assistance bots", []),
            "healthcare": BotCategory("Healthcare", "Medical, clinical, and healthcare-related bots", []),
            "education": BotCategory("Education", "Educational and learning support bots", []),
            "games": BotCategory("Games", "Gaming and entertainment bots", []),
            "productivity": BotCategory("Productivity", "Task management and productivity bots", []),
            "media": BotCategory("Media", "Media handling and processing bots", []),
            "development": BotCategory("Development", "Software development and coding bots", []),
            "analysis": BotCategory("Analysis", "Data analysis and processing bots", []),
            "other": BotCategory("Other", "Uncategorized bots", [])
        }
        self._setup_directories()
        
    def _setup_directories(self) -> None:
        """Create necessary output directories"""
        dirs = [
            self.output_dir,
            f"{self.output_dir}/prompts",
            f"{self.output_dir}/tools",
            f"{self.output_dir}/workflows",
            f"{self.output_dir}/documentation"
        ]
        for dir_path in dirs:
            os.makedirs(dir_path, exist_ok=True)
    
    def _evaluate_prompt(self, prompt: str) -> str:
        """
        Evaluate a prompt's effectiveness
        Returns a detailed analysis string
        """
        issues = []
        
        # Check length
        if len(prompt) < 100:
            issues.append("Prompt may be too brief for complex tasks")
        
        # Check for clear instruction patterns
        if not any(pattern in prompt.lower() for pattern in ["you are", "your role", "your task"]):
            issues.append("Role/purpose could be more explicitly defined")
            
        # Check for accessibility considerations
        if not any(term in prompt.lower() for term in ["accessibility", "accessible", "screen reader", "alt text"]):
            issues.append("Could benefit from explicit accessibility considerations")
            
        # Check for error handling guidance
        if not any(term in prompt.lower() for term in ["if error", "if failed", "exception", "invalid"]):
            issues.append("Error handling guidance could be enhanced")
        
        return "\n".join(issues) if issues else "Prompt appears well-structured"

    def _suggest_improvements(self, prompt: str, evaluation: str) -> List[str]:
        """Generate improvement suggestions based on evaluation"""
        improvements = []
        
        if "too brief" in evaluation:
            improvements.append("Add more detailed task specifications and examples")
        
        if "role" in evaluation:
            improvements.append("Start with a clear role definition: 'You are a specialized assistant that...'")
            
        if "accessibility" in evaluation:
            improvements.append("Add explicit accessibility guidelines and requirements")
            
        if "error handling" in evaluation:
            improvements.append("Include specific error handling instructions and fallback behaviors")
            
        return improvements

    def _extract_api_endpoints(self, tool_config: Dict) -> List[str]:
        """Extract API endpoints from tool configuration"""
        endpoints = []
        
        def recursive_search(obj: Any) -> None:
            if isinstance(obj, dict):
                for key, value in obj.items():
                    if isinstance(key, str) and any(term in key.lower() for term in ["url", "endpoint", "api"]):
                        if isinstance(value, str) and ("http://" in value or "https://" in value):
                            endpoints.append(value)
                    recursive_search(value)
            elif isinstance(obj, list):
                for item in obj:
                    recursive_search(item)
        
        recursive_search(tool_config)
        return endpoints

    def _categorize_bot(self, bot_info: Dict) -> str:
        """Determine the category for a bot based on its description and prompt"""
        name = bot_info.get("name", "").lower()
        description = bot_info.get("description", "").lower()
        prompt = bot_info.get("prompt_info", "").lower()
        
        # Keywords for each category
        category_keywords = {
            "accessibility": ["accessibility", "alt text", "screen reader", "aria", "wcag", "a11y"],
            "research": ["research", "academic", "study", "analysis", "scholar"],
            "healthcare": ["health", "medical", "clinical", "therapy", "slp", "speech", "language"],
            "education": ["education", "learning", "teaching", "curriculum", "iep"],
            "games": ["game", "gaming", "pokemon", "rpg", "dungeon"],
            "productivity": ["productivity", "task", "workflow", "management"],
            "media": ["media", "audio", "video", "image", "speech"],
            "development": ["development", "code", "programming", "api", "plugin"],
            "analysis": ["analysis", "data", "processing", "statistics"]
        }
        
        # Check text against keywords
        text = f"{name} {description} {prompt}"
        for category, keywords in category_keywords.items():
            if any(keyword in text for keyword in keywords):
                return category
                
        return "other"

    def _analyze_accessibility_features(self, bot_info: Dict) -> Dict[str, Any]:
        """Analyze accessibility features of a bot"""
        prompt = bot_info.get("prompt_info", "").lower()
        name = bot_info.get("name", "")
        description = bot_info.get("description", "")
        
        features = []
        score = 0
        
        # Core accessibility features
        accessibility_aspects = {
            "screen_reader": ["screen reader", "screenreader", "tts", "text to speech"],
            "alt_text": ["alt text", "alternative text", "image description"],
            "aria": ["aria", "semantic html", "semantic markup"],
            "keyboard": ["keyboard navigation", "keyboard access"],
            "error_handling": ["error message", "error handling", "fallback"],
            "cognitive": ["clear language", "simple language", "cognitive accessibility"],
            "customization": ["customize", "personalize", "adapt"],
        }
        
        for aspect, keywords in accessibility_aspects.items():
            if any(keyword in prompt for keyword in keywords):
                features.append(aspect)
                score += 1
        
        # Additional accessibility considerations
        if "wcag" in prompt or "web content accessibility" in prompt:
            features.append("wcag_compliance")
            score += 2
            
        if "accessibility testing" in prompt or "accessibility check" in prompt:
            features.append("testing")
            score += 2
            
        return {
            "bot_name": name,
            "score": score,
            "features": features,
            "description": description
        }

    def analyze(self) -> None:
        """Main analysis method"""
        try:
            with open(self.export_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except Exception as e:
            print(f"Error loading export file: {e}")
            return

        # Process each bot
        for bot in data.get("bot_list", []):
            bot_info = bot.get("bot_info", {})
            bot_name = bot_info.get("name", "Unnamed Bot")
            
            # Categorize bot
            category = self._categorize_bot(bot_info)
            self.categories[category].bots.append(bot_name)
            
            # Analyze accessibility features
            if category == "accessibility" or "accessibility" in bot_info.get("description", "").lower():
                accessibility_analysis = self._analyze_accessibility_features(bot_info)
                self.categories[category].accessibility_score += accessibility_analysis["score"]
                self.categories[category].accessibility_features.extend(accessibility_analysis["features"])
            
            # Analyze prompt
            prompt = bot_info.get("prompt_info")
            if prompt:
                analysis = PromptAnalysis(
                    original_text=prompt,
                    bot_name=bot_name,
                    bot_description=bot_info.get("description", ""),
                    evaluation=self._evaluate_prompt(prompt),
                    improvements=self._suggest_improvements(prompt, self._evaluate_prompt(prompt)),
                    accessibility_notes=self._generate_accessibility_notes(prompt)
                )
                self._save_prompt_analysis(analysis)
            
            # Analyze tools
            tools = bot.get("bot_option_data", {}).get("plugin_detail_map", {})
            for tool_id, tool_info in tools.items():
                analysis = ToolAnalysis(
                    tool_name=tool_info.get("name", ""),
                    description=tool_info.get("description", ""),
                    bot_name=bot_name,
                    configuration=tool_info,
                    api_endpoints=self._extract_api_endpoints(tool_info),
                    usage_notes=self._generate_tool_usage_notes(tool_info)
                )
                self._save_tool_analysis(analysis)
        
        self._generate_category_report()
        self._generate_accessibility_audit()
        self._generate_summary()

    def _generate_accessibility_notes(self, prompt: str) -> List[str]:
        """Generate accessibility-focused notes about the prompt"""
        notes = []
        
        # Check for screen reader considerations
        if "screen reader" in prompt.lower():
            notes.append("✓ Includes screen reader considerations")
        else:
            notes.append("Consider adding specific screen reader guidance")
            
        # Check for alternative text guidance
        if "alt text" in prompt.lower() or "alternative text" in prompt.lower():
            notes.append("✓ Includes alternative text guidance")
        else:
            notes.append("Add guidelines for alternative text generation")
            
        # Check for semantic HTML references
        if "semantic" in prompt.lower() or "aria" in prompt.lower():
            notes.append("✓ References semantic markup/ARIA")
        else:
            notes.append("Consider adding semantic markup/ARIA guidelines")
            
        return notes

    def _generate_tool_usage_notes(self, tool_info: Dict) -> List[str]:
        """Generate usage notes for a tool"""
        notes = []
        
        # Basic tool documentation
        notes.append(f"Purpose: {tool_info.get('description', 'No description provided')}")
        
        # Add accessibility considerations
        notes.append("Accessibility Considerations:")
        notes.append("- Ensure output is screen-reader friendly")
        notes.append("- Include proper error messaging")
        notes.append("- Consider keyboard navigation if applicable")
        
        return notes

    def _save_prompt_analysis(self, analysis: PromptAnalysis) -> None:
        """Save prompt analysis to file"""
        safe_name = re.sub(r'[^a-zA-Z0-9]', '_', analysis.bot_name.lower())
        filename = f"{self.output_dir}/prompts/{safe_name}_prompt.md"
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(f"# Prompt Analysis: {analysis.bot_name}\n\n")
            f.write(f"## Description\n{analysis.bot_description}\n\n")
            f.write("## Original Prompt\n```\n")
            f.write(analysis.original_text)
            f.write("\n```\n\n")
            f.write("## Evaluation\n")
            f.write(analysis.evaluation)
            f.write("\n\n## Suggested Improvements\n")
            for improvement in analysis.improvements:
                f.write(f"- {improvement}\n")
            f.write("\n## Accessibility Notes\n")
            for note in analysis.accessibility_notes:
                f.write(f"- {note}\n")

    def _save_tool_analysis(self, analysis: ToolAnalysis) -> None:
        """Save tool analysis to file"""
        safe_name = re.sub(r'[^a-zA-Z0-9]', '_', analysis.tool_name.lower())
        filename = f"{self.output_dir}/tools/{safe_name}_tool.md"
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(f"# Tool Analysis: {analysis.tool_name}\n\n")
            f.write(f"## Used By Bot: {analysis.bot_name}\n\n")
            f.write(f"## Description\n{analysis.description}\n\n")
            if analysis.api_endpoints:
                f.write("## API Endpoints\n")
                for endpoint in analysis.api_endpoints:
                    f.write(f"- {endpoint}\n")
            f.write("\n## Usage Notes\n")
            for note in analysis.usage_notes:
                f.write(f"- {note}\n")

    def _generate_category_report(self) -> None:
        """Generate a report of bot categories"""
        filename = f"{self.output_dir}/documentation/categories.md"
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write("# Bot Categories Analysis\n\n")
            
            for category_id, category in self.categories.items():
                if category.bots:  # Only show categories with bots
                    f.write(f"## {category.name}\n")
                    f.write(f"{category.description}\n\n")
                    f.write("### Bots in this category:\n")
                    for bot in category.bots:
                        f.write(f"- {bot}\n")
                    if category.accessibility_score > 0:
                        f.write(f"\nAccessibility Score: {category.accessibility_score}\n")
                        f.write("Accessibility Features:\n")
                        for feature in set(category.accessibility_features):
                            f.write(f"- {feature.replace('_', ' ').title()}\n")
                    f.write("\n")

    def _generate_accessibility_audit(self) -> None:
        """Generate a comprehensive accessibility audit report"""
        filename = f"{self.output_dir}/documentation/accessibility_audit.md"
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write("# Accessibility Audit Report\n\n")
            
            f.write("## Overview\n")
            total_accessibility_score = sum(c.accessibility_score for c in self.categories.values())
            f.write(f"Total Accessibility Score: {total_accessibility_score}\n\n")
            
            f.write("## Accessibility-Focused Bots\n")
            accessibility_bots = self.categories["accessibility"].bots
            f.write(f"Number of dedicated accessibility bots: {len(accessibility_bots)}\n\n")
            
            f.write("### Key Accessibility Features Found:\n")
            all_features = []
            for category in self.categories.values():
                all_features.extend(category.accessibility_features)
            
            feature_counts = {}
            for feature in all_features:
                feature_counts[feature] = feature_counts.get(feature, 0) + 1
            
            for feature, count in sorted(feature_counts.items(), key=lambda x: x[1], reverse=True):
                f.write(f"- {feature.replace('_', ' ').title()}: {count} implementations\n")
            
            f.write("\n## Recommendations\n")
            f.write("1. Screen Reader Support: Ensure all bots provide clear, structured output\n")
            f.write("2. Error Handling: Implement consistent error messaging across all bots\n")
            f.write("3. Alternative Text: Standardize image description protocols\n")
            f.write("4. ARIA Integration: Enhance semantic markup usage in web interfaces\n")
            f.write("5. Keyboard Navigation: Implement consistent keyboard shortcuts\n")

    def _generate_summary(self) -> None:
        """Generate summary documentation"""
        filename = f"{self.output_dir}/documentation/README.md"
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write("# Coze Bot Analysis Summary\n\n")
            f.write(f"Analysis generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            
            f.write("## Directory Structure\n")
            f.write("```\n")
            f.write("coze_analysis/\n")
            f.write("├── prompts/      # Individual prompt analyses\n")
            f.write("├── tools/        # Tool configurations and analyses\n")
            f.write("├── workflows/    # Workflow documentation\n")
            f.write("└── documentation/ # General documentation\n")
            f.write("```\n\n")
            
            f.write("## Quick Links\n")
            f.write("- [Prompts](../prompts/)\n")
            f.write("- [Tools](../tools/)\n")
            f.write("- [Workflows](../workflows/)\n\n")
            
            f.write("## Accessibility Focus\n")
            f.write("This analysis emphasizes accessibility considerations including:\n")
            f.write("- Screen reader compatibility\n")
            f.write("- Alternative text guidelines\n")
            f.write("- Semantic markup and ARIA practices\n")
            f.write("- Error handling and user feedback\n")

if __name__ == "__main__":
    analyzer = CozeAnalyzer("coze_history.json")
    analyzer.analyze()
    print("Analysis complete. Check the 'coze_analysis' directory for results.") 