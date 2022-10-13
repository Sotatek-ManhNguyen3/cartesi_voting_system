from notificationActions import NOTIFICATION_ACTIONS
from dataService import *
BASE_AMOUNT = 1000000000000000000


notification_type = {
    'error': 'error',
    'success': 'success'
}


def save_notification(user, action, request, timestamp, response):
    if action not in NOTIFICATION_ACTIONS.keys():
        return

    time = datetime.datetime.fromtimestamp(timestamp)
    is_error = 'error' in response.keys()
    payload = {
        'type': notification_type['error'] if is_error else notification_type['success'],
        'error': response['error'] if is_error else None,
        'time': str(time)
    }

    if action == NOTIFICATION_ACTIONS['VOTE']:
        campaign = get_campaign(request['campaign_id'])
        payload['campaign'] = None if len(campaign) == 0 else campaign[0]
        candidate = get_candidate(request['candidate_id'], request['campaign_id'])
        payload['candidate'] = None if len(candidate) == 0 else candidate[0]
    elif action == NOTIFICATION_ACTIONS['CREATE_CAMPAIGN']:
        if not is_error:
            payload['campaign'] = response['campaign']
    elif action == NOTIFICATION_ACTIONS['EDIT_CAMPAIGN']:
        campaign = get_campaign(request['id'])
        payload['campaign'] = None if len(campaign) == 0 else campaign[0]
    elif action == NOTIFICATION_ACTIONS['DELETE_CAMPAIGN']:
        campaign = get_campaign(request['id'])
        payload['campaign'] = None if len(campaign) == 0 else campaign[0]
    elif action == NOTIFICATION_ACTIONS['WITHDRAW']:
        payload['amount'] = int(request['amount']) / BASE_AMOUNT
        payload['token'] = request['token_address']
    elif action == NOTIFICATION_ACTIONS['DEPOSIT']:
        payload['amount'] = request['amount'] / BASE_AMOUNT
        payload['token'] = request['token']
    elif action == NOTIFICATION_ACTIONS['DECREASE_TOKEN']:
        payload['amount'] = request['amount'] / BASE_AMOUNT
        payload['token'] = request['token']

    save_notification_data(user, action, json.dumps(payload), str(time), 'error' if is_error else 'success')
    remove_notification_data(user)
