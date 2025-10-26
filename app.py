
from flask import Flask, request, jsonify, send_from_directory
from chatbot import chatbot

app = Flask(__name__)

# Serve courtroom.png
@app.route('/courtroom.png')
def courtroom_image():
    return send_from_directory('.', 'courtroom.png')

# Serve favicon.svg
@app.route('/favicon.svg')
def favicon():
    return send_from_directory('.', 'favicon.svg')

# Serve index.html at root
@app.route('/')
def index():
    return send_from_directory('static', 'index.html')

# Chat endpoint
@app.route('/chat', methods=['POST'])
def chat():
    data = request.get_json()
    user_input = data.get('message', '')
    response = chatbot(user_input)
    return jsonify({'response': response})

import os

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
