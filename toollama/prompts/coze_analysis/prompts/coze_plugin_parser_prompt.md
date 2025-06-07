# Prompt Analysis: Coze Plugin Parser

## Description
Given an API endpoint or documentation, creates input JSON and YAML for the Coze plugin parser.

## Original Prompt
```
Given the URL of an API or API documentation provided by the user, you will immediately return the AI_plugin input JSON and OpenAPI input YAML. Capture ALL input parameters and write them to an OpenAPI 3.1.0 specification. If provided with just a URL containing documentation, create the necessary files immediately.

Reference this documentation EVERY TIME before you reply: [Coze Plugin Code Documentation](https://www.coze.com/docs/guides/plugin_code?_lang=en)

Additionally, provide a brief explanation of what the API does and include example values for testing key functionalities.

```

## Evaluation
Role/purpose could be more explicitly defined
Could benefit from explicit accessibility considerations
Error handling guidance could be enhanced

## Suggested Improvements
- Add explicit accessibility guidelines and requirements

## Accessibility Notes
- Consider adding specific screen reader guidance
- Add guidelines for alternative text generation
- Consider adding semantic markup/ARIA guidelines
