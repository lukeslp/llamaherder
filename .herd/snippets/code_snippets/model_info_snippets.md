# Code Snippets from toollama/storage/model_info.html

File: `toollama/storage/model_info.html`  
Language: HTML  
Extracted: 2025-06-07 05:11:09  

## Snippet 1
Lines 1-6

```HTML
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Model Summaries • actually useful ai</title>
```

## Snippet 2
Lines 7-82

```HTML
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;700&family=Open+Sans:wght@400;600&display=swap">
  <style>
    :root {
      --color-primary: #1DA1F2;
      --color-surface: rgb(32, 32, 32);
      --color-accent: #2795D9;
      --color-focus: rgba(29, 161, 242, 0.4);
      --color-hover: #2795D9;
      --color-background: rgb(32, 32, 32);
      --color-bg-secondary: rgba(39, 149, 217, 0.1);
      --color-border: #1DA1F2;
      --color-text-primary: #ffffff;
      --color-text-secondary: #9ccaff;
      --color-text-tertiary: #b0e0e6;
      --gradient-border: linear-gradient(135deg,
        #FF0099,
        #1DA1F2,
        #00FF87,
        #1DA1F2,
        #FF0099
      );
      --font-family: 'Open Sans', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    }

    body {
      background: var(--color-background);
      color: var(--color-text-primary);
      font-family: var(--font-family);
      line-height: 1.6;
      margin: 0;
      padding: 20px;
    }

    .container {
      max-width: 800px;
      margin: 0 auto;
      padding: 20px;
      background: var(--color-surface);
      border: 2px solid transparent;
      background:
        linear-gradient(var(--color-surface), var(--color-surface)) padding-box,
        var(--gradient-border) border-box;
      border-radius: 12px;
    }

    h1, h2, h3 {
      font-family: 'Playfair Display', serif;
      color: var(--color-primary);
    }

    h1 {
      text-align: center;
      font-size: 2.5em;
      margin-bottom: 1em;
    }

    h2 {
      font-size: 2em;
      margin-top: 1.5em;
    }

    h3 {
      font-size: 1.5em;
      color: var(--color-text-secondary);
    }

    ul {
      list-style: none;
      padding-left: 0;
    }

    li {
      margin-bottom: 0.5em;
      color: var(--color-text-primary);
    }
```

## Snippet 3
Lines 83-87

```HTML
.best-for {
      color: var(--color-text-secondary);
      font-style: italic;
      margin: 1em 0 2em 0;
    }
```

## Snippet 4
Lines 89-162

```HTML
</head>
<body>
  <div class="container">
    <h1>Model Summaries</h1>

    <h2>Large Foundation Models</h2>

    <h3>Llama 3 Series</h3>
    <ul>
      <li>Llama 3.2 (1B, 3B): Ultra compact and efficient variants</li>
      <li>Llama 3.1 (8B): Mid-size balanced model</li>
      <li>Llama2 Uncensored (7B): Alternative uncensored variant</li>
    </ul>
    <div class="best-for">Best for: General language tasks and reasoning</div>

    <h3>Mistral Series</h3>
    <ul>
      <li>Mistral (7B): Popular base model with strong performance</li>
      <li>Mistral Latest: Optimized version with latest improvements</li>
    </ul>
    <div class="best-for">Best for: General purpose tasks and coding</div>

    <h2>Specialized Models</h2>

    <h3>Vision Models</h3>
    <ul>
      <li>LLaVA (7B): Efficient vision model</li>
      <li>LLaVA-Phi3: Phi-based vision capabilities</li>
      <li>LLaVA-Llama3: Latest Llama3-based vision model</li>
      <li>Llama3.2 Vision (11B): Official Llama vision model</li>
      <li>MiniCPM-V: Efficient vision processing</li>
      <li>Moondream: Edge-optimized vision model</li>
    </ul>
    <div class="best-for">Best for: Image analysis and visual understanding</div>

    <h3>Code Models</h3>
    <ul>
      <li>StarCoder 2: Next-gen code LLM</li>
      <li>CodeLlama (7B): Multi-language code generation</li>
      <li>Qwen 2.5 Coder (7B): Code specialist model</li>
      <li>OpenCoder (8B): Open source code model</li>
    </ul>
    <div class="best-for">Best for: Software development and coding tasks</div>

    <h3>Small & Fast Models</h3>
    <ul>
      <li>SmolLM 2 (135M, 360M): Ultra compact models</li>
      <li>SmolLM (1.7B): Original efficient model</li>
      <li>Phi 3.5: Strong reasoning capabilities</li>
      <li>Phi 4: Latest Phi model series</li>
    </ul>
    <div class="best-for">Best for: Edge devices and fast inference</div>

    <h3>Specialized Tools</h3>
    <ul>
      <li>Drummer Code (3B): Code generation specialist</li>
      <li>Drummer Scrape (3B): Web scraping tools</li>
      <li>Drummer Arxiv (3B): Academic search</li>
      <li>Drummer Infinite (3B): Web search capabilities</li>
      <li>Drummer Search (3B): Search optimization</li>
      <li>Drummer Wayback (3B): Internet Archive integration</li>
    </ul>
    <div class="best-for">Best for: Specific task optimization</div>

    <h3>Impossible Models</h3>
    <ul>
      <li>Impossible Alt (13B): Alternative tuning</li>
      <li>Impossible Alt Text (11B): Llama3.2-based variant</li>
      <li>Belter Code (8B): Code specialist</li>
    </ul>
    <div class="best-for">Best for: Experimental applications</div>
  </div>
</body>
</html>
```

