# Tool Analysis: Notion

## Used By Bot: ClinicalGen - PROMISING TWO

## Description
The notion document plugin supports obtaining the content of user documents through the user's authorization to the integration.
1. The plugin caches user tokens for one hour, so currently it takes an hour to change the document authorization scope again.
2. Currently, the plug-in can only access up to 3 levels of content in the document, and cannot have unlimited access to nested content.


## Usage Notes
- Purpose: The notion document plugin supports obtaining the content of user documents through the user's authorization to the integration.
1. The plugin caches user tokens for one hour, so currently it takes an hour to change the document authorization scope again.
2. Currently, the plug-in can only access up to 3 levels of content in the document, and cannot have unlimited access to nested content.
- Accessibility Considerations:
- - Ensure output is screen-reader friendly
- - Include proper error messaging
- - Consider keyboard navigation if applicable
