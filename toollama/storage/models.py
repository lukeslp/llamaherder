import requests
import json
from typing import Dict, List, Optional

def get_model_category(model_id: str) -> str:
    """Determine the category for a model based on its ID."""
    model_id = model_id.lower()
    
    if any(x in model_id for x in ['drummer-', 'camina']):
        return "Dreamwalker Models"
    elif any(x in model_id for x in ['vision', 'llava', 'bakllava', 'minicpm-v', 'moondream']):
        return "Vision Models"
    elif any(x in model_id for x in ['code', 'starcoder', 'opencoder']):
        return "Code Models"
    elif 'llama' in model_id:
        return "Llama Models"
    elif 'mistral' in model_id:
        return "Mistral Models"
    elif any(x in model_id for x in ['smollm', 'phi', 'nemotron-mini']):
        return "Small & Fast Models"
    elif any(x in model_id for x in ['impossible', 'falcon', 'dolphin', 'gemma']):
        return "Experimental Models"
    elif any(x in model_id for x in ['deepseek', 'granite', 'olmo']):
        return "Foundation Models"
    return "Other Models"

def get_model_info(model_id: str) -> Dict[str, str]:
    """Get the description and other metadata for a model."""
    model_id = model_id.lower()
    
    # Default size if not found
    size = "4.1GB"
    
    # Special cases for known model sizes
    if "14b" in model_id or "13b" in model_id:
        size = "8.0GB"
    elif "7b" in model_id:
        size = "4.7GB"
    elif "8b" in model_id:
        size = "4.9GB"
    elif "3b" in model_id:
        size = "2.0GB"
    elif "1.5b" in model_id:
        size = "1.1GB"
    elif "1b" in model_id:
        size = "1.3GB"
    elif "135m" in model_id:
        size = "270MB"
    elif "360m" in model_id:
        size = "725MB"
    elif "1.7b" in model_id:
        size = "990MB"
    
    # Model descriptions
    descriptions = {
        "camina": "Dreamwalker coordinator - routes requests to specialized models while providing direct assistance",
        "drummer-code": "Specialized code synthesis",
        "drummer-scrape": "Web content extraction",
        "drummer-arxiv": "Research paper analysis",
        "drummer-infinite": "Internet search integration",
        "drummer-document": "Document analysis and processing",
        "drummer-knowledge": "Knowledge base integration",
        "drummer-timecalc": "Time-based calculations",
        "drummer-dataproc": "Data processing and analysis",
        "drummer-finance": "Financial analysis",
        "drummer-wayback": "Historical web access",
        "llava": "Multimodal vision-language model",
        "bakllava": "Optimized vision-language model",
        "minicpm-v": "Optimized vision-language model",
        "moondream": "Lightweight vision model",
        "starcoder2": "Multi-language code generation",
        "codellama": "Code completion and generation",
        "qwen2.5-coder": "Specialized code synthesis",
        "opencoder": "General code understanding",
        "phi3": "Mathematical and logical tasks",
        "phi3.5": "Mathematical and logical tasks",
        "phi4": "Advanced reasoning model",
        "nemotron-mini": "Efficient general-purpose model",
        "impossible_alt": "Creative problem solving",
        "falcon3": "Advanced language model",
        "dolphin3": "Enhanced conversational model",
        "gemma2": "Advanced language understanding",
        "deepseek-r1": "Foundation model for general tasks",
        "granite3.1-moe": "Sparse MoE architecture with conditional routing",
        "granite3.1-dense": "Dense transformer architecture",
        "olmo2": "General purpose foundation model",
        "mistral": "General-purpose foundation model"
    }
    
    # Find matching description
    description = "General purpose model"
    for key, desc in descriptions.items():
        if key in model_id:
            description = desc
            break
    
    return {
        "size": size,
        "info": description
    }

def list_local_models() -> List[Dict[str, str]]:
    """Get list of local models and their metadata."""
    url = "http://localhost:11434/v1/models"
    response = requests.get(url)
    response.raise_for_status()
    
    models_data = []
    if "data" in response.json():
        models = response.json()["data"]
        for model in models:
            model_id = model.get('id', '')
            if not model_id:
                continue
                
            info = get_model_info(model_id)
            category = get_model_category(model_id)
            
            models_data.append({
                "id": model_id,
                "category": category,
                "size": info["size"],
                "info": info["info"]
            })
    
    # Sort models by category and name
    models_data.sort(key=lambda x: (x["category"], x["id"]))
    
    return models_data

def generate_models_json():
    """Generate a JavaScript file containing model information."""
    try:
        models = list_local_models()
        
        # Group models by category
        categories = {}
        for model in models:
            category = model["category"]
            if category not in categories:
                categories[category] = []
            categories[category].append({
                "value": model["id"],
                "text": model["id"].split('/')[-1].replace(':latest', ''),
                "data-size": model["size"],
                "data-info": model["info"]
            })
        
        # Create final structure
        output = {
            "categories": [
                {
                    "label": category,
                    "models": models_list
                }
                for category, models_list in categories.items()
            ]
        }
        
        # Ensure Dreamwalker Models are first and Camina is default
        output["categories"].sort(key=lambda x: x["label"] != "Dreamwalker Models")
        for category in output["categories"]:
            if category["label"] == "Dreamwalker Models":
                for model in category["models"]:
                    if "camina" in model["value"].lower():
                        model["selected"] = True
                        break
        
        # Write to JavaScript file
        with open('models.js', 'w') as f:
            f.write("// Auto-generated by models.py\n")
            f.write("const modelData = ")
            json.dump(output, f, indent=2)
            f.write(";\n")
            
        print("Successfully generated models.js")
        
    except Exception as e:
        print(f"Error generating models.js: {str(e)}")

if __name__ == "__main__":
    generate_models_json()