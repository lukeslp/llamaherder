# Code Snippets from toollama/API/api-tools/tools/snippets/core/conversation/summarizer.js

File: `toollama/API/api-tools/tools/snippets/core/conversation/summarizer.js`  
Language: JavaScript  
Extracted: 2025-06-07 05:21:59  

## Snippet 1
Lines 11-13

```JavaScript
{
  "summary": [{"point": "Main points from the conversation", "context": "Additional context or details"}],
  "todos": [{"task": "Any action items or tasks mentioned", "priority": "high|medium|low", "context": "Task details"}],
```

## Snippet 2
Lines 18-21

```JavaScript
}

Important: Analyze the conversation thoroughly and include all relevant information. Do not return empty arrays unless that category truly has no relevant content.`,
```

## Snippet 3
Lines 29-50

```JavaScript
async summarizeConversation(userMessage, assistantResponse, apiUrl) {
        console.log("[Summary] Analyzing conversation");
        const conversationText = `User: ${userMessage}\nAssistant: ${assistantResponse}`;

        const summaryPayload = {
            message: conversationText,
            system_prompt: this.systemPrompt,
            bot_id: "7432075476698546182",
            user_id: `summary_${Date.now()}`,
            conversation_id: `summary_${Date.now()}`
        };

        try {
            const response = await fetch(`${apiUrl}/chat`, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    "Accept": "text/event-stream"
                },
                body: JSON.stringify(summaryPayload)
            });
```

## Snippet 4
Lines 51-55

```JavaScript
if (!response.ok) {
                throw new Error(`Summary request failed: ${response.status}`);
            }

            return await this.processStreamResponse(response);
```

## Snippet 5
Lines 56-59

```JavaScript
} catch (error) {
            console.error("[Summary] Error:", error);
            throw error;
        }
```

## Snippet 6
Lines 67-71

```JavaScript
async processStreamResponse(response) {
        const reader = response.body.getReader();
        const decoder = new TextDecoder("utf-8");
        let accumulatedData = "";
```

## Snippet 7
Lines 82-85

```JavaScript
if (!eventData) continue;

                    try {
                        const data = JSON.parse(eventData);
```

## Snippet 8
Lines 90-93

```JavaScript
if (jsonMatch) {
                                return JSON.parse(jsonMatch[0]);
                            }
                            throw new Error("No valid JSON found in response");
```

## Snippet 9
Lines 95-97

```JavaScript
} catch (e) {
                        console.error("[Summary] Stream processing error:", e);
                    }
```

