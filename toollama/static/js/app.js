document.addEventListener('DOMContentLoaded', () => {
    const searchForm = document.getElementById('searchForm');
    const searchInput = document.getElementById('searchInput');
    const loadingIndicator = document.getElementById('loadingIndicator');
    const loadingText = document.getElementById('loadingText');
    const searchResults = document.getElementById('searchResults');
    const statusSteps = document.querySelectorAll('.status-step');

    const OLLAMA_URL = 'http://localhost:11434';

    function updateStatus(step, status) {
        statusSteps.forEach(s => {
            if (s.dataset.step === step) {
                s.dataset.status = status;
            }
        });
    }

    function resetStatus() {
        statusSteps.forEach(s => {
            delete s.dataset.status;
        });
    }

    function updateLoadingText(text) {
        loadingText.textContent = text;
    }

    async function performInitialSearch(query) {
        const response = await fetch(`${OLLAMA_URL}/api/chat`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                model: "belter-searcher:latest",
                messages: [
                    { role: "user", content: query }
                ],
                stream: false
            })
        });
        
        if (!response.ok) throw new Error('Initial search failed');
        return await response.json();
    }

    async function performParallelSearches(query, initialResults) {
        // First generate contextual queries
        const queryResponse = await fetch(`${OLLAMA_URL}/api/chat`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                model: "belter-searcher:latest",
                messages: [
                    {
                        role: "user",
                        content: `Based on these results, generate 4 specific follow-up queries:\n\n${initialResults}`
                    }
                ],
                stream: false
            })
        });

        if (!queryResponse.ok) throw new Error('Failed to generate follow-up queries');
        const queryData = await queryResponse.json();
        const followUpQueries = queryData.message.content.split('\n').filter(q => q.trim());

        // Run parallel searches
        const searchPromises = [
            // Follow-up searches
            ...followUpQueries.map(q => fetch(`${OLLAMA_URL}/api/chat`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    model: "belter-searcher:latest",
                    messages: [{ role: "user", content: q }],
                    stream: false
                })
            })),
            // Arxiv search
            fetch(`${OLLAMA_URL}/api/chat`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    model: "belter-nerder:latest",
                    messages: [{ role: "user", content: `Search arxiv for: ${query}` }],
                    stream: false
                })
            }),
            // Wiki search
            fetch(`${OLLAMA_URL}/api/chat`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    model: "belter-reader:latest",
                    messages: [{ role: "user", content: `Search Wikipedia for: ${query}` }],
                    stream: false
                })
            })
        ];

        const results = await Promise.all(searchPromises);
        return await Promise.all(results.map(r => r.json()));
    }

    async function performSynthesis(query, allResults) {
        const response = await fetch(`${OLLAMA_URL}/api/chat`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                model: "deepseek-r1:8b",
                messages: [
                    {
                        role: "system",
                        content: "You are a research assistant tasked with analyzing and synthesizing search results."
                    },
                    {
                        role: "user",
                        content: `Synthesize these search results about "${query}":\n\n${allResults}`
                    }
                ],
                stream: true
            })
        });

        if (!response.ok) throw new Error('Synthesis failed');
        
        // Handle streaming response
        const reader = response.body.getReader();
        const decoder = new TextDecoder();
        let synthesisText = '';
        
        while (true) {
            const { done, value } = await reader.read();
            if (done) break;
            
            const chunk = decoder.decode(value);
            const lines = chunk.split('\n');
            
            for (const line of lines) {
                if (!line.trim()) continue;
                try {
                    const data = JSON.parse(line);
                    if (data.message?.content) {
                        synthesisText += data.message.content;
                        searchResults.textContent = synthesisText;
                    }
                } catch (e) {
                    console.warn('Failed to parse streaming chunk:', e);
                }
            }
        }
        
        return synthesisText;
    }

    async function handleSearch(query) {
        try {
            // Reset UI
            resetStatus();
            searchResults.textContent = '';
            loadingIndicator.classList.remove('hidden');
            
            // Initial Search
            updateStatus('initial', 'active');
            updateLoadingText('Performing initial search...');
            const initialResults = await performInitialSearch(query);
            updateStatus('initial', 'complete');
            
            // Parallel Searches
            updateStatus('parallel', 'active');
            updateLoadingText('Running parallel searches...');
            const parallelResults = await performParallelSearches(query, initialResults.message.content);
            updateStatus('parallel', 'complete');
            
            // Combine all results
            const allResults = [
                initialResults.message.content,
                ...parallelResults.map(r => r.message.content)
            ].join('\n\n---\n\n');
            
            // Final Synthesis
            updateStatus('synthesis', 'active');
            updateLoadingText('Synthesizing results...');
            const finalReport = await performSynthesis(query, allResults);
            updateStatus('synthesis', 'complete');
            
            // Hide loading indicator after streaming completes
            loadingIndicator.classList.add('hidden');
            
        } catch (error) {
            console.error('Search error:', error);
            loadingIndicator.classList.add('hidden');
            searchResults.textContent = `Error: ${error.message}`;
            resetStatus();
        }
    }

    // Handle form submission
    searchForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const query = searchInput.value.trim();
        if (query) {
            await handleSearch(query);
        }
    });

    // Handle input changes
    searchInput.addEventListener('input', () => {
        if (searchInput.value.trim()) {
            searchForm.querySelector('button').removeAttribute('disabled');
        } else {
            searchForm.querySelector('button').setAttribute('disabled', '');
        }
    });
}); 
