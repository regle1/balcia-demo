import os
from time import sleep
from packaging import version
from flask import Flask, request, jsonify
import openai
from openai import OpenAI
import functions

OPENAI_API_KEY = os.environ['OPENAI_API_KEY']

# Start Flask app
app = Flask(__name__)

# Init client
client = OpenAI(default_headers={"OpenAI-Beta": "assistants=v2"}, api_key=OPENAI_API_KEY)  

# Create new assistant or load existing
assistant_id = functions.create_assistant(client)

# Start conversation thread
@app.route('/start', methods=['GET'])
def start_conversation():
    try:
        thread = client.beta.threads.create()
        return jsonify({"thread_id": thread.id})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Generate response
@app.route('/chat', methods=['POST'])
def chat():
    data = request.json
    thread_id = data.get('thread_id')
    user_input = data.get('message', '')

    if not thread_id:
        return jsonify({"error": "Missing thread_id"}), 400

    try:
        client.beta.threads.messages.create(
            thread_id=thread_id,
            role="user",
            content=user_input
        )

        run = client.beta.threads.runs.create(
            thread_id=thread_id,
            assistant_id=assistant_id
        )

        while True:
            run_status = client.beta.threads.runs.retrieve(
                thread_id=thread_id,
                run_id=run.id
            )
            if run_status.status == 'completed':
                break
            sleep(1)

        messages = client.beta.threads.messages.list(thread_id=thread_id)
        response = messages.data[0].content[0].text.value

        print(f"Assistant response: {response}")
        return jsonify({"response": response})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Run server
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
