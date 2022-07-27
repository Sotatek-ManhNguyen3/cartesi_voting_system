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
from votingService import vote, create_new_campaign, get_voted_candidate, change_time_campaign, \
    add_candidates_to_campaign, delete_candidate, voted_campaigns_of_user, initialize_tables, get_campaign_detail, \
    top_ranked_candidates, all_campaigns, to_hex, add_deposit_user
from lib.validator import validator, VALIDATE_RULES
from eth_abi import decode_abi

logging.basicConfig(level="INFO")
logger = logging.getLogger(__name__)

rollup_server = environ["ROLLUP_HTTP_SERVER_URL"]
logger.info(f"HTTP rollup_server url is {rollup_server}")

# Default header for ERC-20 transfers coming from the Portal, which corresponds
# to the Keccak256-encoded string "ERC20_Transfer", as defined at
# https://github.com/cartesi/rollups/blob/main/onchain/rollups/contracts/facets/ERC20PortalFacet.sol.
ERC20_TRANSFER_HEADER = b'Y\xda*\x98N\x16Z\xe4H|\x99\xe5\xd1\xdc\xa7\xe0L\x8a\x990\x1b\xe6\xbc\t)2\xcb]\x7f\x03Cx'


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


def add_report(payload):
    print("Adding report")
    response_data = requests.post(rollup_server + "/report", json={"status": "accept", "payload": payload})
    print(f"Received finish status {response_data.status_code}")
    return True


def action_proxy(data):
    initialize_tables()
    try:
        payload = bytes.fromhex(data["payload"][2:]).decode()
        print(payload)
    except Exception as e:
        handle_deposit_money(data["payload"], data['metadata']['msg_sender'])
        return 'accept'

    user = data['metadata']['msg_sender']
    timestamp = data['metadata']['timestamp']

    if payload == '':
        print('Default call')
        return "Default request"

    try:
        payload = json.loads(payload)
    except Exception as e:
        print('Invalid input')
        return "Invalid input"

    # Validate data
    if payload['action'] in VALIDATE_RULES.keys():
        result = validator(payload, VALIDATE_RULES[payload['action']])
        if 'error' in result.keys():
            print(result)
            add_notice(json.dumps(result))
            return "reject"
    else:
        result = 'Invalid input'
        add_notice(json.dumps(result))
        return "reject"

    if payload['action'] == actions.CAMPAIGN_DETAIL:
        result = get_campaign_detail(payload['campaign_id'])
    elif payload['action'] == actions.TOP_CANDIDATES:
        quantity = payload['quantity'] if 'quantity' in payload.keys() else 10
        result = top_ranked_candidates(payload['campaign_id'], quantity)
    elif payload['action'] == actions.VOTED_CANDIDATE:
        result = get_voted_candidate(user, payload['campaign_id'])
    elif payload['action'] == actions.VOTE:
        result = vote(
            user,
            payload['candidate_id'],
            payload['campaign_id'],
            timestamp
        )
    elif payload['action'] == actions.CREATE_CAMPAIGN:
        result = create_new_campaign(user, payload)
    elif payload['action'] == actions.LIST_CAMPAIGN:
        result = all_campaigns(payload['page'], payload['limit'], payload['type'], user)
    elif payload['action'] == actions.CHANGE_TIME_CAMPAIGN:
        result = change_time_campaign(
            user,
            payload['campaign_id'],
            payload['start_time'],
            payload['end_time']
        )
    elif payload['action'] == actions.ADD_CANDIDATES:
        result = add_candidates_to_campaign(
            user,
            payload['campaign_id'],
            payload['candidates']
        )
    elif payload['action'] == actions.DELETE_CANDIDATE:
        result = delete_candidate(
            user,
            payload['campaign_id'],
            payload['candidate_id']
        )
    elif payload['action'] == actions.VOTED_CAMPAIGN:
        result = voted_campaigns_of_user(user)
    else:
        result = {}

    print(result)
    print("Result type: " + type(result).__name__)
    add_notice(json.dumps(result))


def handle_advance(data):
    print(f"Received advance request body {data}")
    action_proxy(data)
    return "accept"


def handle_inspect(data):
    logger.info(f"Received inspect request data {data}")
    action_proxy(data)
    return "accept"


def handle_deposit_money(payload, sender):
    print(f"Received deposit request {payload}")

    try:
        # Check whether an input was sent by the Portal,
        # which is where all deposits must come from
        if sender != rollup_address:
            return reject_input(f"Input does not come from the Portal", payload)

        # Attempt to decode input as an ABI-encoded ERC20 deposit
        binary = bytes.fromhex(payload[2:])
        try:
            decoded = decode_abi(['bytes32', 'address', 'address', 'uint256', 'bytes'], binary)
        except Exception as e:
            msg = "Payload does not conform to ERC20 deposit ABI"
            print(f"{msg}")
            return reject_input(msg, payload)

        # Check if the header matches the Keccak256-encoded string "ERC20_Transfer"
        input_header = decoded[0]
        if input_header != ERC20_TRANSFER_HEADER:
            return reject_input(f"Input header is not from an ERC20 transfer", payload)

        notice = f"Deposit received from: {decoded[1]}; ERC-20: {decoded[2]}; Amount: {decoded[3]}"
        print(f"Adding notice: {notice}")
        add_deposit_user(decoded[1], decoded[3])
        add_notice(notice)
        return "accept"
    except Exception as e:
        return reject_input(f"Error processing data{payload}", payload)


def reject_input(msg, payload):
    print(f"Reject input {msg}")
    add_report(payload)
    return "reject"


handlers = {
    "advance_state": handle_advance,
    "inspect_state": handle_inspect,
}

finish = {"status": "accept"}
rollup_address = None

while True:
    logger.info("Sending finish")
    response = requests.post(rollup_server + "/finish", json=finish)
    logger.info(f"Received finish status {response.status_code}")
    if response.status_code == 202:
        logger.info("No pending rollup request, trying again")
    else:
        rollup_request = response.json()
        print(rollup_request)
        if rollup_request["request_type"] == 'inspect_state':
            handler = handlers[rollup_request["request_type"]]
            finish["status"] = handler(rollup_request["data"])
        else:
            metadata = rollup_request["data"]["metadata"]
            if metadata["epoch_index"] == 0 and metadata["input_index"] == 0:
                rollup_address = metadata["msg_sender"]
                logger.info(f"Captured rollup address: {rollup_address}")
            else:
                handler = handlers[rollup_request["request_type"]]
                finish["status"] = handler(rollup_request["data"])
