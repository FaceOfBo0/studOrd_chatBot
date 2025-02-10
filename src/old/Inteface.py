from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/ask', methods=['POST'])
def ask():
    data = request.json
    question = data.get('question')
    answer = answer_question(question, chunks, vectorizer)
    return jsonify({'answer': answer})

if __name__ == '__main__':
    app.run(debug=True)