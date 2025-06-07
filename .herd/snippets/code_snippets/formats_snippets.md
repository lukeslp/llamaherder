# Code Snippets from toollama/API/api-tools/tools/snippets/core/prompts/formats.js

File: `toollama/API/api-tools/tools/snippets/core/prompts/formats.js`  
Language: JavaScript  
Extracted: 2025-06-07 05:23:35  

## Snippet 1
Lines 9-14

```JavaScript
json: {
        standard: '{"type": "string", "content": "string", "metadata": {}}',
        analysis: '{"summary": [], "details": [], "references": []}',
        evaluation: '{"score": "number", "feedback": "string", "suggestions": []}'
    },
```

## Snippet 2
Lines 18-23

```JavaScript
markdown: {
        article: '# Title\n## Summary\n[content]\n## Details\n[content]\n## References\n[content]',
        review: '## Strengths\n[content]\n## Weaknesses\n[content]\n## Suggestions\n[content]',
        analysis: '## Key Points\n[content]\n## Evidence\n[content]\n## Conclusion\n[content]'
    },
```

## Snippet 3
Lines 27-31

```JavaScript
structured: {
        report: 'TITLE:\n[content]\nFINDINGS:\n[content]\nRECOMMENDATIONS:\n[content]',
        feedback: 'POSITIVE:\n[content]\nAREAS FOR IMPROVEMENT:\n[content]\nNEXT STEPS:\n[content]',
        summary: 'OVERVIEW:\n[content]\nDETAILS:\n[content]\nCONCLUSION:\n[content]'
    }
```

