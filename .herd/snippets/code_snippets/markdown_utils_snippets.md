# Code Snippets from toollama/API/api-tools/tools/snippets/processed/markdown_utils.js

File: `toollama/API/api-tools/tools/snippets/processed/markdown_utils.js`  
Language: JavaScript  
Extracted: 2025-06-07 05:21:27  

## Snippet 1
Lines 5-15

```JavaScript
// Markdown Configuration and Initialization
export const MarkdownProcessor = {
    initializeMarkdown() {
        console.log("[Markdown] Initializing parser");
        const md = window
            .markdownit({
                html: true,
                breaks: true,
                linkify: true,
                typographer: true,
                highlight: (str, lang) => {
```

## Snippet 2
Lines 16-19

```JavaScript
if (lang && hljs.getLanguage(lang)) {
                        try {
                            console.log("[Markdown] Highlighting:", lang);
                            return `<pre class="hljs"><code>${
```

## Snippet 3
Lines 23-25

```JavaScript
} catch (error) {
                            console.error("[Markdown] Highlight error:", error);
                        }
```

## Snippet 4
Lines 26-29

```JavaScript
}
                    console.log("[Markdown] Using plaintext");
                    const escapedStr = md.utils.escapeHtml(str);
                    return `<pre class="hljs"><code>${escapedStr}</code></pre>`;
```

## Snippet 5
Lines 31-55

```JavaScript
})
            .use(window.markdownitTaskLists)
            .use(window.markdownitFootnote)
            .use(window.markdownitSub)
            .use(window.markdownitSup)
            .use(window.markdownitDeflist)
            .use(window.markdownitAbbr)
            .use(window.markdownitMark)
            .use(window.markdownitMultimdTable, {
                multiline: true,
                rowspan: true,
                headerless: true,
                multibody: true
            })
            .use(window.markdownitKatex, {
                throwOnError: false,
                displayMode: true,
                output: 'html',
                strict: false
            })
            .use(window.markdownitCitations, {
                strict: false,
                format: 'apa'
            });
```

## Snippet 6
Lines 56-58

```JavaScript
// Add inline math support
        md.inline.ruler.before('escape', 'math_inline', (state, silent) => {
            const delimiter = '$';
```

## Snippet 7
Lines 59-64

```JavaScript
if (state.src[state.pos] !== delimiter) return false;

            const start = state.pos;
            const max = state.posMax;

            state.pos++;
```

## Snippet 8
Lines 65-68

```JavaScript
while (state.pos < max && state.src[state.pos] !== delimiter) {
                state.pos++;
            }
```

## Snippet 9
Lines 69-74

```JavaScript
if (state.pos === max || state.src[state.pos] !== delimiter) {
                state.pos = start;
                return false;
            }

            const content = state.src.slice(start + 1, state.pos);
```

## Snippet 10
Lines 75-82

```JavaScript
if (!silent) {
                const token = state.push('math_inline', '', 0);
                token.content = content;
                token.markup = delimiter;
            }

            state.pos++;
            return true;
```

## Snippet 11
Lines 83-111

```JavaScript
});

        // Add accessibility enhancements
        md.renderer.rules.math_inline = (tokens, idx) => {
            const content = tokens[idx].content;
            return `<span class="math-inline" role="math" aria-label="${content}">${content}</span>`;
        };

        md.renderer.rules.math_block = (tokens, idx) => {
            const content = tokens[idx].content;
            return `<div class="math-block" role="math" aria-label="Mathematical expression: ${content}">${content}</div>`;
        };

        md.renderer.rules.footnote_ref = (tokens, idx, options, env, slf) => {
            const id = slf.rules.footnote_anchor_name(tokens, idx, options, env, slf);
            const caption = slf.rules.footnote_caption(tokens, idx, options, env, slf);
            return `<sup class="footnote-ref" role="doc-noteref">
                     <a href="#fn${id}" id="fnref${id}" aria-label="Footnote ${caption}">${caption}</a>
                   </sup>`;
        };

        md.renderer.rules.footnote_block_open = () => {
            return `<section class="footnotes" role="doc-endnotes">
                    <h2 class="sr-only">Footnotes</h2>
                    <ol role="list">`;
        };

        console.log("[Markdown] Parser initialized with academic features");
        return md;
```

## Snippet 12
Lines 112-121

```JavaScript
},

    // Academic writing enhancements
    academicFeatures: {
        // Citation styles (APA, MLA, Chicago, IEEE, Harvard)
        citationStyles: {
            apa: {
                formatInText: (author, year) => `(${author}, ${year})`,
                formatReference: (ref) => {
                    const authors = ref.authors.join(', ');
```

## Snippet 13
Lines 126-130

```JavaScript
formatInText: (author, page) => `(${author} ${page})`,
                formatReference: (ref) => {
                    const authors = ref.authors.join(', ');
                    return `${authors}. "${ref.title}." ${ref.journal}, vol. ${ref.volume}, no. ${ref.issue}, ${ref.year}, pp. ${ref.pages}.`;
                }
```

## Snippet 14
Lines 133-135

```JavaScript
formatInText: (author, year) => `(${author} ${year})`,
                formatReference: (ref) => {
                    const authors = ref.authors.map(a => `${a.family}, ${a.given}`).join(', ');
```

## Snippet 15
Lines 138-149

```JavaScript
},
            ieee: {
                formatInText: (index) => `[${index}]`,
                formatReference: (ref, index) => {
                    const authors = ref.authors.map(a => `${a.initials}. ${a.family}`).join(', ');
                    return `[${index}] ${authors}, "${ref.title}," ${ref.journal}, vol. ${ref.volume}, no. ${ref.issue}, pp. ${ref.pages}, ${ref.year}.`;
                }
            },
            harvard: {
                formatInText: (author, year) => `(${author}, ${year})`,
                formatReference: (ref) => {
                    const authors = ref.authors.map(a => `${a.family}, ${a.given[0]}.`).join(', ');
```

## Snippet 16
Lines 153-161

```JavaScript
},

        // Bibliography management
        bibliographyManager: {
            references: [],
            citationCount: {},

            addReference(ref) {
                const id = this.generateCitationId(ref);
```

## Snippet 17
Lines 165-168

```JavaScript
} else {
                    this.citationCount[id]++;
                }
                return id;
```

## Snippet 18
Lines 169-181

```JavaScript
},

            generateCitationId(ref) {
                return `${ref.authors[0].family.toLowerCase()}${ref.year}`;
            },

            formatBibliography(style = 'apa') {
                const formatter = this.citationStyles[style].formatReference;
                return this.references
                    .sort((a, b) => a.authors[0].family.localeCompare(b.authors[0].family))
                    .map((ref, index) => formatter(ref, index + 1))
                    .join('\n\n');
            }
```

## Snippet 19
Lines 182-238

```JavaScript
},

        // Figure and table numbering
        contentNumbering: {
            figures: 1,
            tables: 1,
            equations: 1,

            getNextNumber(type) {
                return this[type]++;
            },

            formatFigure(caption, imageUrl = '') {
                const num = this.getNextNumber('figures');
                return `<figure role="figure" aria-labelledby="fig-${num}">
                          ${imageUrl ? `<img src="${imageUrl}" alt="${caption}">` : ''}
                          <figcaption id="fig-${num}">Figure ${num}: ${caption}</figcaption>
                        </figure>`;
            },

            formatTable(caption, content) {
                const num = this.getNextNumber('tables');
                return `<div role="table" aria-labelledby="table-${num}">
                          <div id="table-${num}" class="table-caption">Table ${num}: ${caption}</div>
                          ${content}
                        </div>`;
            },

            formatEquation(equation, label = '') {
                const num = this.getNextNumber('equations');
                return `<div class="equation-container" role="math" aria-label="Equation ${num}${label ? ': ' + label : ''}">
                          <div class="equation" id="eq-${num}">${equation}</div>
                          <div class="equation-number">(${num})</div>
                        </div>`;
            }
        },

        // Academic document sections
        documentSections: {
            abstract: (content) => `
                <section class="abstract" role="doc-abstract" aria-label="Abstract">
                    <h2>Abstract</h2>
                    <div class="abstract-content">${content}</div>
                </section>`,

            keywords: (keywords) => `
                <section class="keywords" role="doc-keywords" aria-label="Keywords">
                    <h3>Keywords</h3>
                    <div class="keywords-list">${keywords.join(', ')}</div>
                </section>`,

            acknowledgments: (content) => `
                <section class="acknowledgments" role="doc-acknowledgments" aria-label="Acknowledgments">
                    <h2>Acknowledgments</h2>
                    <div class="acknowledgments-content">${content}</div>
                </section>`
        }
```

## Snippet 20
Lines 240-243

```JavaScript
};

// Link Embedding
export const LinkEmbedder = {
```

## Snippet 21
Lines 244-267

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

## Snippet 22
Lines 268-270

```JavaScript
const response = await fetch(url, { method: 'HEAD' });
            const contentType = response.headers.get('content-type');
            return response.ok && contentType && contentType.includes('pdf');
```

## Snippet 23
Lines 271-274

```JavaScript
} catch (error) {
            console.error('[PDF] Validation failed:', error);
            return false;
        }
```

## Snippet 24
Lines 275-296

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

## Snippet 25
Lines 297-300

```JavaScript
} catch (error) {
            console.error('[Citation] Fetch failed:', error);
            return null;
        }
```

## Snippet 26
Lines 304-307

```JavaScript
if (!citation) return '';
        return `
            <div class="citation-card">
                <h3>${citation.title[0]}</h3>
```

## Snippet 27
Lines 309-312

```JavaScript
<div class="citation-journal">${citation.publisher} (${citation['published-print']?.['date-parts']?.[0]?.[0] || 'n.d.'})</div>
                <div class="citation-metrics">
                    ${citation['is-referenced-by-count'] ? `<span>Cited by: ${citation['is-referenced-by-count']}</span>` : ''}
                </div>
```

## Snippet 28
Lines 314-319

```JavaScript
},

    // Process links in markdown content
    async processLinks(content, md) {
        const tokens = md.parse(content, {});
```

## Snippet 29
Lines 321-323

```JavaScript
if (tokens[i].type !== "inline") continue;

            const children = tokens[i].children;
```

## Snippet 30
Lines 329-332

```JavaScript
if (hrefIndex >= 0) {
                        const href = token.attrs[hrefIndex][1];
                        await this.handleLink(href, token, children, j, md);
                    }
```

## Snippet 31
Lines 335-337

```JavaScript
}

        return md.renderer.render(tokens, md.options);
```

## Snippet 32
Lines 338-344

```JavaScript
},

    // Handle different types of links
    async handleLink(href, token, children, index, md) {
        let match;

        // YouTube videos
```

## Snippet 33
Lines 345-349

```JavaScript
if ((match = this.patterns.youtube.exec(href))) {
            const videoId = match[1];
            this.replaceTokens(children, index, this.embedYouTube(videoId));
        }
        // PDFs
```

## Snippet 34
Lines 350-359

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

## Snippet 35
Lines 360-368

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

## Snippet 36
Lines 369-373

```JavaScript
},

    // Replace tokens with embedded content
    replaceTokens(children, startIndex, content) {
        let endIndex = startIndex + 1;
```

## Snippet 37
Lines 374-381

```JavaScript
while (endIndex < children.length && children[endIndex].type !== "link_close") {
            endIndex++;
        }

        const htmlToken = new children[startIndex].constructor("html_block", "", 0);
        htmlToken.content = content;

        children.splice(startIndex, endIndex - startIndex + 1, htmlToken);
```

