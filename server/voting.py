# Copyright 2022 Cartesi Pte. Ltd.
#
# SPDX-License-Identifier: Apache-2.0
# Licensed under the Apache License, Version 2.0 (the "License"); you may not use
# this file except in compliance with the License. You may obtain a copy of the
# License at http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software distributed
# under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR
# CONDITIONS OF ANY KIND, either express or implied. See the License for the
# specific language governing permissions and limitations under the License.

from os import environ
import logging
import requests
from flask import Flask, request
import json
import actions
from dataService import create_candidates, list_all_candidates, top_candidates, voted_candidate
from votingService import vote

app = Flask(__name__)
app.logger.setLevel(logging.INFO)

dispatcher_url = environ["HTTP_DISPATCHER_URL"]
app.logger.info(f"HTTP dispatcher url is {dispatcher_url}")


@app.route('/advance', methods=['POST'])
def advance():
    body = request.get_json("metadata")
    print(f"Received advance request body {body}")
    create_candidates()

    payload = bytes.fromhex(body["payload"][2:]).decode()
    print(payload)
    payload = json.loads(payload)

    if payload['action'] == actions.LIST_ALL:
        result = list_all_candidates()
    elif payload['action'] == actions.TOP_CANDIDATES:
        result = top_candidates(payload['quantity'])
    elif payload['action'] == actions.VOTED_CANDIDATE:
        result = voted_candidate(body['metadata']['address'])
    elif payload['action'] == actions.VOTE:
        result = vote(body['metadata']['address'], payload['candidate_id'])
    else:
        result = {}

    print(result)
    print("Result type: " + type(result).__name__)
    add_notice(json.dumps(result))
    finish()
    return "", 202


@app.route('/inspect', methods=['GET'])
def inspect(payload):
    print(f"Received inspect request payload {payload}")
    return {"reports": [{"payload": payload}]}, 200


def to_hex(value):
    return "0x" + value.encode().hex()


def add_notice(message):
    message = to_hex(message)
    print("Adding notice")
    response = requests.post(dispatcher_url + "/notice", json={"payload": message})
    print(f"Received notice status {response.status_code} body {response.json()}")
    return True


def finish():
    print("Finishing")
    response = requests.post(dispatcher_url + "/finish", json={"status": "accept"})
    print(f"Received finish status {response.status_code}")
    return True
