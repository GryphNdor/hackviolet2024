import os
import json
import tempfile
from flask import Flask, request, jsonify, send_file
from openai import OpenAI

from .utils import get_completion

# Initialize flask app
app = Flask(__name__)

# Initialize OpenAI client
client = OpenAI() 

# Default endpoint
@app.route('/')
def home():
    return 'Hello, World!'

# Generate words
@app.route('/generate', methods=['POST'])
def generate():
    data = request.json
    topic = data.get('topic')
    
    prompt = "Generate a list of 20 related words for: " + topic + ". For each word in the list, \
        generate its plural form as well. These entries should not be mapped to each other, but \
        should rather be individual entries. For example, if the input is 'fruits', the output should \
        be ['apple', 'apples', 'banana', 'bananas', etc.] Format your answer as a JSON array and \
        include no additional context."
    
    # Get the completion from OpenAI
    try:
        response = get_completion(client, prompt)
        response_object = json.loads(response)

        with open(os.path.join(tempfile.gettempdir(), 'response.json'), 'w') as file:
            json.dump(response_object, file, indent=4)

        return jsonify(response_object)
    
    except Exception as e:
        return jsonify(message=f"An error occurred: {str(e)}")


# Retrieve JSON file
@app.route('/get-json', methods=['GET'])
def get_json():
    return send_file(os.path.join(tempfile.gettempdir(), 'response.json'), as_attachment=True)


# Run application
if __name__ == '__main__':
    app.run()