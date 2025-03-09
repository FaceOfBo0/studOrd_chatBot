from flask import Flask, render_template, request, Response, stream_with_context
from Generation.Generator import Generator
from Retrieval.RetrieverHF import RetrieverHF
import json

app = Flask(__name__)

generator = Generator()
# retriever = RetrieverHF("deutsche-telekom/gbert-large-paraphrase-cosine", "src/database/hf_dt_gbert", "cuda")
# retriever = RetrieverHF("akot/german-semantic-bmf-matryoshka", "src/database/hf_dt_matryoshka", "cuda")
# retriever = RetrieverHF("Alibaba-NLP/gte-multilingual-base", "src/database/hf_ml_alibaba", "cuda")
# retriever = RetrieverHF("CISCai/jina-embeddings-v3-query-distilled", "src/database/hf_ml_jina_lora", "cuda")
retriever = RetrieverHF("jinaai/jina-embeddings-v3", "src/database/hf_ml_jina_lora", "cuda", "retrieval.query")

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
        for token in generator.gen_response_oll_stream("phi4-mini", query, contexts):
            yield f"event: token\ndata: {token}\n\n"

    return Response(stream_with_context(generate()), mimetype='text/event-stream')

if __name__ == '__main__':
    app.run()