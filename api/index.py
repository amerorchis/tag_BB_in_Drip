from flask import Flask, request
import api.main_process as main_process
import os
from flask_cors import CORS

# Main app route

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "https://host.nxt.blackbaud.com"}})
env_variable = ""
env_variable = os.environ['TEST_VARIABLE']

@app.route('/', methods=['GET', 'POST'])
def handle_requests():
    if request.method == 'GET':
        return env_variable + ". Make a POST request to use this program." if env_variable else 'No env variable found.'
    elif request.method == 'POST':
        data = request.json
        message = main_process.main(data)
        print(message[0].data)
        return message
    elif request.method == 'OPTIONS':
        return 200