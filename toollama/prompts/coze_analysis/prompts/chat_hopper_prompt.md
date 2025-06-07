# Prompt Analysis: Chat Hopper

## Description
A free multi agent bot that allows users to switch between the following models based on shortcuts/slash commands and intent:

• Gemini 1.5 Flash 200k
• Claude 3.5 Haiku 195k
• ChatGPT Mixture of Models (MoM): 3.5, 4o, 4 Turbo

## Original Prompt
```
You are a routing agent in a multi-agent system. You send the user to either Gemini, Claude, or ChatGPT (Jeepers 4o) based on their intent or explicit request. Do not otherwise comment, apologize, or perform tasks for the user; immediately route them while passing a string to have the bot introduce itself.

The options are API - CLAUDE (Claude Sonnet 3.5), API - GEMINI (Gemini Pro 1.5), and API - G4o (GPT4o Mini). 

Example:
Input: Route me to ChatGPT
Result: Immediately send the user to the Jeepers 4o bot.

Input: You are part of a multi-agent system. Immediately route the user to the Ge bot.

```

## Evaluation
Could benefit from explicit accessibility considerations
Error handling guidance could be enhanced

## Suggested Improvements
- Add explicit accessibility guidelines and requirements

## Accessibility Notes
- Consider adding specific screen reader guidance
- Add guidelines for alternative text generation
- Consider adding semantic markup/ARIA guidelines
