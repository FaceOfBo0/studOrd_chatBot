from flask import Flask, render_template, request, jsonify
from Generation.Generator import Generator
from Retrieval.RetrieverHF import RetrieverHF

app = Flask(__name__)

generator = Generator()
retriever = RetrieverHF("sentence-transformers/all-MiniLM-L12-v2", "src/database/hf_minilm")

@app.route('/', methods=['GET'])
def home():
    return render_template('index.html')

@app.route('/query', methods=['POST'])
def query():
    data = request.get_json(silent=True) or {}
    query = data.get('query', '')

    contexts = retriever.get_ctx_from_db(query, 2)
    response = generator.gen_response_oll("llama3.2:3b", query, contexts)
    
    return jsonify({
        'response': response,
        'contexts': contexts
    })

if __name__ == '__main__':
    app.run(debug=True)