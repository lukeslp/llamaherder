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

def get_model_details(model_id: str) -> Dict[str, str]:
    """Get detailed information about a model using the show endpoint."""
    try:
        url = "http://localhost:11434/api/show"
        response = requests.post(url, json={"name": model_id})
        response.raise_for_status()
        details = response.json()
        
        # Extract size in bytes and convert to human readable
        size_bytes = details.get("size", 0)
        if size_bytes > 1024*1024*1024:  # GB
            size = f"{size_bytes/(1024*1024*1024):.1f}GB"
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
        if parameter_size:
            description_parts.append(f"{parameter_size} parameters")
        if family:
            description_parts.append(f"{family.title()} architecture")
        elif families and families[0]:
            description_parts.append(f"{families[0].title()} architecture")
            
        if not description_parts:
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
            for key, desc in descriptions.items():
                if key in model_id:
                    description_parts.append(desc)
                    break
            
            if not description_parts:
                description_parts.append("General purpose model")
        
        return {
            "size": size,
            "info": " • ".join(description_parts)
        }
        
    except Exception as e:
        print(f"Error getting details for {model_id}: {str(e)}")
        return {
            "size": "Unknown",
            "info": "Model information unavailable"
        }

def list_local_models() -> List[Dict[str, str]]:
    """Get list of local models and their metadata."""
    url = "http://localhost:11434/api/tags"
    response = requests.get(url)
    response.raise_for_status()
    
    models_data = []
    if "models" in response.json():
        models = response.json()["models"]
        for model in models:
            model_id = model.get('name', '')
            if not model_id:
                continue
            
            # Get size from the tags response
            size_bytes = model.get('size', 0)
            if size_bytes > 1024*1024*1024:  # GB
                size = f"{size_bytes/(1024*1024*1024):.1f}GB"
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
                    "desc": "Specialized code synthesis model optimized for software development",
                    "best_for": "Code generation, debugging, and technical documentation"
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
            }
            
            # Get model description and best use cases
            for key, desc_data in descriptions.items():
                if key in model_id_lower:
                    description = f"{desc_data['desc']}|{desc_data['best_for']}"
                    break
            
            # If no custom description, generate from model details
            if not description:
                general_desc = []
                best_for = []
                
                if family := model_details.get('family'):
                    general_desc.append(f"{family.title()}-based language model")
                    best_for.append("general text generation and comprehension")
                elif families := model_details.get('families', []):
                    if families and families[0]:
                        general_desc.append(f"{families[0].title()}-based language model")
                        best_for.append("general text generation and comprehension")
                
                if "vision" in model_id_lower or any(x in model_id_lower for x in ['llava', 'bakllava', 'moondream']):
                    general_desc.append("with multimodal capabilities")
                    best_for.append("image understanding and visual tasks")
                elif "code" in model_id_lower:
                    general_desc.append("optimized for code generation")
                    best_for.append("software development and technical tasks")
                
                description = f"{' '.join(general_desc)}|{', '.join(best_for)}"
            
            # Build data points with labels
            data_points = []
            
            # Add parameter size if available
            if param_size := model_details.get('parameter_size'):
                data_points.append(f"Parameters: {param_size}")
            
            # Add architecture info
            if family := model_details.get('family'):
                data_points.append(f"Architecture: {family.title()}")
            elif families := model_details.get('families', []):
                if families and families[0]:
                    data_points.append(f"Architecture: {families[0].title()}")
            
            category = get_model_category(model_id)
            
            models_data.append({
                "id": model_id,
                "category": category,
                "size": size,
                "info": " | ".join(data_points),
                "description": description,
                "details": model_details
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