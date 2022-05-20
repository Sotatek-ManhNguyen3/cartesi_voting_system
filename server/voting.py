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
import json
import actions
from dataService import create_base_tables, list_all_candidates, top_candidates, list_campaign
from votingService import vote, create_new_campaign, get_voted_candidate, change_time_campaign, \
    add_candidates_to_campaign, delete_candidate, voted_campaigns_of_user
from lib.validator import validator, VALIDATE_RULES

logging.basicConfig(level="INFO")
logger = logging.getLogger(__name__)

rollup_server = environ["ROLLUP_HTTP_SERVER_URL"]
logger.info(f"HTTP rollup_server url is {rollup_server}")


def to_hex(value):
    return "0x" + value.encode().hex()


def add_notice(message):
    message = to_hex(message)
    print("Adding notice")
    response_data = requests.post(rollup_server + "/notice", json={"payload": message})
    print(f"Received notice status {response_data.status_code} body {response_data.json()}")
    return True


def call_finish():
    print("Finishing")
    response_data = requests.post(rollup_server + "/finish", json={"status": "accept"})
    print(f"Received finish status {response_data.status_code}")
    return True


def handle_advance(data):
    body = data
    print(f"Received advance request body {body}")
    create_base_tables()

    payload = bytes.fromhex(body["payload"][2:]).decode()
    print(payload)

    if payload == '':
        print('Default call')
        add_notice(json.dumps({'message': 'Default request'}))
        return "accept"

    payload = json.loads(payload)

    # Validate data
    if payload['action'] in VALIDATE_RULES.keys():
        result = validator(payload, VALIDATE_RULES[payload['action']])
        if 'error' in result.keys():
            print(result)
            add_notice(json.dumps(result))
            return "accept"

    if payload['action'] == actions.LIST_ALL:
        result = list_all_candidates(payload['campaign_id'])
    elif payload['action'] == actions.TOP_CANDIDATES:
        quantity = payload['quantity'] if 'quantity' in payload.keys() else 10
        result = top_candidates(payload['campaign_id'], quantity)
    elif payload['action'] == actions.VOTED_CANDIDATE:
        result = get_voted_candidate(body['metadata']['msg_sender'], payload['campaign_id'])
    elif payload['action'] == actions.VOTE:
        result = vote(
            body['metadata']['msg_sender'],
            payload['candidate_id'],
            payload['campaign_id'],
            body['metadata']['timestamp']
        )
    elif payload['action'] == actions.CREATE_CAMPAIGN:
        result = create_new_campaign(body['metadata']['msg_sender'], payload)
    elif payload['action'] == actions.LIST_CAMPAIGN:
        result = list_campaign()
    elif payload['action'] == actions.CHANGE_TIME_CAMPAIGN:
        result = change_time_campaign(
            body['metadata']['msg_sender'],
            payload['campaign_id'],
            payload['start_time'],
            payload['end_time']
        )
    elif payload['action'] == actions.ADD_CANDIDATES:
        result = add_candidates_to_campaign(
            body['metadata']['msg_sender'],
            payload['campaign_id'],
            payload['candidates']
        )
    elif payload['action'] == actions.DELETE_CANDIDATE:
        result = delete_candidate(
            body['metadata']['msg_sender'],
            payload['campaign_id'],
            payload['candidate_id']
        )
    elif payload['action'] == actions.VOTED_CAMPAIGN:
        result = voted_campaigns_of_user(body['metadata']['msg_sender'])
    else:
        result = {}

    print(result)
    print("Result type: " + type(result).__name__)
    add_notice(json.dumps(result))
    return "accept"


def handle_inspect(data):
    logger.info(f"Received inspect request data {data}")
    logger.info("Adding report")
    report = {"payload": data["payload"]}
    response_data = requests.post(rollup_server + "/report", json=report)
    logger.info(f"Received report status {response_data.status_code}")
    return "accept"


handlers = {
    "advance_state": handle_advance,
    "inspect_state": handle_inspect,
}


finish = {"status": "accept"}
while True:
    logger.info("Sending finish")
    response = requests.post(rollup_server + "/finish", json=finish)
    logger.info(f"Received finish status {response.status_code}")
    if response.status_code == 202:
        logger.info("No pending rollup request, trying again")
    else:
        rollup_request = response.json()
        handler = handlers[rollup_request["request_type"]]
        finish["status"] = handler(rollup_request["data"])
