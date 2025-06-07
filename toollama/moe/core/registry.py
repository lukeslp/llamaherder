"""
Model registry for managing available models and their configurations.
"""

import os
from pathlib import Path
from typing import Dict, Any, Optional
import yaml
import logging

logger = logging.getLogger(__name__)

class ModelNotFoundError(Exception):
    """Raised when a requested model is not found in the registry"""
    pass

class ModelRegistry:
    """Registry for managing model configurations"""
    
    def __init__(self, config_path: Optional[Path] = None):
        """
        Initialize the model registry.
        
        Args:
            config_path: Path to models.yaml configuration file
        """
        self.models: Dict[str, Dict[str, Any]] = {}
        self.config_path = config_path
        
        if config_path and config_path.exists():
            self.load_config(config_path)
        else:
            # Use default configuration
            self.models = {
                'camina': {
                    'type': 'primary',
                    'base_model': 'mistral-22b',
                    'endpoint': os.getenv('CAMINA_ENDPOINT', 'http://localhost:6000/camina'),
                    'capabilities': ['orchestration', 'conversation', 'planning']
                },
                'property_belter': {
                    'type': 'belter',
                    'base_model': 'mistral-7b',
                    'endpoint': os.getenv('PROPERTY_BELTER_ENDPOINT', 'http://localhost:6001/belter'),
                    'capabilities': ['real_estate', 'location_analysis', 'market_research']
                },
                'knowledge_belter': {
                    'type': 'belter',
                    'base_model': 'mistral-7b',
                    'endpoint': os.getenv('KNOWLEDGE_BELTER_ENDPOINT', 'http://localhost:6002/belter'),
                    'capabilities': ['knowledge_base', 'fact_checking', 'research']
                },
                'location_drummer': {
                    'type': 'drummer',
                    'base_model': 'llama-3b',
                    'endpoint': os.getenv('LOCATION_DRUMMER_ENDPOINT', 'http://localhost:6003/drummer'),
                    'capabilities': ['location_services', 'mapping', 'navigation']
                }
            }
            
    def load_config(self, config_path: Path) -> None:
        """
        Load model configurations from YAML file.
        
        Args:
            config_path: Path to configuration file
        """
        try:
            with open(config_path, 'r') as f:
                self.models = yaml.safe_load(f)
            logger.info(f"Loaded {len(self.models)} models from {config_path}")
        except Exception as e:
            logger.error(f"Error loading model config: {e}")
            raise
            
    def get_model(self, model_id: str) -> Dict[str, Any]:
        """
        Get model configuration by ID.
        
        Args:
            model_id: Model identifier
            
        Returns:
            Model configuration dictionary
            
        Raises:
            ModelNotFoundError: If model not found
        """
        if model_id not in self.models:
            raise ModelNotFoundError(f"Model {model_id} not found")
        return self.models[model_id]
        
    def register_model(self, model_id: str, config: Dict[str, Any]) -> None:
        """
        Register a new model configuration.
        
        Args:
            model_id: Model identifier
            config: Model configuration
        """
        self.models[model_id] = config
        logger.info(f"Registered model {model_id}")
        
    def get_models_by_type(self, model_type: str) -> Dict[str, Dict[str, Any]]:
        """
        Get all models of a specific type.
        
        Args:
            model_type: Model type to filter by
            
        Returns:
            Dictionary of matching models
        """
        return {
            model_id: config
            for model_id, config in self.models.items()
            if config.get('type') == model_type
        }
        
    def get_models_by_capability(self, capability: str) -> Dict[str, Dict[str, Any]]:
        """
        Get all models with a specific capability.
        
        Args:
            capability: Capability to filter by
            
        Returns:
            Dictionary of matching models
        """
        return {
            model_id: config
            for model_id, config in self.models.items()
            if capability in config.get('capabilities', [])
        }
        
    def save_config(self) -> None:
        """Save current configuration to file"""
        if not self.config_path:
            logger.warning("No config path set, cannot save")
            return
            
        try:
            with open(self.config_path, 'w') as f:
                yaml.safe_dump(self.models, f)
            logger.info(f"Saved configuration to {self.config_path}")
        except Exception as e:
            logger.error(f"Error saving config: {e}")
            raise
