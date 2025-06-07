# Code Snippets from toollama/storage/update_models.py

File: `toollama/storage/update_models.py`  
Language: Python  
Extracted: 2025-06-07 05:11:19  

## Snippet 1
Lines 1-4

```Python
import requests
import json
from typing import Dict, List, Optional
```

## Snippet 2
Lines 23-26

```Python
elif any(x in model_id for x in ['deepseek', 'granite', 'olmo']):
        return "Foundation Models"
    return "Other Models"
```

## Snippet 3
Lines 27-36

```Python
def get_model_details(model_id: str) -> Dict[str, str]:
    """Get detailed information about a model using the show endpoint."""
    try:
        url = "http://localhost:11434/api/show"
        response = requests.post(url, json={"name": model_id})
        response.raise_for_status()
        details = response.json()

        # Extract size in bytes and convert to human readable
        size_bytes = details.get("size", 0)
```

## Snippet 4
Lines 39-51

```Python
elif size_bytes > 1024*1024:  # MB
            size = f"{size_bytes/(1024*1024):.0f}MB"
        else:
            size = f"{size_bytes/1024:.0f}KB"

        # Get model details
        model_details = details.get("details", {})
        parameter_size = model_details.get("parameter_size", "")
        families = model_details.get("families", [])
        family = model_details.get("family", "")

        # Build description
        description_parts = []
```

## Snippet 5
Lines 60-74

```Python
# Fallback to our predefined descriptions if no details available
            model_id = model_id.lower()
            descriptions = {
                "camina": "Dreamwalker coordinator - routes requests to specialized models",
                "drummer-code": "Specialized code synthesis",
                "drummer-scrape": "Web content extraction",
                "drummer-arxiv": "Research paper analysis",
                "drummer-infinite": "Internet search integration",
                "drummer-document": "Document analysis and processing",
                "drummer-knowledge": "Knowledge base integration",
                "drummer-timecalc": "Time-based calculations",
                "drummer-dataproc": "Data processing and analysis",
                "drummer-finance": "Financial analysis",
                "drummer-wayback": "Historical web access"
            }
```

## Snippet 6
Lines 76-79

```Python
if key in model_id:
                    description_parts.append(desc)
                    break
```

## Snippet 7
Lines 83-87

```Python
return {
            "size": size,
            "info": " • ".join(description_parts)
        }
```

## Snippet 8
Lines 89-94

```Python
print(f"Error getting details for {model_id}: {str(e)}")
        return {
            "size": "Unknown",
            "info": "Model information unavailable"
        }
```

## Snippet 9
Lines 95-101

```Python
def list_local_models() -> List[Dict[str, str]]:
    """Get list of local models and their metadata."""
    url = "http://localhost:11434/api/tags"
    response = requests.get(url)
    response.raise_for_status()

    models_data = []
```

## Snippet 10
Lines 106-110

```Python
if not model_id:
                continue

            # Get size from the tags response
            size_bytes = model.get('size', 0)
```

## Snippet 11
Lines 113-129

```Python
elif size_bytes > 1024*1024:  # MB
                size = f"{size_bytes/(1024*1024):.0f}MB"
            else:
                size = f"{size_bytes/1024:.0f}KB"

            # Get details directly from the tags response
            model_details = model.get('details', {})

            # Build model description
            description = ""
            model_id_lower = model_id.lower()
            descriptions = {
                "camina": {
                    "desc": "Dreamwalker coordinator model that intelligently routes requests to specialized models",
                    "best_for": "Task delegation, workflow optimization, and coordinating complex operations"
                },
                "drummer-code": {
```

## Snippet 12
Lines 132-168

```Python
},
                "drummer-scrape": {
                    "desc": "Web content extraction and processing model",
                    "best_for": "Web scraping, content analysis, and data extraction"
                },
                "drummer-arxiv": {
                    "desc": "Research paper analysis and comprehension model",
                    "best_for": "Academic research, paper summaries, and scientific analysis"
                },
                "drummer-infinite": {
                    "desc": "Internet search integration and information synthesis model",
                    "best_for": "Web search, information gathering, and knowledge synthesis"
                },
                "drummer-document": {
                    "desc": "Document analysis and processing specialist",
                    "best_for": "Document parsing, content extraction, and format conversion"
                },
                "drummer-knowledge": {
                    "desc": "Knowledge base integration and management model",
                    "best_for": "Knowledge management, data organization, and information retrieval"
                },
                "drummer-timecalc": {
                    "desc": "Time-based calculations and scheduling model",
                    "best_for": "Time series analysis, scheduling, and temporal reasoning"
                },
                "drummer-dataproc": {
                    "desc": "Data processing and analysis specialist",
                    "best_for": "Data analysis, pattern recognition, and statistical processing"
                },
                "drummer-finance": {
                    "desc": "Financial analysis and processing model",
                    "best_for": "Financial calculations, market analysis, and economic modeling"
                },
                "drummer-wayback": {
                    "desc": "Historical web access and analysis model",
                    "best_for": "Historical data retrieval, trend analysis, and temporal web content"
                }
```

## Snippet 13
Lines 173-176

```Python
if key in model_id_lower:
                    description = f"{desc_data['desc']}|{desc_data['best_for']}"
                    break
```

## Snippet 14
Lines 213-223

```Python
category = get_model_category(model_id)

            models_data.append({
                "id": model_id,
                "category": category,
                "size": size,
                "info": " | ".join(data_points),
                "description": description,
                "details": model_details
            })
```

## Snippet 15
Lines 224-228

```Python
# Sort models by category and name
    models_data.sort(key=lambda x: (x["category"], x["id"]))

    return models_data
```

## Snippet 16
Lines 229-235

```Python
def generate_models_json():
    """Generate a JavaScript file containing model information."""
    try:
        models = list_local_models()

        # Group models by category
        categories = {}
```

## Snippet 17
Lines 238-246

```Python
if category not in categories:
                categories[category] = []
            categories[category].append({
                "value": model["id"],
                "text": model["id"].split('/')[-1].replace(':latest', ''),
                "data-size": model["size"],
                "data-info": model["info"]
            })
```

## Snippet 18
Lines 247-253

```Python
# Create final structure
        output = {
            "categories": [
                {
                    "label": category,
                    "models": models_list
                }
```

## Snippet 19
Lines 256-259

```Python
}

        # Ensure Dreamwalker Models are first and Camina is default
        output["categories"].sort(key=lambda x: x["label"] != "Dreamwalker Models")
```

## Snippet 20
Lines 267-275

```Python
# Write to JavaScript file
        with open('models.js', 'w') as f:
            f.write("// Auto-generated by models.py\n")
            f.write("const modelData = ")
            json.dump(output, f, indent=2)
            f.write(";\n")

        print("Successfully generated models.js")
```

