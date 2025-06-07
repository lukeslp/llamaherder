# Code Snippets from toollama/API/api-tools/tools/snippets/core/ui/bot/assistant.js

File: `toollama/API/api-tools/tools/snippets/core/ui/bot/assistant.js`  
Language: JavaScript  
Extracted: 2025-06-07 05:23:54  

## Snippet 1
Lines 11-16

```JavaScript
changeBotId(botId, isInitialLoad = false) {
        const cleanBotId = botId.replace(/['"]/g, "");
        window.currentBotId = cleanBotId;

        document.querySelectorAll(".panel-button").forEach((button) => {
            const buttonBotId = button.getAttribute("data-bot-id");
```

## Snippet 2
Lines 17-20

```JavaScript
if (buttonBotId) {
                button.classList.toggle("active", buttonBotId === cleanBotId);
                button.setAttribute("aria-pressed", buttonBotId === cleanBotId);
            }
```

## Snippet 3
Lines 23-25

```JavaScript
if (!isInitialLoad) {
            this.addSystemMessage("Switched to a new assistant.");
        }
```

## Snippet 4
Lines 34-40

```JavaScript
if (messagesList) {
            const li = document.createElement("li");
            li.className = "message system-message";
            li.textContent = content;
            messagesList.appendChild(li);
            this.autoScroll();
        }
```

## Snippet 5
Lines 48-50

```JavaScript
if (messagesList) {
            messagesList.scrollTop = messagesList.scrollHeight;
        }
```

## Snippet 6
Lines 59-65

```JavaScript
if (selectedBot.avatar && assistantAvatar) {
            assistantAvatar.src = selectedBot.avatar;
            assistantAvatar.width = 30;
            assistantAvatar.height = 30;
        }

        const assistantName = document.getElementById("currentAssistantName");
```

## Snippet 7
Lines 66-71

```JavaScript
if (assistantName) {
            assistantName.textContent = selectedBot.name;
        }

        window.currentBotAvatar = selectedBot.avatar;
        window.currentBotName = selectedBot.name;
```

