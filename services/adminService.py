from services.dataService import get_role, create_role, list_role, delete_role, update_role, \
    create_token, update_token, delete_token, list_token
from constants import actions


def handle_admin_action(sender, payload):
    if not can_execute_action(payload['action'], sender):
        return {'error': 'You do not have permission!'}

    if payload['action'] == actions.ADD_ROLE:
        if does_role_exist(payload['user'].lower()):
            return {'error': 'This user is already had a role in this system!'}

        return create_role(
            payload['user'].lower(),
            payload['manage_user'],
            payload['manage_token'],
            payload['manage_post'],
            payload['manage_system']
        )
    elif payload['action'] == actions.LIST_ROLE:
        return {'data': list_role(payload['roles'] if 'roles' in payload.keys() else [])}
    elif payload['action'] == actions.DELETE_ROLE:
        return delete_role(payload['user'].lower())
    elif payload['action'] == actions.UPDATE_ROLE:
        return update_role(
            payload['id'],
            payload['user'].lower(),
            payload['manage_user'],
            payload['manage_token'],
            payload['manage_post'],
            payload['manage_system']
        )
    elif payload['action'] == actions.ADD_TOKEN:
        return create_token(
            payload['address'].lower(),
            payload['name'],
            payload['fee']
        )
    elif payload['action'] == actions.DELETE_TOKEN:
        return delete_token(payload['address'].lower())
    elif payload['action'] == actions.LIST_TOKEN:
        return {'data': list_token()}
    elif payload['action'] == actions.UPDATE_TOKEN:
        return update_token(
            payload['id'],
            payload['address'].lower(),
            payload['name'],
            payload['fee']
        )
    else:
        return {'error': 'No action founded'}


def does_role_exist(user):
    role = get_role(user)
    return len(role) is not 0


def can_execute_action(action, user):
    role = get_role(user)
    if len(role) == 0:
        return False

    role = role[0]
    if action in [actions.ADD_ROLE, actions.DELETE_ROLE, actions.UPDATE_ROLE]:
        return role['manage_user'] == 1
    elif action in [actions.ADD_TOKEN, actions.DELETE_TOKEN, actions.UPDATE_TOKEN]:
        return role['manage_token'] == 1
    elif action in [actions.LIST_ROLE, actions.LIST_TOKEN]:
        return True
    else:
        return False
