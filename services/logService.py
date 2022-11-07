from constants.historyActions import ACTIONS
from services.dataService import *
import datetime


def log_action(user, action, payload, timestamp):
    log_action_data(user, action, payload, str(datetime.datetime.fromtimestamp(timestamp)))


def format_action_histories(data):
    action_contain_campaign = [
        ACTIONS['CREATE_CAMPAIGN'],
        ACTIONS['VOTE'],
        ACTIONS['EDIT_CAMPAIGN'],
        ACTIONS['DELETE_CAMPAIGN'],
    ]

    result = []

    for log in data:
        payload = json.loads(log['payload'])
        if log['action'] in action_contain_campaign:
            campaign_detail = get_campaign(payload['campaign']['id'])
            print(campaign_detail)

            if len(campaign_detail) != 0:
                payload['campaign'] = campaign_detail[0]

        if 'token' in payload.keys():
            token_info = get_token(payload['token'], None)
            payload['token'] = token_info[0]

        log['payload'] = payload
        log.pop('id', None)
        log.pop('user', None)
        log.pop('time', None)
        result.append(log)

    return result
