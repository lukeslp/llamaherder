from flask import Flask, request, jsonify, render_template
from belter import OllamaInfiniteUser
import asyncio

app = Flask(__name__)
searcher = OllamaInfiniteUser()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/search/initial', methods=['POST'])
async def initial_search():
    try:
        data = request.json
        query = data.get('query')
        if not query:
            return jsonify({'error': 'No query provided'}), 400
            
        # Perform initial search
        initial_tool_call = {
            "tool": "google_search",
            "parameters": {"query": query}
        }
        initial_result = await searcher.execute_tool(initial_tool_call)
        
        return jsonify({'status': 'success', 'result': initial_result})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/search/parallel', methods=['POST'])
async def parallel_search():
    try:
        data = request.json
        query = data.get('query')
        if not query:
            return jsonify({'error': 'No query provided'}), 400
            
        # Generate queries and run parallel searches
        initial_result = await searcher.execute_tool({
            "tool": "google_search",
            "parameters": {"query": query}
        })
        
        adjacent_queries = await searcher.generate_adjacent_queries(
            query, 
            searcher.format_search_result(initial_result)
        )
        
        urls_to_scrape = searcher.extract_important_urls(
            searcher.format_search_result(initial_result)
        )
        
        # Prepare parallel tasks
        tasks = []
        
        # Add follow-up search tasks
        for q in adjacent_queries:
            tasks.append(searcher.execute_tool({
                "tool": "google_search",
                "parameters": {"query": q}
            }))
        
        # Add specialized searches
        tasks.extend([
            searcher.async_post(
                searcher.base_url,
                {
                    "model": "belter-nerder:latest",
                    "messages": [{"role": "user", "content": f"Search arxiv for: {query}"}],
                    "stream": False,
                    "context_length": 8192,
                    "num_predict": 4096
                }
            ),
            searcher.async_post(
                searcher.base_url,
                {
                    "model": "belter-reader:latest",
                    "messages": [{"role": "user", "content": f"Search Wikipedia for: {query}"}],
                    "stream": False,
                    "context_length": 8192,
                    "num_predict": 4096
                }
            )
        ])
        
        # Add scraping tasks
        for url in urls_to_scrape[:2]:
            tasks.append(
                searcher.async_post(
                    searcher.base_url,
                    {
                        "model": "belter-scraper:latest",
                        "messages": [{"role": "user", "content": f"Scrape and summarize: {url}"}],
                        "stream": False,
                        "context_length": 8192,
                        "num_predict": 4096
                    }
                )
            )
        
        # Execute all tasks
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        return jsonify({
            'status': 'success',
            'results': results
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/search/synthesis', methods=['POST'])
async def synthesis():
    try:
        data = request.json
        query = data.get('query')
        if not query:
            return jsonify({'error': 'No query provided'}), 400
            
        # Get all saved results for this query
        saved_files = [f for f in searcher.results_dir.glob(f'*_{query}_*.txt')]
        
        if not saved_files:
            return jsonify({'error': 'No results found for synthesis'}), 404
            
        # Perform synthesis
        final_report = await searcher.synthesize_results(saved_files, query)
        
        return jsonify({
            'status': 'success',
            'content': final_report
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True) 