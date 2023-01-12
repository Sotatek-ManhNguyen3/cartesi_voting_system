from services.dataService import get_role, create_role, list_role, delete_role, update_role, \
    create_token, update_token, delete_token, get_token, change_status_token, count_active_campaign_by_token, \
    backup_table
from constants import actions
from constants.consts import STATUS_TOKEN
import json


def handle_admin_action(sender, payload, timestamp):
    if not can_execute_action(payload['action'], sender):
        return {'error': 'You do not have permission!'}

    match payload['action']:
        case actions.ADD_ROLE:
            if does_role_exist(payload['user'].lower()):
                return {'error': 'This user is already had a role in this system!'}

            return create_role(
                payload['user'].lower(),
                payload['manage_user'],
                payload['manage_token'],
                payload['manage_post'],
                payload['manage_system']
            )
        case actions.LIST_ROLE:
            return {'data': list_role(payload['roles'] if 'roles' in payload.keys() else [])}
        case actions.DELETE_ROLE:
            return delete_role(payload['user'].lower())
        case actions.UPDATE_ROLE:
            return update_role(
                payload['id'],
                payload['user'].lower(),
                payload['manage_user'],
                payload['manage_token'],
                payload['manage_post'],
                payload['manage_system']
            )
        case actions.ADD_TOKEN:
            if does_token_exist(payload['address'].lower()):
                return {'error': 'This token already exists!'}

            status = payload['status'] if 'status' in payload.keys() else None

            if status not in [STATUS_TOKEN['ACTIVE'], STATUS_TOKEN['LOCKED']]:
                return {'error': 'Invalid token status'}

            delete_token(payload['address'].lower())
            return create_token(
                payload['address'].lower(),
                payload['name'],
                payload['fee'] if 'fee' in payload.keys() else None,
                payload['icon'] if 'icon' in payload.keys() else None,
                status,
                payload['can_vote'] if 'can_vote' in payload.keys() else None,
                payload['can_create_campaign'] if 'can_create_campaign' in payload.keys() else None,
            )
        case actions.DELETE_TOKEN:
            if not can_delete_token(payload['address'].lower(), timestamp):
                return {'error': 'There are on going campaigns using this token. '
                                 'You can lock this token until all the campaigns using this token are ended!'}
            return change_status_token(payload['address'].lower(), STATUS_TOKEN['DISABLED'])
        case actions.UPDATE_TOKEN:
            status = payload['status'] if 'status' in payload.keys() else None
            if status not in [STATUS_TOKEN['ACTIVE'], STATUS_TOKEN['LOCKED']]:
                return {'error': 'Invalid token status'}

            return update_token(
                payload['id'],
                payload['address'].lower(),
                payload['name'],
                payload['fee'] if 'fee' in payload.keys() else None,
                payload['icon'] if 'icon' in payload.keys() else None,
                status,
                payload['can_vote'] if 'can_vote' in payload.keys() else None,
                payload['can_create_campaign'] if 'can_create_campaign' in payload.keys() else None,
            )
        case actions.BACKUP:
            res = backup_table(payload['table'])
            if type(res).__name__ == 'dict':
                return res

            return {'data': list(map(lambda row: json.dumps(row), res))}
        case _:
            return {'error': 'No action founded'}


def does_role_exist(user):
    role = get_role(user)
    return len(role) != 0


def does_token_exist(token):
    token = get_token(token)
    return len(token) != 0


def can_delete_token(token, timestamp):
    count = count_active_campaign_by_token(token, timestamp)[0]['count']
    return count == 0


def can_execute_action(action, user):
    role = get_role(user)
    if len(role) == 0:
        return False

    role = role[0]
    if action in [actions.ADD_ROLE, actions.DELETE_ROLE, actions.UPDATE_ROLE]:
        return role['manage_user'] == 1
    elif action in [actions.ADD_TOKEN, actions.DELETE_TOKEN, actions.UPDATE_TOKEN]:
        return role['manage_token'] == 1
    elif action in [actions.LIST_ROLE, actions.LIST_TOKEN, actions.BACKUP]:
        return True
    else:
        return False
