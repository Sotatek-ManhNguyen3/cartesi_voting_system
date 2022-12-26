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
import datetime
from os import environ
import logging
import requests
import json
from constants import actions, consts
from services.votingService import vote, create_new_campaign, get_voted_candidate, \
    initialize_tables, get_campaign_detail, get_actions_histories, \
    all_campaigns, to_hex, add_deposit_user, get_voting_result, get_detail_candidate, \
    edit_campaign, delete_campaign, get_user_info, withdraw_money, save_executed_voucher_for_user, \
    get_executed_vouchers, can_deposit_token, list_token, list_voter, create_profile, update_profile, \
    delete_profile, list_profile_of_user, detail_profile, list_profile, list_campaign_of_profile, \
    list_profile_of_manager, join_profile, leave_profile
from lib.validator import validator, VALIDATE_RULES, ALLOWED_ACTIONS_INSPECT
from eth_abi import decode_abi, encode_abi
from services.notificationService import save_notification, get_notification
from services.adminService import handle_admin_action
from constants.notificationActions import NOTIFICATION_ACTIONS

logging.basicConfig(level="INFO")
logger = logging.getLogger(__name__)

rollup_server = environ["ROLLUP_HTTP_SERVER_URL"]
logger.info(f"HTTP rollup_server url is {rollup_server}")

# Default header for ERC-20 transfers coming from the Portal, which corresponds
# to the Keccak256-encoded string "ERC20_Transfer", as defined at
# https://github.com/cartesi/rollups/blob/main/onchain/rollups/contracts/facets/ERC20PortalFacet.sol.
ERC20_TRANSFER_HEADER = b'Y\xda*\x98N\x16Z\xe4H|\x99\xe5\xd1\xdc\xa7\xe0L\x8a\x990\x1b\xe6\xbc\t)2\xcb]\x7f\x03Cx'
# Function selector to be called during the execution of a voucher that transfers funds,
# which corresponds to the first 4 bytes of the Keccak256-encoded result of "transfer(address,uint256)"
TRANSFER_FUNCTION_SELECTOR = b'\xa9\x05\x9c\xbb'

BASE_AMOUNT = 1000000000000000000


def add_notice(message, status=consts.ACCEPT_STATUS):
    message = to_hex(message)
    print("Adding notice")
    response_data = requests.post(rollup_server + "/notice", json={"status": status, "payload": message})
    print(f"Received notice status {response_data.status_code}")
    return status


def call_finish(status=consts.ACCEPT_STATUS):
    print("Finishing")
    response_data = requests.post(rollup_server + "/finish", json={"status": status})
    print(f"Received finish status {response_data.status_code}")
    return status


def add_report(payload, status=consts.ACCEPT_STATUS):
    print("Adding report")
    response_data = requests.post(rollup_server + "/report", json={"payload": to_hex(payload)})
    print(response_data.status_code)
    print(response_data.content)
    print(f"Received report status {response_data.status_code}")
    return status


# Handle incoming action
# Return status of action
def action_proxy(data, is_inspect=False):
    if is_inspect:
        hand_result = add_report
    else:
        hand_result = add_notice

    timestamp = data['metadata']['timestamp']

    try:
        payload = bytes.fromhex(data["payload"][2:]).decode()
        print(payload)
    except Exception as e:
        print(e)
        return handle_deposit_money(data["payload"], data['metadata']['msg_sender'], timestamp)

    user = data['metadata']['msg_sender']

    if payload == '':
        print('Default call')
        return consts.ACCEPT_STATUS

    try:
        payload = json.loads(payload)
    except Exception as e:
        result = {'error': 'Invalid input'}
        hand_result = add_report
        print(e)
        print(result)
        hand_result(json.dumps(result), consts.REJECT_STATUS)
        save_notification(user, NOTIFICATION_ACTIONS['SYSTEM'], {}, timestamp, result)
        return consts.REJECT_STATUS

    # Validate inspect call
    if is_inspect and payload['action'] not in ALLOWED_ACTIONS_INSPECT:
        result = {'error': 'This action is not allowed to use inspect api!'}
        hand_result = add_report
        print(result)
        hand_result(json.dumps(result), consts.REJECT_STATUS)
        save_notification(user, NOTIFICATION_ACTIONS['SYSTEM'], {}, timestamp, result)
        return consts.REJECT_STATUS

    # Validate data
    if payload['action'] in VALIDATE_RULES.keys():
        result = validator(payload, VALIDATE_RULES[payload['action']])
        if 'error' in result.keys():
            print(result)
            hand_result = add_report
            hand_result(json.dumps(result), consts.REJECT_STATUS)
            save_notification(user, payload['action'], payload, timestamp, result)
            return consts.REJECT_STATUS
    else:
        result = {'error': 'Invalid action'}
        print(result)
        hand_result = add_report
        hand_result(json.dumps(result), consts.REJECT_STATUS)
        save_notification(user, NOTIFICATION_ACTIONS['SYSTEM'], {}, timestamp, result)
        return consts.REJECT_STATUS

    print('Accept payload')

    if payload['action'] == actions.CAMPAIGN_DETAIL:
        result = get_campaign_detail(user, payload['campaign_id'])
    elif payload['action'] == actions.VOTED_CANDIDATE:
        result = get_voted_candidate(user, payload['campaign_id'])
    elif payload['action'] == actions.VOTE:
        result = vote(
            user,
            payload['candidate_id'],
            payload['campaign_id'],
            timestamp,
            payload['comment'] if 'comment' in payload.keys() else None
        )
    elif payload['action'] == actions.CREATE_CAMPAIGN:
        result = create_new_campaign(user, payload, timestamp, payload['token_address'])
    elif payload['action'] == actions.LIST_CAMPAIGN:
        result = all_campaigns(
            payload['page'],
            payload['limit'],
            payload['type'],
            user,
            timestamp,
            payload['my_campaign']
        )
    elif payload['action'] == actions.RESULT:
        result = get_voting_result(user, payload['campaign_id'])
    elif payload['action'] == actions.LIST_VOTER:
        result = list_voter(payload['id'], payload['page'], payload['limit'])
    elif payload['action'] == actions.CANDIDATE_DETAIL:
        result = get_detail_candidate(payload['campaign_id'], payload['candidate_id'])
    elif payload['action'] == actions.EDIT_CAMPAIGN:
        result = edit_campaign(user, payload['id'], timestamp, payload)
    elif payload['action'] == actions.DELETE_CAMPAIGN:
        result = delete_campaign(payload['id'], user, timestamp)
    elif payload['action'] == actions.USER_INFO:
        result = get_user_info(user)
    elif payload['action'] == actions.WITHDRAW:
        amount = int(payload['amount'])
        result = withdraw_money(user, amount / BASE_AMOUNT, timestamp, payload['token_address'])
        if 'error' not in result.keys():
            handle_withdraw_money(user, amount, payload['token_address'])
    elif payload['action'] == actions.SAVE_EXECUTED_VOUCHER:
        result = save_executed_voucher_for_user(
            user,
            payload['id'],
            timestamp,
            payload['amount'],
            payload['token_address']
        )
    elif payload['action'] == actions.LIST_EXECUTED_VOUCHER:
        result = get_executed_vouchers(user)
    elif payload['action'] == actions.ACTION_HISTORY:
        result = get_actions_histories(user, payload['page'], payload['limit'], payload['type'])
    elif payload['action'] == actions.NOTIFICATION:
        result = get_notification(user, payload['page'], payload['limit'])
    elif payload['action'] == actions.LIST_TOKEN:
        result = {'data': list_token()}
    elif payload['action'] == actions.CREATE_PROFILE:
        result = create_profile(user, payload, timestamp)
    elif payload['action'] == actions.UPDATE_PROFILE:
        result = update_profile(user, payload['id'], payload, timestamp)
    elif payload['action'] == actions.DELETE_PROFILE:
        result = delete_profile(user, payload['id'], timestamp)
    elif payload['action'] == actions.LIST_PROFILE:
        if payload['my_profile']:
            result = list_profile_of_user(user, payload['page'], payload['limit'], payload['keyword'])
        else:
            result = list_profile(payload['page'], payload['limit'], payload['keyword'])
    elif payload['action'] == actions.DETAIL_PROFILE:
        result = detail_profile(payload['id'])
    elif payload['action'] == actions.LIST_CAMPAIGN_OF_PROFILE:
        result = list_campaign_of_profile(payload['profile_id'], payload['page'], payload['limit'])
    elif payload['action'] == actions.LIST_PROFILE_OF_CURRENT_USER:
        result = list_profile_of_manager(user)
    elif payload['action'] == actions.JOIN_PROFILE:
        result = join_profile(user, payload['profile_id'], timestamp)
    elif payload['action'] == actions.LEAVE_PROFILE:
        result = leave_profile(user, payload['profile_id'], timestamp)
    else:
        result = handle_admin_action(user, payload, timestamp)

    print(result)
    print("Result type: " + type(result).__name__)

    if 'error' in result.keys():
        action_status = consts.REJECT_STATUS
        hand_result = add_report
    else:
        action_status = consts.ACCEPT_STATUS

    save_notification(user, payload['action'], payload, timestamp, result)
    hand_result(json.dumps(result), action_status)

    return consts.ACCEPT_STATUS


def handle_advance(data):
    print(f"Received advance request body {data}")
    return action_proxy(data)


def handle_inspect(data):
    logger.info(f"Received inspect request data {data}")
    try:
        data = bytes.fromhex(data["payload"][2:]).decode()
        data = json.loads(data)
        print(data)
        return action_proxy(data, True)
    except Exception as e:
        print(e)
        print('Invalid payload inspect')
        add_report(json.dumps({'error': 'Invalid payload inspect'}), consts.REJECT_STATUS)
        return consts.REJECT_STATUS


def handle_deposit_money(payload, sender, timestamp):
    print(f"Received deposit request {payload}")

    try:
        # Check whether an input was sent by the Portal,
        # which is where all deposits must come from
        # if sender != rollup_address:
        #     result = {'error': 'Input does not come from the Portal'}
        #     save_notification(sender, NOTIFICATION_ACTIONS['SYSTEM'], {}, timestamp, result)
        #     return reject_input(json.dumps(result), payload)

        # Attempt to decode input as an ABI-encoded ERC20 deposit
        binary = bytes.fromhex(payload[2:])
        try:
            decoded = decode_abi(['bytes32', 'address', 'address', 'uint256', 'bytes'], binary)
        except Exception as e:
            print(e)
            result = {'error': "Payload does not conform to ERC20 deposit ABI"}
            print(result)
            save_notification(sender, NOTIFICATION_ACTIONS['SYSTEM'], {}, timestamp, result)
            return reject_input(json.dumps(result), payload)

        # Check if the header matches the Keccak256-encoded string "ERC20_Transfer"
        # input_header = decoded[0]
        # if input_header != ERC20_TRANSFER_HEADER:
        #     result = {'error': 'Input header is not from an ERC20 transfer'}
        #     save_notification(sender, NOTIFICATION_ACTIONS['SYSTEM'], {}, timestamp, result)
        #     return reject_input(json.dumps(result), payload)

        user = decoded[1]
        erc20_contract = decoded[2]
        amount = decoded[3]

        result = {'message': f"Deposit received from: {user}; ERC-20: {erc20_contract}; Amount: {amount}"}
        print(f"Adding notice: {json.dumps(result)}")

        if not can_deposit_token(erc20_contract):
            print(f"Token is not acceptable, sending them back")
            handle_withdraw_money(user, amount, erc20_contract)
            result = {'error': "Token is not acceptable, we are sending them back to you as voucher!"}
            save_notification(
                user,
                NOTIFICATION_ACTIONS['DEPOSIT'],
                {'amount': amount, 'token': erc20_contract},
                timestamp,
                result
            )
            reject_input('Invalid token', json.dumps(result))
            return consts.ACCEPT_STATUS

        add_deposit_user(user, amount / BASE_AMOUNT, erc20_contract, timestamp)
        add_notice(json.dumps(result))
        save_notification(
            user,
            NOTIFICATION_ACTIONS['DEPOSIT'],
            {'amount': amount, 'token': erc20_contract},
            timestamp,
            result
        )
        return consts.ACCEPT_STATUS
    except Exception as e:
        print(e)
        return reject_input(f"Error processing data{payload}", payload)


def handle_withdraw_money(user, amount, token):
    # Encode a transfer function call that returns the amount back to the depositor
    print('return amount', amount)
    timestamp = int(datetime.datetime.now().timestamp())
    transfer_payload = \
        TRANSFER_FUNCTION_SELECTOR \
        + encode_abi(['address', 'uint256', 'address', 'uint256'], [user, amount, token, timestamp])
    # Post voucher executing the transfer on the ERC-20 contract: "I don't want your money"!
    voucher = {"address": token, "payload": "0x" + transfer_payload.hex()}
    logger.info(f"Issuing voucher {voucher}")
    res = requests.post(rollup_server + "/voucher", json=voucher)
    logger.info(f"Received voucher status {res.status_code} body {res.content}")


def reject_input(msg, payload):
    print(f"Reject input {msg}")
    add_report(payload, consts.REJECT_STATUS)
    return consts.REJECT_STATUS


handlers = {
    "advance_state": handle_advance,
    "inspect_state": handle_inspect,
}

finish = {"status": "accept"}
rollup_address = None
initialize_tables()

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
