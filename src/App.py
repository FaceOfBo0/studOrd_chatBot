from flask import Flask, render_template, request, Response, stream_with_context
from Generation import Generator
from Retrieval.RetrieverHF import RetrieverHF
from Preprocessing import PreProcessor, FileHandler
import json

app = Flask(__name__)

retriever = RetrieverHF("jinaai/jina-embeddings-v3", "database/hf_jinaai_lora", "retrieval.query")
studReg = FileHandler.load_regulation_from_json("data/json/stdReg_new.json")
pntCtxMap = PreProcessor.create_pntCtxMap_from_stdyReg(studReg)

@app.route('/', methods=['GET'])
def home():
    return render_template('index.html')

@app.route('/query', methods=['POST'])
def query():
    data = request.get_json(silent=True) or {}
    query = data.get('query', '')

    # Get contexts first
    results = retriever.get_results_from_db(query, 3, "docs")
    contexts = []
    for elem in results:
        if elem in pntCtxMap:
            contexts.append(PreProcessor.get_context_string(pntCtxMap[elem]) + ":<br><br>" + elem)
        else:
            contexts.append(elem)

    def generate():
        yield f"event: contexts\ndata: {json.dumps({'contexts': contexts})}\n\n"
        for token in Generator.gen_response_lms_stream("gemma-3-4b-it", query, contexts):
            yield f"event: token\ndata: {token}\n\n"

    return Response(stream_with_context(generate()), mimetype='text/event-stream')

if __name__ == '__main__':
    app.run()
