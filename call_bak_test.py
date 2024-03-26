from flask import Flask, request,Response
from flask import jsonify
from channel import channel_factory
from common.log import logger
from config import conf
import time
from threading import Thread
from flask import Flask, jsonify, request, abort
app = Flask(__name__)

@app.route('/dialogue/<string:custom_user_id>', methods=['POST'])
def create_task(custom_user_id):
    data = request.get_json(silent=True)
    return data
    # if task_id in tasks:
    #     abort(409)  # Conflict: task_id already exists
    # if not request.json or 'task' not in request.json:
    #     abort(400)
    # tasks[task_id] = {'task': request.json['task']}
    # return jsonify(tasks[task_id]), 201
