# Code Snippets from toollama/prompts/coze_analyzer.py

File: `toollama/prompts/coze_analyzer.py`  
Language: Python  
Extracted: 2025-06-07 05:11:01  

## Snippet 1
Lines 1-12

```Python
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
```

## Snippet 2
Lines 13-28

```Python
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
```

## Snippet 3
Lines 30-38

```Python
class PromptAnalysis:
    """Represents analysis of a single prompt"""
    original_text: str
    bot_name: str
    bot_description: str
    evaluation: str
    improvements: List[str]
    accessibility_notes: List[str]
```

## Snippet 4
Lines 40-48

```Python
class ToolAnalysis:
    """Represents analysis of a tool configuration"""
    tool_name: str
    description: str
    bot_name: str
    configuration: Dict[str, Any]
    api_endpoints: List[str]
    usage_notes: List[str]
```

## Snippet 5
Lines 50-57

```Python
class BotCategory:
    """Represents a category of bots"""
    name: str
    description: str
    bots: List[str]
    accessibility_score: int = 0
    accessibility_features: List[str] = None
```

## Snippet 6
Lines 65-82

```Python
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
```

## Snippet 7
Lines 83-91

```Python
def _setup_directories(self) -> None:
        """Create necessary output directories"""
        dirs = [
            self.output_dir,
            f"{self.output_dir}/prompts",
            f"{self.output_dir}/tools",
            f"{self.output_dir}/workflows",
            f"{self.output_dir}/documentation"
        ]
```

## Snippet 8
Lines 95-102

```Python
def _evaluate_prompt(self, prompt: str) -> str:
        """
        Evaluate a prompt's effectiveness
        Returns a detailed analysis string
        """
        issues = []

        # Check length
```

## Snippet 9
Lines 120-123

```Python
def _suggest_improvements(self, prompt: str, evaluation: str) -> List[str]:
        """Generate improvement suggestions based on evaluation"""
        improvements = []
```

## Snippet 10
Lines 133-137

```Python
if "error handling" in evaluation:
            improvements.append("Include specific error handling instructions and fallback behaviors")

        return improvements
```

## Snippet 11
Lines 138-141

```Python
def _extract_api_endpoints(self, tool_config: Dict) -> List[str]:
        """Extract API endpoints from tool configuration"""
        endpoints = []
```

## Snippet 12
Lines 162-175

```Python
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
```

## Snippet 13
Lines 183-202

```Python
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
```

## Snippet 14
Lines 209-212

```Python
if "wcag" in prompt or "web content accessibility" in prompt:
            features.append("wcag_compliance")
            score += 2
```

## Snippet 15
Lines 213-223

```Python
if "accessibility testing" in prompt or "accessibility check" in prompt:
            features.append("testing")
            score += 2

        return {
            "bot_name": name,
            "score": score,
            "features": features,
            "description": description
        }
```

## Snippet 16
Lines 224-233

```Python
def analyze(self) -> None:
        """Main analysis method"""
        try:
            with open(self.export_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except Exception as e:
            print(f"Error loading export file: {e}")
            return

        # Process each bot
```

## Snippet 17
Lines 234-242

```Python
for bot in data.get("bot_list", []):
            bot_info = bot.get("bot_info", {})
            bot_name = bot_info.get("name", "Unnamed Bot")

            # Categorize bot
            category = self._categorize_bot(bot_info)
            self.categories[category].bots.append(bot_name)

            # Analyze accessibility features
```

## Snippet 18
Lines 243-249

```Python
if category == "accessibility" or "accessibility" in bot_info.get("description", "").lower():
                accessibility_analysis = self._analyze_accessibility_features(bot_info)
                self.categories[category].accessibility_score += accessibility_analysis["score"]
                self.categories[category].accessibility_features.extend(accessibility_analysis["features"])

            # Analyze prompt
            prompt = bot_info.get("prompt_info")
```

## Snippet 19
Lines 250-262

```Python
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
```

## Snippet 20
Lines 263-273

```Python
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
```

## Snippet 21
Lines 278-281

```Python
def _generate_accessibility_notes(self, prompt: str) -> List[str]:
        """Generate accessibility-focused notes about the prompt"""
        notes = []
```

## Snippet 22
Lines 283-287

```Python
if "screen reader" in prompt.lower():
            notes.append("✓ Includes screen reader considerations")
        else:
            notes.append("Consider adding specific screen reader guidance")
```

## Snippet 23
Lines 295-301

```Python
if "semantic" in prompt.lower() or "aria" in prompt.lower():
            notes.append("✓ References semantic markup/ARIA")
        else:
            notes.append("Consider adding semantic markup/ARIA guidelines")

        return notes
```

## Snippet 24
Lines 303-312

```Python
"""Generate usage notes for a tool"""
        notes = []

        # Basic tool documentation
        notes.append(f"Purpose: {tool_info.get('description', 'No description provided')}")

        # Add accessibility considerations
        notes.append("Accessibility Considerations:")
        notes.append("- Ensure output is screen-reader friendly")
        notes.append("- Include proper error messaging")
```

## Snippet 25
Lines 313-316

```Python
notes.append("- Consider keyboard navigation if applicable")

        return notes
```

## Snippet 26
Lines 317-330

```Python
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
```

## Snippet 27
Lines 331-333

```Python
for improvement in analysis.improvements:
                f.write(f"- {improvement}\n")
            f.write("\n## Accessibility Notes\n")
```

## Snippet 28
Lines 337-345

```Python
def _save_tool_analysis(self, analysis: ToolAnalysis) -> None:
        """Save tool analysis to file"""
        safe_name = re.sub(r'[^a-zA-Z0-9]', '_', analysis.tool_name.lower())
        filename = f"{self.output_dir}/tools/{safe_name}_tool.md"

        with open(filename, 'w', encoding='utf-8') as f:
            f.write(f"# Tool Analysis: {analysis.tool_name}\n\n")
            f.write(f"## Used By Bot: {analysis.bot_name}\n\n")
            f.write(f"## Description\n{analysis.description}\n\n")
```

## Snippet 29
Lines 354-360

```Python
def _generate_category_report(self) -> None:
        """Generate a report of bot categories"""
        filename = f"{self.output_dir}/documentation/categories.md"

        with open(filename, 'w', encoding='utf-8') as f:
            f.write("# Bot Categories Analysis\n\n")
```

## Snippet 30
Lines 368-370

```Python
if category.accessibility_score > 0:
                        f.write(f"\nAccessibility Score: {category.accessibility_score}\n")
                        f.write("Accessibility Features:\n")
```

## Snippet 31
Lines 375-382

```Python
def _generate_accessibility_audit(self) -> None:
        """Generate a comprehensive accessibility audit report"""
        filename = f"{self.output_dir}/documentation/accessibility_audit.md"

        with open(filename, 'w', encoding='utf-8') as f:
            f.write("# Accessibility Audit Report\n\n")

            f.write("## Overview\n")
```

## Snippet 32
Lines 383-391

```Python
total_accessibility_score = sum(c.accessibility_score for c in self.categories.values())
            f.write(f"Total Accessibility Score: {total_accessibility_score}\n\n")

            f.write("## Accessibility-Focused Bots\n")
            accessibility_bots = self.categories["accessibility"].bots
            f.write(f"Number of dedicated accessibility bots: {len(accessibility_bots)}\n\n")

            f.write("### Key Accessibility Features Found:\n")
            all_features = []
```

## Snippet 33
Lines 402-408

```Python
f.write("\n## Recommendations\n")
            f.write("1. Screen Reader Support: Ensure all bots provide clear, structured output\n")
            f.write("2. Error Handling: Implement consistent error messaging across all bots\n")
            f.write("3. Alternative Text: Standardize image description protocols\n")
            f.write("4. ARIA Integration: Enhance semantic markup usage in web interfaces\n")
            f.write("5. Keyboard Navigation: Implement consistent keyboard shortcuts\n")
```

## Snippet 34
Lines 409-437

```Python
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
```

