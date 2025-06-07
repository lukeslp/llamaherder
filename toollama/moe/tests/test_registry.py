"""Tests for the MoE model registry."""

import pytest
import yaml
import tempfile
from pathlib import Path
from moe.core.registry import (
    ModelRegistry,
    ModelConfig,
    ModelCapabilities,
    GlobalSettings,
    ModelNotFoundError,
    InvalidConfigError
)

@pytest.fixture
def test_config():
    """Test configuration fixture"""
    return {
        'models': {
            'test_model': {
                'model_id': 'test_model',
                'model_type': 'belter',
                'base_model': 'mistral:7b',
                'endpoint': 'http://localhost:8001/test',
                'capabilities': {
                    'capabilities': ['test_capability'],
                    'max_tokens': 2048,
                    'temperature': 0.4,
                    'timeout': 30
                }
            }
        },
        'settings': {
            'retry_config': {
                'max_retries': 3,
                'backoff_factor': 1.5,
                'max_backoff': 30
            },
            'rate_limits': {
                'requests_per_minute': 60,
                'requests_per_hour': 1000
            },
            'monitoring': {
                'enable_metrics': True,
                'log_level': 'INFO'
            },
            'security': {
                'require_authentication': True,
                'token_expiry': 3600
            }
        }
    }

@pytest.fixture
def config_file(test_config):
    """Create temporary config file"""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
        yaml.safe_dump(test_config, f)
        return Path(f.name)

@pytest.fixture
def registry(config_file):
    """ModelRegistry fixture"""
    return ModelRegistry(str(config_file))

def test_load_config(registry, test_config):
    """Test configuration loading"""
    assert len(registry.models) == 1
    assert 'test_model' in registry.models
    assert registry.settings is not None
    
    model = registry.models['test_model']
    assert model.model_id == 'test_model'
    assert model.model_type == 'belter'
    assert model.base_model == 'mistral:7b'
    assert model.endpoint == 'http://localhost:8001/test'
    assert 'test_capability' in model.capabilities.capabilities

def test_register_model(registry):
    """Test model registration"""
    new_model = {
        'model_id': 'new_model',
        'model_type': 'drummer',
        'base_model': 'llama3.2:3b',
        'endpoint': 'http://localhost:8002/new',
        'capabilities': {
            'capabilities': ['new_capability'],
            'max_tokens': 1024,
            'temperature': 0.2,
            'timeout': 15
        }
    }
    
    registry.register_model('new_model', new_model)
    assert 'new_model' in registry.models
    assert 'new_capability' in registry.capability_index

def test_get_model(registry):
    """Test getting model configuration"""
    model = registry.get_model('test_model')
    assert isinstance(model, ModelConfig)
    assert model.model_id == 'test_model'
    
    with pytest.raises(ModelNotFoundError):
        registry.get_model('non_existent_model')

def test_find_models_by_capability(registry):
    """Test finding models by capability"""
    models = registry.find_models_by_capability('test_capability')
    assert len(models) == 1
    assert 'test_model' in models
    
    empty_models = registry.find_models_by_capability('non_existent_capability')
    assert len(empty_models) == 0

def test_find_models_by_type(registry):
    """Test finding models by type"""
    models = registry.find_models_by_type('belter')
    assert len(models) == 1
    assert 'test_model' in models
    
    empty_models = registry.find_models_by_type('non_existent_type')
    assert len(empty_models) == 0

def test_update_model_config(registry):
    """Test updating model configuration"""
    updates = {
        'capabilities': {
            'capabilities': ['updated_capability'],
            'max_tokens': 4096,
            'temperature': 0.5,
            'timeout': 45
        }
    }
    
    registry.update_model_config('test_model', updates)
    model = registry.get_model('test_model')
    assert 'updated_capability' in model.capabilities.capabilities
    assert model.capabilities.max_tokens == 4096
    
    with pytest.raises(ModelNotFoundError):
        registry.update_model_config('non_existent_model', updates)

def test_remove_model(registry):
    """Test removing model"""
    registry.remove_model('test_model')
    assert 'test_model' not in registry.models
    assert 'test_capability' not in registry.capability_index
    
    with pytest.raises(ModelNotFoundError):
        registry.remove_model('non_existent_model')

def test_get_settings(registry):
    """Test getting global settings"""
    settings = registry.get_settings()
    assert isinstance(settings, GlobalSettings)
    assert settings.retry_config['max_retries'] == 3
    assert settings.rate_limits['requests_per_minute'] == 60

def test_invalid_config():
    """Test handling invalid configuration"""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
        f.write("invalid: yaml: content")
        
    with pytest.raises(InvalidConfigError):
        ModelRegistry(f.name)

def test_model_validation():
    """Test model configuration validation"""
    # Valid model config
    valid_config = {
        'model_id': 'test_model',
        'model_type': 'belter',
        'base_model': 'mistral:7b',
        'endpoint': 'http://localhost:8001/test',
        'capabilities': {
            'capabilities': ['test_capability'],
            'max_tokens': 2048,
            'temperature': 0.4,
            'timeout': 30
        }
    }
    model = ModelConfig(**valid_config)
    assert model.model_id == 'test_model'
    
    # Invalid model config (missing required fields)
    invalid_config = {
        'model_id': 'test_model',
        'model_type': 'belter'
    }
    with pytest.raises(ValueError):
        ModelConfig(**invalid_config)

def test_capabilities_validation():
    """Test capabilities configuration validation"""
    # Valid capabilities
    valid_capabilities = {
        'capabilities': ['test_capability'],
        'max_tokens': 2048,
        'temperature': 0.4,
        'timeout': 30
    }
    capabilities = ModelCapabilities(**valid_capabilities)
    assert capabilities.max_tokens == 2048
    
    # Invalid capabilities (missing required fields)
    invalid_capabilities = {
        'capabilities': ['test_capability']
    }
    with pytest.raises(ValueError):
        ModelCapabilities(**invalid_capabilities)

def test_settings_validation():
    """Test global settings validation"""
    # Valid settings
    valid_settings = {
        'retry_config': {
            'max_retries': 3
        },
        'rate_limits': {
            'requests_per_minute': 60
        },
        'monitoring': {
            'enable_metrics': True
        },
        'security': {
            'require_authentication': True
        }
    }
    settings = GlobalSettings(**valid_settings)
    assert settings.retry_config['max_retries'] == 3
    
    # Invalid settings (missing required fields)
    invalid_settings = {
        'retry_config': {
            'max_retries': 3
        }
    }
    with pytest.raises(ValueError):
        GlobalSettings(**invalid_settings) 