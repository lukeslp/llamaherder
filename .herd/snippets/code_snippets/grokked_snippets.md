# Code Snippets from toollama/API/--storage/grokked.html

File: `toollama/API/--storage/grokked.html`  
Language: HTML  
Extracted: 2025-06-07 05:17:04  

## Snippet 1
Lines 1-6

```HTML
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Grok Debates Elon Musk</title>
```

## Snippet 2
Lines 7-179

```HTML
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Open+Sans:wght@400;700&display=swap">
  <script src="https://cdn.jsdelivr.net/npm/marked/marked.min.js"></script>
  <style>
    :root {
      --bg-color: #000000;
      --text-color: #ffffff;
      --accent-color: #00ff00;
      --secondary-color: #333333;
      --input-bg: #1a1a1a;
      --step-inactive: #444444;
      --step-active: var(--accent-color);
      --step-complete: #00cc00;
      --thought-color: #0858ae;
      --fanboy-color: #e74c3c;
      --hater-color: #8e44ad;
      --judge-color: #27ae60;
    }

    * {
      margin: 0;
      padding: 0;
      box-sizing: border-box;
    }

    body {
      background-color: var(--bg-color);
      color: var(--text-color);
      font-family: 'Open Sans', sans-serif;
      min-height: 100vh;
      display: flex;
      flex-direction: column;
      align-items: center;
    }

    .container {
      width: 100%;
      max-width: 1000px;
      padding: 20px;
    }

    header {
      text-align: center;
      margin-bottom: 2rem;
    }

    h1 {
      color: var(--accent-color);
      font-size: 2.5rem;
      margin: 1rem 0;
    }

    .debate-info {
      font-style: italic;
      color: var(--text-color);
      opacity: 0.7;
      margin-bottom: 1.5rem;
    }

    .random-news-btn {
      padding: 0.75rem 1.5rem;
      background-color: var(--accent-color);
      color: var(--bg-color);
      border: none;
      border-radius: 4px;
      font-family: inherit;
      font-size: 1rem;
      cursor: pointer;
      margin-bottom: 1.5rem;
      transition: all 0.3s ease;
    }

    .random-news-btn:hover {
      background-color: var(--step-complete);
    }

    .scorecard {
      display: flex;
      justify-content: center;
      gap: 4rem;
      background: var(--input-bg);
      padding: 1rem;
      border-radius: 8px;
      margin: 1rem 0;
      box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
    }

    .score {
      text-align: center;
    }

    .score-name {
      font-weight: bold;
      margin-bottom: 0.5rem;
    }

    .score-points {
      font-size: 1.5rem;
      font-weight: bold;
    }

    .fanboy-score {
      color: var(--fanboy-color);
    }

    .hater-score {
      color: var(--hater-color);
    }

    form {
      margin-bottom: 2rem;
      text-align: center;
    }

    textarea {
      width: 90%;
      height: 80px;
      margin-bottom: 0.5rem;
      font-size: 1rem;
      padding: 1rem;
      border: 2px solid var(--secondary-color);
      border-radius: 4px;
      background-color: var(--input-bg);
      color: var(--text-color);
      font-family: inherit;
      transition: all 0.3s ease;
    }

    textarea:focus {
      outline: none;
      border-color: var(--accent-color);
      box-shadow: 0 0 10px rgba(0, 255, 0, 0.2);
    }

    button {
      padding: 0.75rem 1.5rem;
      background-color: var(--accent-color);
      color: var(--bg-color);
      border: none;
      border-radius: 4px;
      font-family: inherit;
      font-size: 1rem;
      cursor: pointer;
      transition: all 0.3s ease;
    }

    button:hover {
      background-color: var(--step-complete);
    }

    button:disabled {
      background-color: var(--step-inactive);
      cursor: not-allowed;
    }

    .status {
      text-align: center;
      font-style: italic;
      color: var(--accent-color);
      margin: 1rem 0;
    }

    .loading {
      display: inline-block;
      width: 16px;
      height: 16px;
      border: 3px solid rgba(0, 255, 0, 0.2);
      border-radius: 50%;
      border-top-color: var(--accent-color);
      animation: spin 1s ease-in-out infinite;
      margin-left: 10px;
      vertical-align: middle;
    }
```

## Snippet 3
Lines 182-192

```HTML
}

    .topic {
      background: var(--input-bg);
      border-radius: 8px;
      padding: 1rem;
      margin: 1rem 0;
      text-align: center;
      border-left: 3px solid var(--accent-color);
    }
```

## Snippet 4
Lines 193-197

```HTML
/* Debate container styling */
    .debate-container {
      margin: 1.5rem 0;
    }
```

## Snippet 5
Lines 199-210

```HTML
@media (min-width: 768px) {
      .debate-exchange {
        display: flex;
        gap: 2rem;
        margin-bottom: 1rem;
      }

      .debate-exchange .message {
        flex: 1;
      }
    }
```

## Snippet 6
Lines 212-330

```HTML
@media (max-width: 767px) {
      .debate-exchange {
        display: flex;
        flex-direction: column;
        gap: 1rem;
        margin-bottom: 1rem;
      }
    }

    .message {
      position: relative;
      padding: 1rem;
      margin-bottom: 1rem;
      border-radius: 12px;
      max-width: 100%;
      color: var(--text-color);
    }

    .message strong {
      display: block;
      margin-bottom: 0.5rem;
      color: inherit;
      font-weight: bold;
    }

    .message.topic {
      background-color: var(--input-bg);
      color: var(--accent-color);
    }

    .message.fanboy {
      background-color: rgba(231, 76, 60, 0.2);
      border-left: none;
      align-self: flex-start;
      margin-right: 10%;
      border-top-left-radius: 0;
    }

    .message.fanboy::before {
      content: '';
      position: absolute;
      top: 0;
      left: -10px;
      width: 0;
      height: 0;
      border-top: 10px solid transparent;
      border-bottom: 10px solid transparent;
      border-right: 10px solid rgba(231, 76, 60, 0.2);
    }

    .message.hater {
      background-color: rgba(142, 68, 173, 0.2);
      border-left: none;
      align-self: flex-end;
      margin-left: 10%;
      border-top-right-radius: 0;
    }

    .message.hater::before {
      content: '';
      position: absolute;
      top: 0;
      right: -10px;
      width: 0;
      height: 0;
      border-top: 10px solid transparent;
      border-bottom: 10px solid transparent;
      border-left: 10px solid rgba(142, 68, 173, 0.2);
    }

    .message.judge {
      background-color: rgba(39, 174, 96, 0.2);
      border-left: 3px solid var(--judge-color);
      margin: 1.5rem auto;
      max-width: 90%;
    }

    .markdown-content a {
      color: var(--accent-color);
      text-decoration: none;
    }

    .markdown-content a:hover {
      text-decoration: underline;
    }

    .markdown-content ul, .markdown-content ol {
      margin-left: 1.5rem;
      margin-bottom: 1rem;
    }

    .markdown-content p {
      margin-bottom: 0.75rem;
    }

    .markdown-content h1, .markdown-content h2, .markdown-content h3 {
      margin: 0.75rem 0;
      color: inherit;
    }

    .markdown-content img {
      max-width: 100%;
      height: auto;
    }

    .markdown-content code {
      background-color: rgba(255, 255, 255, 0.1);
      padding: 0.1rem 0.3rem;
      border-radius: 3px;
    }

    .markdown-content pre {
      background-color: rgba(0, 0, 0, 0.3);
      padding: 0.5rem;
      border-radius: 4px;
      overflow-x: auto;
      margin-bottom: 1rem;
    }
```

## Snippet 7
Lines 331-369

```HTML
/* News modal */
    .modal {
      display: none;
      position: fixed;
      z-index: 1000;
      left: 0;
      top: 0;
      width: 100%;
      height: 100%;
      background-color: rgba(0, 0, 0, 0.8);
      overflow: auto;
    }

    .modal-content {
      background-color: var(--input-bg);
      margin: 10% auto;
      padding: 2rem;
      border-radius: 8px;
      max-width: 800px;
      position: relative;
      animation: fadeIn 0.3s;
      border-left: 3px solid var(--accent-color);
    }

    .close-modal {
      position: absolute;
      top: 10px;
      right: 20px;
      color: var(--text-color);
      font-size: 28px;
      font-weight: bold;
      cursor: pointer;
    }

    .modal-title {
      color: var(--accent-color);
      margin-bottom: 1rem;
    }
```

## Snippet 8
Lines 370-451

```HTML
/* User chat section */
    .user-chat-container {
      width: 100%;
      margin: 2rem 0;
      border-top: 1px solid var(--secondary-color);
      padding-top: 1.5rem;
    }

    .user-chat-title {
      text-align: center;
      margin-bottom: 1rem;
      color: var(--accent-color);
      font-size: 1.2rem;
    }

    .user-chat {
      background-color: var(--input-bg);
      border-radius: 8px;
      padding: 1rem;
      margin-bottom: 1rem;
    }

    .user-message {
      background-color: rgba(52, 152, 219, 0.2);
      border-left: none;
      align-self: flex-end;
      margin-left: 20%;
      border-top-right-radius: 0;
      position: relative;
      padding: 1rem;
      margin-bottom: 1rem;
      border-radius: 12px;
    }

    .user-message::before {
      content: '';
      position: absolute;
      top: 0;
      right: -10px;
      width: 0;
      height: 0;
      border-top: 10px solid transparent;
      border-bottom: 10px solid transparent;
      border-left: 10px solid rgba(52, 152, 219, 0.2);
    }

    .user-input-container {
      display: flex;
      margin-top: 1rem;
    }

    .user-input {
      flex: 1;
      padding: 0.75rem;
      border: 2px solid var(--secondary-color);
      border-radius: 4px 0 0 4px;
      background-color: var(--input-bg);
      color: var(--text-color);
      font-family: inherit;
    }

    .user-input:focus {
      outline: none;
      border-color: var(--accent-color);
    }

    .send-button {
      padding: 0.75rem 1.5rem;
      background-color: var(--accent-color);
      color: var(--bg-color);
      border: none;
      border-radius: 0 4px 4px 0;
      cursor: pointer;
    }

    .control-buttons {
      display: flex;
      justify-content: center;
      gap: 1rem;
      margin: 1.5rem 0;
    }
```

## Snippet 9
Lines 457-518

```HTML
</head>
<body>
  <div class="container">
    <header>
      <h1>Elon Musk Debate Arena</h1>
      <p class="debate-info">Watch two Grok personalities with distinctive styles argue about Elon Musk based on your topic.
        After 6 exchanges, a judge will determine the winner.</p>
      <button id="randomNewsBtn" class="random-news-btn">Get Random Elon News</button>
    </header>

    <div class="scorecard">
      <div class="score">
        <div class="score-name fanboy-score">Elon Fanboy</div>
        <div class="score-points fanboy-score" id="fanboyScore">0</div>
      </div>
      <div class="score">
        <div class="score-name hater-score">Elon Hater</div>
        <div class="score-points hater-score" id="haterScore">0</div>
      </div>
    </div>

  <form id="elonForm">
      <textarea id="elonInput" placeholder="Enter a topic about Elon Musk (e.g., 'Twitter acquisition', 'Tesla stock', 'SpaceX launch')..." required></textarea><br>
      <button type="submit" id="submitButton">Start Debate</button>
  </form>

    <div id="statusBar" class="status" style="display: none;">
      Groks are debating... <span class="loading"></span>
    </div>

    <div id="conversation" class="debate-container"></div>

    <div class="user-chat-container">
      <h3 class="user-chat-title">or tell them what you think</h3>
      <div id="userChat" class="user-chat"></div>
      <div class="user-input-container">
        <input type="text" id="userMessageInput" class="user-input" placeholder="Enter your message...">
        <button id="sendUserMessage" class="send-button">Send</button>
      </div>
    </div>

    <div class="control-buttons">
      <button id="clearDebateBtn">Clear Debate History</button>
      <button id="resetScoresBtn">Reset Scores</button>
    </div>
  </div>

  <!-- News Modal -->
  <div id="newsModal" class="modal">
    <div class="modal-content">
      <span class="close-modal">&times;</span>
      <h2 class="modal-title">Latest Elon Musk News</h2>
      <div id="newsContent" class="markdown-content"></div>
    </div>
  </div>

  <script>
    // API endpoint
    const API_BASE_URL = 'https://api.assisted.space/v2';

    // Store conversation history and scores in local storage
    let messages = [];
```

## Snippet 10
Lines 519-533

```HTML
let scores = { fanboy: 0, hater: 0 };
    let userMessages = [];

    // DOM elements
    const modal = document.getElementById('newsModal');
    const modalClose = document.querySelector('.close-modal');
    const randomNewsBtn = document.getElementById('randomNewsBtn');
    const newsContent = document.getElementById('newsContent');
    const userMessageInput = document.getElementById('userMessageInput');
    const sendUserMessageBtn = document.getElementById('sendUserMessage');
    const userChatContainer = document.getElementById('userChat');
    const clearDebateBtn = document.getElementById('clearDebateBtn');
    const resetScoresBtn = document.getElementById('resetScoresBtn');

    // Load conversation from localStorage on page load
```

## Snippet 11
Lines 536-539

```HTML
if (savedMessages) {
        try {
          messages = JSON.parse(savedMessages);
          displayMessages();
```

## Snippet 12
Lines 540-543

```HTML
} catch (err) {
          console.error("Error parsing saved messages:", err);
          messages = [];
        }
```

## Snippet 13
Lines 544-546

```HTML
}

      const savedScores = localStorage.getItem('grokScores');
```

## Snippet 14
Lines 547-550

```HTML
if (savedScores) {
        try {
          scores = JSON.parse(savedScores);
          updateScoreboard();
```

## Snippet 15
Lines 555-557

```HTML
}

      const savedUserMessages = localStorage.getItem('userMessages');
```

## Snippet 16
Lines 558-561

```HTML
if (savedUserMessages) {
        try {
          userMessages = JSON.parse(savedUserMessages);
          displayUserMessages();
```

## Snippet 17
Lines 562-565

```HTML
} catch (err) {
          console.error("Error parsing saved user messages:", err);
          userMessages = [];
        }
```

## Snippet 18
Lines 570-574

```HTML
function saveMessages() {
      localStorage.setItem('grokMessages', JSON.stringify(messages));
    }

    // Save scores to localStorage
```

## Snippet 19
Lines 575-579

```HTML
function saveScores() {
      localStorage.setItem('grokScores', JSON.stringify(scores));
    }

    // Save user messages to localStorage
```

## Snippet 20
Lines 580-584

```HTML
function saveUserMessages() {
      localStorage.setItem('userMessages', JSON.stringify(userMessages));
    }

    // Update the scoreboard display
```

## Snippet 21
Lines 585-590

```HTML
function updateScoreboard() {
      document.getElementById('fanboyScore').textContent = scores.fanboy;
      document.getElementById('haterScore').textContent = scores.hater;
    }

    // Display all messages in the conversation div
```

## Snippet 22
Lines 591-599

```HTML
function displayMessages() {
        const convDiv = document.getElementById('conversation');
        convDiv.innerHTML = '';

      // Group fanboy and hater messages that come after each other
      let currentExchange = null;
      let currentExchangeDiv = null;

      messages.forEach((msg, index) => {
```

## Snippet 23
Lines 600-608

```HTML
if (msg.role === 'Topic') {
          // Create a topic message
          const topicDiv = document.createElement('div');
          topicDiv.className = 'message topic';
          topicDiv.innerHTML = `<strong>${msg.role}:</strong> ${msg.text}`;
          convDiv.appendChild(topicDiv);
          // Reset the current exchange
          currentExchange = null;
          currentExchangeDiv = null;
```

## Snippet 24
Lines 609-617

```HTML
} else if (msg.role === 'Judge') {
          // Create a judge message
          const judgeDiv = document.createElement('div');
          judgeDiv.className = 'message judge';
          judgeDiv.innerHTML = `<strong>${msg.role}:</strong> <div class="markdown-content">${marked.parse(msg.text)}</div>`;
          convDiv.appendChild(judgeDiv);
          // Reset the current exchange
          currentExchange = null;
          currentExchangeDiv = null;
```

## Snippet 25
Lines 621-633

```HTML
if (currentExchange !== index - 1 ||
              (messages[index-1] && messages[index-1].role !== 'Elon Fanboy' && messages[index-1].role !== 'Elon Hater')) {
            // Create a new exchange div
            currentExchangeDiv = document.createElement('div');
            currentExchangeDiv.className = 'debate-exchange';
            convDiv.appendChild(currentExchangeDiv);
          }

          // Add the message to the current exchange
          const msgDiv = document.createElement('div');
          msgDiv.className = `message ${msg.role.toLowerCase().replace(' ', '-')}`;
          msgDiv.innerHTML = `<strong>${msg.role}:</strong> <div class="markdown-content">${marked.parse(msg.text)}</div>`;
```

## Snippet 26
Lines 646-650

```HTML
function displayUserMessages() {
      userChatContainer.innerHTML = '';

      userMessages.forEach(msg => {
        const msgDiv = document.createElement('div');
```

## Snippet 27
Lines 651-653

```HTML
if (msg.role === 'User') {
          msgDiv.className = 'user-message';
          msgDiv.innerHTML = `<strong>You:</strong> ${msg.text}`;
```

## Snippet 28
Lines 654-659

```HTML
} else {
          // For responses from either fanboy or hater
          msgDiv.className = `message ${msg.role.toLowerCase().replace(' ', '-')}`;
          msgDiv.innerHTML = `<strong>${msg.role}:</strong> <div class="markdown-content">${marked.parse(msg.text)}</div>`;
        }
        userChatContainer.appendChild(msgDiv);
```

## Snippet 29
Lines 678-684

```HTML
function clearConversation() {
      messages = [];
      saveMessages();
      displayMessages();
    }

    // Clear user chat history
```

## Snippet 30
Lines 685-691

```HTML
function clearUserChat() {
      userMessages = [];
      saveUserMessages();
      displayUserMessages();
    }

    // Clear score history
```

## Snippet 31
Lines 693-695

```HTML
scores = { fanboy: 0, hater: 0 };
      saveScores();
      updateScoreboard();
```

## Snippet 32
Lines 699-718

```HTML
async function getRandomElonNews() {
      const topics = [
        "Elon Musk's latest Tesla announcement",
        "Elon Musk SpaceX recent launch",
        "Elon Musk Twitter X controversy",
        "Elon Musk Neuralink progress",
        "Elon Musk Boring Company updates",
        "Elon Musk AI statements",
        "Elon Musk recent interviews",
        "Elon Musk SEC disputes",
        "Elon Musk political statements"
      ];

      const randomTopic = topics[Math.floor(Math.random() * topics.length)];
      modal.style.display = "block";
      newsContent.innerHTML = "Loading latest news...";

      try {
        const requestData = {
          model: "perplexity",
```

## Snippet 33
Lines 719-722

```HTML
prompt: `Provide a brief summary of the most recent news about ${randomTopic} within the last month. Include only verified information from reliable sources. Format your response in markdown with proper headings, bullet points, and emphasis where appropriate. Keep it concise.`,
          max_tokens: 2048,
          stream: false,
          temperature: 0.7
```

## Snippet 34
Lines 723-732

```HTML
};

        const response = await fetch(`${API_BASE_URL}/chat/perplexity`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify(requestData)
        });
```

## Snippet 35
Lines 733-739

```HTML
if (!response.ok) {
          throw new Error(`HTTP error ${response.status}`);
        }

        const data = await response.json();
        let content = '';
```

## Snippet 36
Lines 749-752

```HTML
} catch (error) {
        console.error("Error fetching Elon news:", error);
        newsContent.innerHTML = `Error fetching news: ${error.message}. Please try again.`;
      }
```

## Snippet 37
Lines 753-761

```HTML
}

    // Load saved conversation on page load
    loadConversation();

    // Handle debate form submission
    document.getElementById('elonForm').addEventListener('submit', async (e) => {
      e.preventDefault();
      const userInput = document.getElementById('elonInput').value.trim();
```

## Snippet 38
Lines 762-774

```HTML
if (!userInput) return;

      // Disable the submit button and show status bar
      const submitButton = document.getElementById('submitButton');
      submitButton.disabled = true;
      document.getElementById('statusBar').style.display = 'block';

      // Add topic message
      addMessage('Topic', userInput);

      try {
        // Create prompts with distinct personality characteristics
        const fanBoyPrompt = `You are an EXTREMELY PASSIONATE Elon Musk fanboy who uses internet slang, emojis, and profanity. Your communication style:
```

## Snippet 39
Lines 775-785

```HTML
- Use ALL CAPS for emphasis
        - Short, punchy sentences
        - Lots of !!!!! and ?????
        - Use emojis and internet speak (ur, u, lol, omg)
        - Be aggressive and mock the hater
        - Use made-up statistics that sound impressive
        - Refer to Elon as a genius/savior/messiah

        Topic: ${userInput}

        KEEP YOUR RESPONSE BRIEF - MAXIMUM 150 WORDS!
```

## Snippet 40
Lines 786-800

```HTML
Format your response with markdown for emphasis.
        BE EXTREMELY DIFFERENT FROM THE HATER IN YOUR STYLE - YOU'RE LOUD, OBNOXIOUS, AND PASSIONATE!`;

        const haterPrompt = `You are a sophisticated, condescending Elon Musk critic who despises him. Your communication style:
        - Use elevated vocabulary and complex sentence structures
        - Employ sarcasm and subtle mockery
        - Reference academic concepts and literature
        - Use numbered points and structured arguments
        - Maintain perfect grammar and punctuation
        - Refer to Musk as "Mr. Musk" or "the so-called genius"
        - Include precise dates and figures in your criticism

        Topic: ${userInput}

        KEEP YOUR RESPONSE BRIEF - MAXIMUM 150 WORDS!
```

## Snippet 41
Lines 801-867

```HTML
Format your response with markdown for emphasis.
        BE EXTREMELY DIFFERENT FROM THE FANBOY IN YOUR STYLE - YOU'RE CALCULATED, INTELLECTUAL, AND COLDLY DISMISSIVE!`;

        let fullDebate = "";

        // First turn
        const fanBoyResponse1 = await callXaiApi(fanBoyPrompt);
        addMessage('Elon Fanboy', fanBoyResponse1);
        fullDebate += "Fanboy: " + fanBoyResponse1 + "\n\n";

        const haterResponse1 = await callXaiApi(`${haterPrompt}

        Respond directly to this childish argument: "${fanBoyResponse1}"

        KEEP YOUR RESPONSE BRIEF - MAXIMUM 150 WORDS!`);
        addMessage('Elon Hater', haterResponse1);
        fullDebate += "Hater: " + haterResponse1 + "\n\n";

        // Second turn
        const fanBoyResponse2 = await callXaiApi(`${fanBoyPrompt}

        RESPOND DIRECTLY to this pretentious hater: "${haterResponse1}"

        BE EVEN MORE AGGRESSIVE AND CHILDISH! KEEP YOUR RESPONSE BRIEF - MAXIMUM 150 WORDS!`);
        addMessage('Elon Fanboy', fanBoyResponse2);
        fullDebate += "Fanboy: " + fanBoyResponse2 + "\n\n";

        const haterResponse2 = await callXaiApi(`${haterPrompt}

        Respond with increasing intellectual disdain to this juvenile retort: "${fanBoyResponse2}"

        Be even more formal and structured. KEEP YOUR RESPONSE BRIEF - MAXIMUM 150 WORDS!`);
        addMessage('Elon Hater', haterResponse2);
        fullDebate += "Hater: " + haterResponse2 + "\n\n";

        // Third turn
        const fanBoyResponse3 = await callXaiApi(`${fanBoyPrompt}

        THIS IS YOUR FINAL ARGUMENT! Respond to this stuck-up hater with maximum passion and aggression: "${haterResponse2}"

        GO ALL OUT WITH CAPS, EMOJIS, AND WILD CLAIMS ABOUT ELON'S GREATNESS!!!
        KEEP YOUR RESPONSE BRIEF - MAXIMUM 150 WORDS!`);
        addMessage('Elon Fanboy', fanBoyResponse3);
        fullDebate += "Fanboy: " + fanBoyResponse3 + "\n\n";

        const haterResponse3 = await callXaiApi(`${haterPrompt}

        This is your final devastating rebuttal. Deliver the most eloquent and scathing critique possible in response to: "${fanBoyResponse3}"

        End with a particularly withering remark. KEEP YOUR RESPONSE BRIEF - MAXIMUM 150 WORDS!`);
        addMessage('Elon Hater', haterResponse3);
        fullDebate += "Hater: " + haterResponse3 + "\n\n";

        // Judge evaluates the debate
        const judgePrompt = `You are an impartial debate judge evaluating a heated exchange about Elon Musk on the topic: "${userInput}".

        The full debate transcript is as follows:

        ${fullDebate}

        Evaluate the arguments made by both sides concisely. Consider:
        1. Quality of reasoning and evidence
        2. Persuasiveness and rhetorical effectiveness
        3. Responsiveness to opponent's arguments
        4. Overall presentation

        Keep your evaluation brief and concise (maximum 250 words).
```

## Snippet 42
Lines 868-875

```HTML
Format your response with markdown for emphasis and structure.
        Declare either "Elon Fanboy" or "Elon Hater" as the winner of this round.
        End with "WINNER: [Elon Fanboy/Elon Hater]" on a separate line.`;

        const judgeResponse = await callXaiApi(judgePrompt);

        // Extract winner from judge response
        let winner = "";
```

## Snippet 43
Lines 876-878

```HTML
if (judgeResponse.includes("WINNER: Elon Fanboy")) {
          winner = "fanboy";
          scores.fanboy += 1;
```

## Snippet 44
Lines 879-890

```HTML
} else if (judgeResponse.includes("WINNER: Elon Hater")) {
          winner = "hater";
          scores.hater += 1;
        }

        // Update and save scores
        saveScores();
        updateScoreboard();

        // Add judge's response
        addMessage('Judge', judgeResponse);
```

## Snippet 45
Lines 891-893

```HTML
} catch (error) {
        console.error("Error getting responses:", error);
        addMessage('System', `Error: ${error.message}`);
```

## Snippet 46
Lines 894-900

```HTML
} finally {
        // Re-enable the submit button and hide status bar
        submitButton.disabled = false;
        document.getElementById('statusBar').style.display = 'none';
        // Clear the input field
        document.getElementById('elonInput').value = '';
      }
```

## Snippet 47
Lines 901-905

```HTML
});

    // Handle user message submission
    sendUserMessageBtn.addEventListener('click', async () => {
      const userMessage = userMessageInput.value.trim();
```

## Snippet 48
Lines 906-916

```HTML
if (!userMessage) return;

      // Add user message to chat
      addUserMessage('User', userMessage);
      userMessageInput.value = '';

      try {
        // Get response from either fanboy or hater (randomly)
        const respondent = Math.random() < 0.5 ? 'Elon Fanboy' : 'Elon Hater';

        let prompt = '';
```

## Snippet 49
Lines 917-922

```HTML
if (respondent === 'Elon Fanboy') {
          prompt = `You are an EXTREMELY PASSIONATE Elon Musk fanboy who uses internet slang, emojis, and profanity. Respond to this message about Elon Musk: "${userMessage}"

          Use ALL CAPS, emojis, and be passionate!
          KEEP YOUR RESPONSE BRIEF - MAXIMUM 100 WORDS!
          Format with markdown.`;
```

## Snippet 50
Lines 923-933

```HTML
} else {
          prompt = `You are a sophisticated, condescending Elon Musk critic who despises him. Respond to this message about Elon Musk: "${userMessage}"

          Use elevated vocabulary, structured arguments, and subtle mockery.
          KEEP YOUR RESPONSE BRIEF - MAXIMUM 100 WORDS!
          Format with markdown.`;
        }

        const response = await callXaiApi(prompt);
        addUserMessage(respondent, response);
```

## Snippet 51
Lines 934-937

```HTML
} catch (error) {
        console.error("Error getting response:", error);
        addUserMessage('System', `Error: ${error.message}`);
      }
```

## Snippet 52
Lines 943-947

```HTML
// Create request payload for the X.AI API
        const requestData = {
          model: "grok-2-1212",
          prompt: prompt,
          max_tokens: 1024,
```

## Snippet 53
Lines 950-960

```HTML
};

        // Make API request
        const response = await fetch(`${API_BASE_URL}/chat/xai`, {
            method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify(requestData)
        });
```

## Snippet 54
Lines 962-966

```HTML
if (!response.ok) {
          let errorText = await response.text();
          try {
            const errorJson = JSON.parse(errorText);
            throw new Error(errorJson.error || `HTTP error ${response.status}`);
```

## Snippet 55
Lines 967-969

```HTML
} catch (e) {
            throw new Error(`HTTP error ${response.status}: ${errorText}`);
          }
```

## Snippet 56
Lines 970-975

```HTML
}

        // Parse response
        const data = await response.json();

        // Extract content from response (handle different response formats)
```

## Snippet 57
Lines 980-982

```HTML
} else {
          return JSON.stringify(data);
        }
```

## Snippet 58
Lines 983-986

```HTML
} catch (error) {
        console.error("Error calling X.AI API:", error);
        throw error;
      }
```

## Snippet 59
Lines 995-998

```HTML
if (e.key === 'Enter') {
        e.preventDefault();
        sendUserMessageBtn.click();
      }
```

## Snippet 60
Lines 1001-1008

```HTML
// Set up event listeners for news modal
    randomNewsBtn.addEventListener('click', getRandomElonNews);

    modalClose.addEventListener('click', () => {
      modal.style.display = "none";
    });

    window.addEventListener('click', (e) => {
```

## Snippet 61
Lines 1009-1011

```HTML
if (e.target === modal) {
        modal.style.display = "none";
      }
```

