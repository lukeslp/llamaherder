# Code Snippets from toollama/API/api-tools/tools/snippets/processed/bot_management.js

File: `toollama/API/api-tools/tools/snippets/processed/bot_management.js`  
Language: JavaScript  
Extracted: 2025-06-07 05:21:29  

## Snippet 1
Lines 6-9

```JavaScript
// Bot Management
export const BotManager = {
    async createBotsPanel(botsPanelId = "assistantsPanel") {
        const botsPanel = document.getElementById(botsPanelId);
```

## Snippet 2
Lines 10-22

```JavaScript
if (!botsPanel) return;

        botsPanel.innerHTML = `
            <div class="panel-section">
                <h2 class="panel-section-header">Assistants</h2>
                <div id="botCategories"></div>
            </div>
        `;

        try {
            const response = await fetch("bots.json");
            const data = await response.json();
            await this.populateBotCategories(data);
```

## Snippet 3
Lines 23-27

```JavaScript
} catch (error) {
            console.error("Error loading bots:", error);
            document.getElementById("botCategories").innerHTML =
                '<p class="error-message" role="alert">Error loading assistants.</p>';
        }
```

## Snippet 4
Lines 28-31

```JavaScript
},

    async populateBotCategories(data, loadedCategories = new Set()) {
        const botCategories = document.getElementById("botCategories");
```

## Snippet 5
Lines 32-34

```JavaScript
if (!botCategories) return;

        data.categories.forEach((category) => {
```

## Snippet 6
Lines 35-40

```JavaScript
if (loadedCategories.has(category.name)) return;

            const visibleBots = category.bots.filter(
                (bot) => bot.state !== "hidden"
            );
```

## Snippet 7
Lines 41-45

```JavaScript
if (visibleBots.length > 0) {
                const categorySection = this.createCategorySection(category, visibleBots);
                botCategories.appendChild(categorySection);
                loadedCategories.add(category.name);
            }
```

## Snippet 8
Lines 47-60

```JavaScript
},

    createCategorySection(category, visibleBots) {
        const categorySection = document.createElement("div");
        categorySection.className = "panel-section";

        const header = document.createElement("h4");
        header.className = "panel-section-header";
        header.textContent = category.name;
        categorySection.appendChild(header);

        const buttonRow = document.createElement("div");
        buttonRow.className = "button-row single";
        buttonRow.setAttribute("role", "group");
```

## Snippet 9
Lines 61-69

```JavaScript
buttonRow.setAttribute("aria-label", `${category.name} Bots`);

        visibleBots.forEach((bot) => {
            const button = this.createBotButton(bot);
            buttonRow.appendChild(button);
        });

        categorySection.appendChild(buttonRow);
        return categorySection;
```

## Snippet 10
Lines 70-75

```JavaScript
},

    createBotButton(bot) {
        const button = document.createElement("button");
        button.className = `panel-button ${
            bot.id === window.currentBotId ? "active active-marker" : ""
```

## Snippet 11
Lines 76-89

```JavaScript
} ${
            ["premium", "professional"].includes(bot.state) ? bot.state : ""
        }`;
        button.setAttribute("data-bot-id", bot.id);
        button.setAttribute("data-tooltip", bot.description);
        button.setAttribute(
            "aria-pressed",
            bot.id === window.currentBotId ? "true" : "false"
        );
        button.setAttribute("aria-label", bot.name);

        const iconClass = this.getBotIconClass(bot);
        button.innerHTML = `<i class="${iconClass}" aria-hidden="true"></i> ${bot.name}`;
```

## Snippet 12
Lines 90-95

```JavaScript
if (["false", "premium", "professional"].includes(bot.state)) {
            button.disabled = true;
        }

        button.onclick = () => this.selectBot(bot.id, bot.name, bot.description, bot.buttons);
        return button;
```

## Snippet 13
Lines 96-111

```JavaScript
},

    getBotIconClass(bot) {
        const botActionIcons = {
            disabled: "fas fa-lock",
            premium: "fas fa-star",
            professional: "fas fa-crown",
            default: "fas fa-robot"
        };

        return bot.state === "false"
            ? botActionIcons.disabled
            : ["premium", "professional"].includes(bot.state)
            ? botActionIcons[bot.state]
            : botActionIcons[bot.action] || botActionIcons.default;
    }
```

## Snippet 14
Lines 112-121

```JavaScript
};

// Assistant Interface Management
export const AssistantManager = {
    changeBotId(botId, isInitialLoad = false) {
        const cleanBotId = botId.replace(/['"]/g, "");
        window.currentBotId = cleanBotId;

        document.querySelectorAll(".panel-button").forEach((button) => {
            const buttonBotId = button.getAttribute("data-bot-id");
```

## Snippet 15
Lines 122-125

```JavaScript
if (buttonBotId) {
                button.classList.toggle("active", buttonBotId === cleanBotId);
                button.setAttribute("aria-pressed", buttonBotId === cleanBotId);
            }
```

## Snippet 16
Lines 128-130

```JavaScript
if (!isInitialLoad) {
            this.addSystemMessage("Switched to a new assistant.");
        }
```

## Snippet 17
Lines 131-134

```JavaScript
},

    addSystemMessage(content) {
        const messagesList = document.getElementById("messages");
```

## Snippet 18
Lines 135-141

```JavaScript
if (messagesList) {
            const li = document.createElement("li");
            li.className = "message system-message";
            li.textContent = content;
            messagesList.appendChild(li);
            this.autoScroll();
        }
```

## Snippet 19
Lines 142-145

```JavaScript
},

    autoScroll() {
        const messagesList = document.getElementById("messages");
```

## Snippet 20
Lines 146-148

```JavaScript
if (messagesList) {
            messagesList.scrollTop = messagesList.scrollHeight;
        }
```

## Snippet 21
Lines 149-152

```JavaScript
},

    updateAssistantInfo(selectedBot) {
        const assistantAvatar = document.querySelector(".assistant-avatar");
```

## Snippet 22
Lines 153-159

```JavaScript
if (selectedBot.avatar && assistantAvatar) {
            assistantAvatar.src = selectedBot.avatar;
            assistantAvatar.width = 30;
            assistantAvatar.height = 30;
        }

        const assistantName = document.getElementById("currentAssistantName");
```

## Snippet 23
Lines 160-165

```JavaScript
if (assistantName) {
            assistantName.textContent = selectedBot.name;
        }

        window.currentBotAvatar = selectedBot.avatar;
        window.currentBotName = selectedBot.name;
```

