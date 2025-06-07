# Code Snippets from toollama/API/api-tools/tools/snippets/core/markdown/processor.js

File: `toollama/API/api-tools/tools/snippets/core/markdown/processor.js`  
Language: JavaScript  
Extracted: 2025-06-07 05:22:53  

## Snippet 1
Lines 5-14

```JavaScript
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
Lines 15-18

```JavaScript
if (lang && hljs.getLanguage(lang)) {
                        try {
                            console.log("[Markdown] Highlighting:", lang);
                            return `<pre class="hljs"><code>${
```

## Snippet 3
Lines 22-24

```JavaScript
} catch (error) {
                            console.error("[Markdown] Highlight error:", error);
                        }
```

## Snippet 4
Lines 25-28

```JavaScript
}
                    console.log("[Markdown] Using plaintext");
                    const escapedStr = md.utils.escapeHtml(str);
                    return `<pre class="hljs"><code>${escapedStr}</code></pre>`;
```

## Snippet 5
Lines 30-54

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
Lines 55-57

```JavaScript
// Add inline math support
        md.inline.ruler.before('escape', 'math_inline', (state, silent) => {
            const delimiter = '$';
```

## Snippet 7
Lines 58-63

```JavaScript
if (state.src[state.pos] !== delimiter) return false;

            const start = state.pos;
            const max = state.posMax;

            state.pos++;
```

## Snippet 8
Lines 64-67

```JavaScript
while (state.pos < max && state.src[state.pos] !== delimiter) {
                state.pos++;
            }
```

## Snippet 9
Lines 68-73

```JavaScript
if (state.pos === max || state.src[state.pos] !== delimiter) {
                state.pos = start;
                return false;
            }

            const content = state.src.slice(start + 1, state.pos);
```

## Snippet 10
Lines 74-81

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
Lines 82-110

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
Lines 111-120

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
Lines 125-129

```JavaScript
formatInText: (author, page) => `(${author} ${page})`,
                formatReference: (ref) => {
                    const authors = ref.authors.join(', ');
                    return `${authors}. "${ref.title}." ${ref.journal}, vol. ${ref.volume}, no. ${ref.issue}, ${ref.year}, pp. ${ref.pages}.`;
                }
```

## Snippet 14
Lines 132-134

```JavaScript
formatInText: (author, year) => `(${author} ${year})`,
                formatReference: (ref) => {
                    const authors = ref.authors.map(a => `${a.family}, ${a.given}`).join(', ');
```

## Snippet 15
Lines 137-148

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
Lines 152-160

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
Lines 164-167

```JavaScript
} else {
                    this.citationCount[id]++;
                }
                return id;
```

## Snippet 18
Lines 168-180

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
Lines 181-237

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

