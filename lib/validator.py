import actions
from lib.helpers import get_date_time_from_string


def validator(variable, rules):
    field_keys = rules.keys()
    var_keys = variable.keys()

    for key in field_keys:
        if key not in var_keys:
            if rules[key]['nullable']:
                continue
            else:
                return {'error': key + ' is required!'}

        data = variable[key]

        if rules[key]['type'] == 'datetime':
            try:
                get_date_time_from_string(data)
                continue
            except Exception as e:
                print("NOTICE EXCEPTION" + e.__str__())
                return {'error': 'Invalid datetime format ' + key}

        if type(data).__name__ != rules[key]['type']:
            return {'error': 'Invalid type of ' + key
                             + '. It must be ' + rules[key]['type'] + '. ' + type(data).__name__ + ' given!'}

    return {'message': 'passed'}


VALIDATE_RULES = {
    actions.CAMPAIGN_DETAIL: {
        'campaign_id': {
            'type': 'int',
            'nullable': False
        }
    },
    actions.VOTED_CANDIDATE: {
        'campaign_id': {
            'type': 'int',
            'nullable': False
        },
    },
    actions.VOTE: {
        'candidate_id': {
            'type': 'int',
            'nullable': False
        },
        'campaign_id': {
            'type': 'int',
            'nullable': False
        },
        'token_address': {
            'type': 'str',
            'nullable': False
        }
    },
    actions.CREATE_CAMPAIGN: {
        'name': {
            'type': 'str',
            'nullable': False
        },
        'description': {
            'type': 'str',
            'nullable': False
        },
        'start_time': {
            'type': 'datetime',
            'nullable': False
        },
        'end_time': {
            'type': 'datetime',
            'nullable': False
        },
        'candidates': {
            'type': 'list',
            'nullable': False
        },
        'token_address': {
            'type': 'str',
            'nullable': False
        }
    },
    actions.RESULT: {
        'campaign_id': {
            'type': 'int',
            'nullable': False
        },
    },
    actions.CANDIDATE_DETAIL: {
        'campaign_id': {
            'type': 'int',
            'nullable': False
        },
        'candidate_id': {
            'type': 'int',
            'nullable': False
        },
    },
    actions.LIST_CAMPAIGN: {
        'page': {
            'type': 'int',
            'nullable': False
        },
        'limit': {
            'type': 'int',
            'nullable': False
        },
        'type': {
            'type': 'str',
            'nullable': False
        },
        'my_campaign': {
            'type': 'bool',
            'nullable': False
        }
    },
    actions.EDIT_CAMPAIGN: {
        'name': {
            'type': 'str',
            'nullable': False
        },
        'id': {
            'type': 'int',
            'nullable': False
        },
        'description': {
            'type': 'str',
            'nullable': False
        },
        'start_time': {
            'type': 'datetime',
            'nullable': False
        },
        'end_time': {
            'type': 'datetime',
            'nullable': False
        },
        'candidates': {
            'type': 'list',
            'nullable': False
        }
    },
    actions.DELETE_CAMPAIGN: {
        'id': {
            'type': 'int',
            'nullable': False
        },
    },
    actions.DEPOSIT_INFO: {},
    actions.WITHDRAW: {
        'amount': {
            'type': 'str',
            'nullable': False
        },
        'token_address': {
            'type': 'str',
            'nullable': False
        }
    },
    actions.SAVE_EXECUTED_VOUCHER: {
        'id': {
            'type': 'str',
            'nullable': False
        },
        'amount': {
            'type': 'int',
            'nullable': False
        },
        'token_address': {
            'type': 'str',
            'nullable': False
        }
    },
    actions.LIST_EXECUTED_VOUCHER: {},
    actions.ACTION_HISTORY: {
        'page': {
            'type': 'int',
            'nullable': False
        },
        'limit': {
            'type': 'int',
            'nullable': False
        },
        'type': {
            'type': 'str',
            'nullable': False
        },
    },
    actions.NOTIFICATION: {
        'page': {
            'type': 'int',
            'nullable': False
        },
        'limit': {
            'type': 'int',
            'nullable': False
        },
    },
}

ALLOWED_ACTIONS_INSPECT = [
    actions.CAMPAIGN_DETAIL,
    actions.VOTED_CANDIDATE,
    actions.LIST_CAMPAIGN,
    actions.RESULT,
    actions.CANDIDATE_DETAIL,
    actions.DEPOSIT_INFO,
    actions.LIST_EXECUTED_VOUCHER,
    actions.ACTION_HISTORY,
    actions.NOTIFICATION,
]
