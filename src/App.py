from flask import Flask, render_template, request, Response, stream_with_context
from Generation import Generator
from Retrieval.RetrieverHF import RetrieverHF
from Preprocessing import PreProcessor, FileHandler
import json

app = Flask(__name__)

# retriever = RetrieverHF("deutsche-telekom/gbert-large-paraphrase-cosine", "src/database/hf_dt_gbert", "cuda")
# retriever = RetrieverHF("akot/german-semantic-bmf-matryoshka", "src/database/hf_dt_matryoshka", "cuda")
# retriever = RetrieverHF("Alibaba-NLP/gte-multilingual-base", "src/database/hf_ml_alibaba", "cuda")
# retriever = RetrieverHF("CISCai/jina-embeddings-v3-query-distilled", "src/database/hf_ml_jina_lora", "cuda")
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
    results = retriever.get_results_from_db(query, 3, "docs_pnt")
    contexts = []
    for elem in results:
        if elem in pntCtxMap:
            contexts.append(PreProcessor.get_context_string(pntCtxMap[elem]) + ":<br><br>" + elem)
        else:
            contexts.append(elem)
    # contexts = [PreProcessor.get_context_string(pntCtxMap[elem]) + ":<br><br>" + elem for elem in contexts]


    def generate():
        # Send a special marker for contexts
        yield f"event: contexts\ndata: {json.dumps({'contexts': contexts})}\n\n"

        # Then stream the response with a different event type, "mistral-nemo-instruct-2407"
        # for token in Generator.gen_response_lms_stream("phi-4-mini-instruct", query, contexts):
        #     yield f"event: token\ndata: {token}\n\n"
        for token in Generator.gen_response_oll_stream("phi4-mini", query, contexts):
            yield f"event: token\ndata: {token}\n\n"

    return Response(stream_with_context(generate()), mimetype='text/event-stream')

if __name__ == '__main__':
    app.run()
