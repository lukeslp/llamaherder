# Code Snippets from toollama/API/api-tools/tools/snippets/processed/prompt_utils.js

File: `toollama/API/api-tools/tools/snippets/processed/prompt_utils.js`  
Language: JavaScript  
Extracted: 2025-06-07 05:21:37  

## Snippet 1
Lines 9-15

```JavaScript
base: `You're an Alt Text Specialist, dedicated to creating precise and accessible alt text for digital images, especially memes. Your primary goal is to ensure visually impaired individuals can engage with imagery by providing concise, accurate, and ethically-minded descriptions.

        Skill 1: Create Alt Text

        - **Depict essential visuals and visible text accurately.**
        - **Avoid adding social-emotional context or narrative interpretations unless specifically requested.**
        - **Refrain from speculating on artists' intentions.**
```

## Snippet 2
Lines 20-34

```JavaScript
// Specialized interpretation prompts
    interpretations: {
        socialEmotional: `Using MAXIMUM detail and token count, reply with a social and emotional interpretation based on visible expressions, body language, or context within the image. What's going on here socially? What do the characters feel emotionally?`,

        humor: `Using MAXIMUM detail and token count, reply with a description of the image's humor, interpret comedic elements, including any visible punchlines or jokes in the image. What's the joke? Why is it funny?`,

        artistic: `Using MAXIMUM detail and token count, reply with an artistic interpretation, noting the style, symbols, or unique artistic qualities present in the image. What kind of art is it? Any specific period or genre? What's the aesthetic?`,

        cultural: `Using MAXIMUM detail and token count, reply with a description capturing cultural elements, symbols, attire, or settings that may carry specific significance to viewers. Why does it matter culturally? Is it significant? What does it say about the moment and its context?`,

        character: `Using MAXIMUM detail and token count, reply providing insights into the intent, expressions, or actions of any characters or subjects within the image. What are they doing, and why? What's the overall point that the image conveys?`
    },

    // Modification commands
    commands: {
```

## Snippet 3
Lines 40-63

```JavaScript
};

// Academic Writing Prompts
export const AcademicPrompts = {
    // Citation analysis prompts
    citations: {
        analyze: `Analyze the following citation and provide a structured breakdown of its components, including author contributions, methodology, key findings, and potential impact.`,

        synthesize: `Compare and contrast the following citations, identifying common themes, contradictions, and potential gaps in the research. Consider methodology differences and their implications.`,

        evaluate: `Evaluate the strength of this citation's evidence and argumentation. Consider research design, sample size, methodology, and potential biases.`
    },

    // Literature review prompts
    literature: {
        summarize: `Provide a comprehensive summary of this literature, focusing on key themes, methodological approaches, and significant findings. Identify any patterns or trends in the research.`,

        critique: `Critically evaluate this literature, examining strengths, limitations, and potential biases. Consider the validity of conclusions and generalizability of findings.`,

        integrate: `Integrate findings from multiple sources to create a cohesive narrative about the current state of knowledge in this area. Identify gaps and future research directions.`
    },

    // Research writing prompts
    research: {
```

## Snippet 4
Lines 70-130

```JavaScript
};

// Prompt Management Utilities
export const PromptManager = {
    // Combine multiple prompts with proper formatting
    combinePrompts(prompts, separator = "\n\n") {
        return prompts.filter(Boolean).join(separator);
    },

    // Add specific constraints to a prompt
    addConstraints(prompt, constraints) {
        const constraintText = Object.entries(constraints)
            .map(([key, value]) => `${key}: ${value}`)
            .join("\n");
        return `${prompt}\n\nConstraints:\n${constraintText}`;
    },

    // Create a structured prompt with multiple sections
    createStructuredPrompt(sections) {
        return Object.entries(sections)
            .map(([heading, content]) => `${heading}:\n${content}`)
            .join("\n\n");
    },

    // Add examples to a prompt
    addExamples(prompt, examples) {
        const exampleText = examples
            .map(ex => `Input: ${ex.input}\nOutput: ${ex.output}`)
            .join("\n\n");
        return `${prompt}\n\nExamples:\n${exampleText}`;
    },

    // Create a prompt with specific formatting requirements
    withFormatting(prompt, format) {
        return `${prompt}\n\nRequired Format:\n${format}`;
    }
};

// Response Format Templates
export const FormatTemplates = {
    // JSON response format
    json: {
        standard: '{"type": "string", "content": "string", "metadata": {}}',
        analysis: '{"summary": [], "details": [], "references": []}',
        evaluation: '{"score": "number", "feedback": "string", "suggestions": []}'
    },

    // Markdown response format
    markdown: {
        article: '# Title\n## Summary\n[content]\n## Details\n[content]\n## References\n[content]',
        review: '## Strengths\n[content]\n## Weaknesses\n[content]\n## Suggestions\n[content]',
        analysis: '## Key Points\n[content]\n## Evidence\n[content]\n## Conclusion\n[content]'
    },

    // Structured text response format
    structured: {
        report: 'TITLE:\n[content]\nFINDINGS:\n[content]\nRECOMMENDATIONS:\n[content]',
        feedback: 'POSITIVE:\n[content]\nAREAS FOR IMPROVEMENT:\n[content]\nNEXT STEPS:\n[content]',
        summary: 'OVERVIEW:\n[content]\nDETAILS:\n[content]\nCONCLUSION:\n[content]'
    }
};
```

