from flask import Flask, request
import api.main_process as main_process
import os

# Main app route

app = Flask(__name__)
env_variable = ""
env_variable = os.environ['TEST_VARIABLE']

@app.route('/', methods=['GET', 'POST'])
def handle_requests():
    if request.method == 'GET':
        return env_variable + "." if env_variable else 'No env variable found.'
    elif request.method == 'POST':
        data = request.json
        message = main_process.main(data)
        return message
