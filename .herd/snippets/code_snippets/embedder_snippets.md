# Code Snippets from toollama/API/api-tools/tools/snippets/core/markdown/embedder.js

File: `toollama/API/api-tools/tools/snippets/core/markdown/embedder.js`  
Language: JavaScript  
Extracted: 2025-06-07 05:22:50  

## Snippet 1
Lines 6-29

```JavaScript
// Regular expressions for different link types
    patterns: {
        youtube: /^(?:https?:\/\/)?(?:www\.)?(?:youtube\.com\/watch\?v=|youtu\.be\/)([a-zA-Z0-9_-]+)/,
        pdf: /^(https?:\/\/[^\s]+\.pdf)$/i,
        doi: /^(?:https?:\/\/(?:dx\.)?doi\.org\/|doi:)(10\.\d{4,}\/\S+)$/i,
        pubmed: /^https?:\/\/(?:www\.)?ncbi\.nlm\.nih\.gov\/pubmed\/(\d+)$/i
    },

    // Embed YouTube videos
    embedYouTube(videoId) {
        console.log("[Links] Embedding YouTube:", videoId);
        return `
            <div class="video-container">
                <iframe src="https://www.youtube.com/embed/${videoId}"
                        frameborder="0"
                        allowfullscreen
                        title="YouTube video player">
                </iframe>
            </div>`;
    },

    // Handle PDF embedding
    async validatePDFUrl(url) {
        try {
```

## Snippet 2
Lines 30-32

```JavaScript
const response = await fetch(url, { method: 'HEAD' });
            const contentType = response.headers.get('content-type');
            return response.ok && contentType && contentType.includes('pdf');
```

## Snippet 3
Lines 33-36

```JavaScript
} catch (error) {
            console.error('[PDF] Validation failed:', error);
            return false;
        }
```

## Snippet 4
Lines 37-58

```JavaScript
},

    embedPDF(url) {
        return `
            <div class="pdf-embed-container">
                <iframe class="pdf-viewer"
                        src="${url}"
                        frameborder="0"
                        title="PDF document viewer">
                </iframe>
                <div class="pdf-fallback">
                    <p>Unable to display PDF. <a href="${url}" target="_blank" rel="noopener noreferrer">Open PDF</a></p>
                </div>
            </div>`;
    },

    // Handle citations
    async fetchCitation(doi) {
        try {
            const response = await fetch(`https://api.crossref.org/works/${doi}`);
            const data = await response.json();
            return data.message;
```

## Snippet 5
Lines 59-62

```JavaScript
} catch (error) {
            console.error('[Citation] Fetch failed:', error);
            return null;
        }
```

## Snippet 6
Lines 66-69

```JavaScript
if (!citation) return '';
        return `
            <div class="citation-card">
                <h3>${citation.title[0]}</h3>
```

## Snippet 7
Lines 71-74

```JavaScript
<div class="citation-journal">${citation.publisher} (${citation['published-print']?.['date-parts']?.[0]?.[0] || 'n.d.'})</div>
                <div class="citation-metrics">
                    ${citation['is-referenced-by-count'] ? `<span>Cited by: ${citation['is-referenced-by-count']}</span>` : ''}
                </div>
```

## Snippet 8
Lines 76-81

```JavaScript
},

    // Process links in markdown content
    async processLinks(content, md) {
        const tokens = md.parse(content, {});
```

## Snippet 9
Lines 83-85

```JavaScript
if (tokens[i].type !== "inline") continue;

            const children = tokens[i].children;
```

## Snippet 10
Lines 91-94

```JavaScript
if (hrefIndex >= 0) {
                        const href = token.attrs[hrefIndex][1];
                        await this.handleLink(href, token, children, j, md);
                    }
```

## Snippet 11
Lines 97-99

```JavaScript
}

        return md.renderer.render(tokens, md.options);
```

## Snippet 12
Lines 100-106

```JavaScript
},

    // Handle different types of links
    async handleLink(href, token, children, index, md) {
        let match;

        // YouTube videos
```

## Snippet 13
Lines 107-111

```JavaScript
if ((match = this.patterns.youtube.exec(href))) {
            const videoId = match[1];
            this.replaceTokens(children, index, this.embedYouTube(videoId));
        }
        // PDFs
```

## Snippet 14
Lines 112-121

```JavaScript
else if (this.patterns.pdf.test(href)) {
            const isValid = await this.validatePDFUrl(href);
            const content = isValid
                ? this.embedPDF(href)
                : `<div class="pdf-embed-container error">
                    <p>PDF not available. <a href="${href}" target="_blank" rel="noopener noreferrer">Try opening directly</a></p>
                   </div>`;
            this.replaceTokens(children, index, content);
        }
        // DOIs and PubMed
```

## Snippet 15
Lines 122-130

```JavaScript
else if (this.patterns.doi.test(href) || this.patterns.pubmed.test(href)) {
            const citation = await this.fetchCitation(href);
            const content = citation
                ? this.embedCitation(citation)
                : `<div class="citation-card error">
                    <p>Citation not available. <a href="${href}" target="_blank" rel="noopener noreferrer">Try opening directly</a></p>
                   </div>`;
            this.replaceTokens(children, index, content);
        }
```

## Snippet 16
Lines 131-135

```JavaScript
},

    // Replace tokens with embedded content
    replaceTokens(children, startIndex, content) {
        let endIndex = startIndex + 1;
```

## Snippet 17
Lines 136-143

```JavaScript
while (endIndex < children.length && children[endIndex].type !== "link_close") {
            endIndex++;
        }

        const htmlToken = new children[startIndex].constructor("html_block", "", 0);
        htmlToken.content = content;

        children.splice(startIndex, endIndex - startIndex + 1, htmlToken);
```

