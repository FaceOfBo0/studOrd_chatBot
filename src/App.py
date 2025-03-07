from flask import Flask, render_template, request, Response, stream_with_context
from Generation.Generator import Generator
from Retrieval.RetrieverHF import RetrieverHF
import json

app = Flask(__name__)

generator = Generator()
retriever = RetrieverHF("deutsche-telekom/gbert-large-paraphrase-cosine", "src/database/hf_dt_gbert", "cuda")

@app.route('/', methods=['GET'])
def home():
    return render_template('index.html')

@app.route('/query', methods=['POST'])
def query():
    data = request.get_json(silent=True) or {}
    query = data.get('query', '')
    
    # Get contexts first
    contexts = retriever.get_results_from_db(query, 3, "docs_pnt")
    
    def generate():
        # Send a special marker for contexts
        yield f"event: contexts\ndata: {json.dumps({'contexts': contexts})}\n\n"
        
        # Then stream the response with a different event type
        for token in generator.gen_response_stream("llama3.2:3b", query, contexts):
            yield f"event: token\ndata: {token}\n\n"

    return Response(stream_with_context(generate()), mimetype='text/event-stream')

if __name__ == '__main__':
    app.run(debug=True)