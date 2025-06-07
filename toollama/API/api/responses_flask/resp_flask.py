from openai import OpenAI
from flask import Flask, render_template_string, request, Response

app = Flask(__name__)

# Hard-coded API key (WARNING: For demonstration purposes only!)
client = OpenAI(api_key="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")

# HTML template with a basic form and JavaScript to stream the response
index_html = """
<!DOCTYPE html>
<html>
<head>
    <title>OpenAI Streaming Response</title>
</head>
<body>
    <h1>OpenAI Streaming Response</h1>
    <form id="prompt-form">
        <textarea id="prompt" name="prompt" rows="5" cols="60" placeholder="Enter your prompt here"></textarea><br>
        <button type="submit">Submit</button>
    </form>
    <h2>Response:</h2>
    <pre id="response"></pre>

    <script>
    // Intercept the form submission to start a streaming request
    document.getElementById("prompt-form").addEventListener("submit", function(e) {
        e.preventDefault();
        const prompt = document.getElementById("prompt").value;
        const responseElement = document.getElementById("response");
        responseElement.textContent = "";
        
        fetch("/generate", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({ prompt: prompt })
        }).then(response => {
            const reader = response.body.getReader();
            const decoder = new TextDecoder();
            function read() {
                reader.read().then(({ done, value }) => {
                    if (done) {
                        return;
                    }
                    const chunk = decoder.decode(value);
                    responseElement.textContent += chunk;
                    read();
                });
            }
            read();
        }).catch(err => {
            console.error(err);
        });
    });
    </script>
</body>
</html>
"""

@app.route("/")
def index():
    return render_template_string(index_html)

@app.route("/generate", methods=["POST"])
def generate():
    data = request.get_json()
    prompt = data.get("prompt", "")

    def generate_openai():
        # Call the OpenAI API using the ChatCompletion endpoint with streaming enabled.
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            stream=True
        )
        for chunk in response:
            # Use getattr to safely access the "content" attribute from the delta.
            text = getattr(chunk.choices[0].delta, "content", "")
            if text:
                yield text

    # Return a streaming response with MIME type text/plain
    return Response(generate_openai(), mimetype="text/plain")

if __name__ == "__main__":
    # Run the Flask app in debug mode (do not use debug mode in production)
    app.run(debug=True, threaded=True)