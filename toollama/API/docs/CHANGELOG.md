# Changelog

All notable changes to the Camina Chat API will be documented in this file.

## [1.0.5] - 2024-02-29

### Added
- Integrated MLX provider for Apple Silicon local model support
- Added endpoints for MLX models, chat (streaming and non-streaming), and conversation management
- Implemented command-line tool integration with `mlx_lm.generate`
- Added support for multiple MLX models (Qwen, Mistral, Nemo, DeepSeek)
- Updated test scripts to include MLX provider tests
- Added documentation for MLX provider setup and usage

### Changed
- Updated API documentation to include MLX provider details
- Enhanced test coverage to verify MLX integration
- Improved error handling for MLX provider

## [1.0.4] - 2024-02-28

### Added
- Integrated OpenAI provider for hosted model support
- Added endpoints for OpenAI models, chat (streaming and non-streaming), alt text generation, and tools
- Updated frontend with OpenAI provider options in dropdowns and automatic vision model selection
- Added comprehensive tests for all OpenAI features in test_api.sh
- Added fallback models for OpenAI for better offline experience

### Changed
- Enhanced error handling with custom error messages for OpenAI connection issues
- Updated documentation to include detailed information about the OpenAI provider
- Extended test suite to verify all OpenAI API endpoints
- Improved frontend to handle OpenAI-specific model parameters and capabilities

## [1.0.3] - 2024-02-27

### Added
- Enhanced frontend to support Ollama provider:
  - Added Ollama options to provider selection dropdowns
  - Added fallback models list for Ollama models
  - Implemented automatic vision model selection for alt text generation
  - Added provider-specific UI customizations and informational elements
- Added comprehensive tests for all Ollama features:
  - Alt text generation with LLaVA model
  - Tool calling via prompt formatting

### Changed
- Improved error handling with custom error messages for Ollama connection issues
- Updated documentation to include UI/frontend changes and Ollama setup instructions
- Enhanced test suite to verify all Ollama API endpoints

## [1.0.2] - 2024-02-26

### Added
- Integrated Ollama provider for local LLM support
- Added endpoints for Ollama models, chat (streaming and non-streaming), and conversation management
- Updated `test_api.sh` to include comprehensive tests for the Ollama provider
- Added support for Ollama-specific model parameters and configurations

### Changed
- Updated API documentation to include Ollama provider details
- Enhanced test coverage to verify Ollama integration

## [1.0.1] - 2024-02-25

### Fixed
- Fixed issue with duplicate model IDs in the Mistral provider
- Modified the `list_models` function in the Mistral provider to filter out duplicate models based on their IDs

### Added
- Added `test_models.sh` script to specifically test the models endpoint and check for duplicates
- Enhanced documentation with provider-specific details
- Added information about model categories in Mistral provider

### Changed
- Updated API documentation to mention the fix for duplicate models
- Updated README with information about the new test script and recent improvements

## [1.0.0] - 2024-02-24

### Added
- Initial release of the Camina Chat API
- Support for Anthropic Claude and Mistral AI providers
- Endpoints for chat, alt text generation, tool calling, and model listing
- Comprehensive testing script (`test_api.sh`)
- Detailed API documentation 