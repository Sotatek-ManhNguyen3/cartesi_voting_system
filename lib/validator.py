from constants import actions
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
                print('NOTICE EXCEPTION' + e.__str__())
                return {'error': 'Invalid datetime format ' + key}

        if rules[key]['type'] == 'number' and is_number(data):
            continue

        if type(data).__name__ != rules[key]['type']:
            return {'error': 'Invalid type of ' + key
                             + '. It must be ' + rules[key]['type'] + '. ' + type(data).__name__ + ' given!'}

    return {'message': 'passed'}


def is_number(variable):
    return type(variable).__name__ in ['int', 'float']


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
        'comment': {
            'type': 'str',
            'nullable': True,
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
        },
        'accept_token': {
            'type': 'str',
            'nullable': False
        },
        'fee': {
            'type': 'number',
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
        },
        'accept_token': {
            'type': 'str',
            'nullable': False
        },
        'fee': {
            'type': 'number',
            'nullable': False
        }
    },
    actions.DELETE_CAMPAIGN: {
        'id': {
            'type': 'int',
            'nullable': False
        },
    },
    actions.USER_INFO: {},
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
            'type': 'number',
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
    actions.ADD_ROLE: {
        'user': {
            'type': 'str',
            'nullable': False
        },
        'manage_user': {
            'type': 'int',
            'nullable': False
        },
        'manage_token': {
            'type': 'int',
            'nullable': False
        },
        'manage_post': {
            'type': 'int',
            'nullable': False
        },
        'manage_system': {
            'type': 'int',
            'nullable': False
        }
    },
    actions.LIST_ROLE: {
        'roles': {
            'type': 'list',
            'nullable': True
        }
    },
    actions.DELETE_ROLE: {
        'user': {
            'type': 'str',
            'nullable': False
        }
    },
    actions.UPDATE_ROLE: {
        'user': {
            'type': 'str',
            'nullable': False
        },
        'manage_user': {
            'type': 'int',
            'nullable': False
        },
        'manage_token': {
            'type': 'int',
            'nullable': False
        },
        'manage_post': {
            'type': 'int',
            'nullable': False
        },
        'manage_system': {
            'type': 'int',
            'nullable': False
        },
        'id': {
            'type': 'int',
            'nullable': False
        }
    },
    actions.ADD_TOKEN: {
        'address': {
            'type': 'str',
            'nullable': False
        },
        'name': {
            'type': 'str',
            'nullable': False
        },
        'fee': {
            'type': 'number',
            'nullable': False
        },
        'icon': {
            'type': 'str',
            'nullable': True,
        },
        'status': {
            'type': 'int',
            'nullable': True,
        },
        'can_vote': {
            'type': 'int',
            'nullable': False,
        },
        'can_create_campaign': {
            'type': 'int',
            'nullable': False,
        }
    },
    actions.LIST_TOKEN: {},
    actions.DELETE_TOKEN: {
        'address': {
            'type': 'str',
            'nullable': False
        }
    },
    actions.UPDATE_TOKEN: {
        'address': {
            'type': 'str',
            'nullable': False
        },
        'name': {
            'type': 'str',
            'nullable': False
        },
        'fee': {
            'type': 'number',
            'nullable': False
        },
        'id': {
            'type': 'int',
            'nullable': False
        }
    },
    actions.BACKUP: {
        'table': {
            'type': 'str',
            'nullable': False
        }
    },
    actions.LIST_VOTER: {
        'id': {
            'type': 'int',
            'nullable': False
        },
        'page': {
            'type': 'int',
            'nullable': False
        },
        'limit': {
            'type': 'int',
            'nullable': False
        },
    },
    actions.CREATE_PROFILE: {
        'name': {
            'type': 'str',
            'nullable': False
        },
        'description': {
            'type': 'str',
            'nullable': False
        },
        'website': {
            'type': 'str',
            'nullable': True
        },
        'social_media': {
            'type': 'str',
            'nullable': True
        },
        'thumbnail': {
            'type': 'str',
            'nullable': False
        },
        'managers': {
            'type': 'list',
            'nullable': False
        }
    },
    actions.UPDATE_PROFILE: {
        'name': {
            'type': 'str',
            'nullable': False
        },
        'description': {
            'type': 'str',
            'nullable': False
        },
        'website': {
            'type': 'str',
            'nullable': True
        },
        'social_media': {
            'type': 'str',
            'nullable': True
        },
        'thumbnail': {
            'type': 'str',
            'nullable': False
        },
        'managers': {
            'type': 'list',
            'nullable': False
        },
        'id': {
            'type': 'int',
            'nullable': False
        }
    },
    actions.DELETE_PROFILE: {
        'id': {
            'type': 'int',
            'nullable': False
        }
    },
    actions.LIST_PROFILE_OF_USER: {
        'user': {
            'type': 'str',
            'nullable': False
        }
    },
    actions.DETAIL_PROFILE: {
        'id': {
            'type': 'int',
            'nullable': False
        }
    }
}

ALLOWED_ACTIONS_INSPECT = [
    actions.CAMPAIGN_DETAIL,
    actions.VOTED_CANDIDATE,
    actions.LIST_CAMPAIGN,
    actions.RESULT,
    actions.LIST_VOTER,
    actions.CANDIDATE_DETAIL,
    actions.USER_INFO,
    actions.LIST_EXECUTED_VOUCHER,
    actions.ACTION_HISTORY,
    actions.NOTIFICATION,
    actions.LIST_TOKEN,
    actions.LIST_ROLE,
    actions.BACKUP,
    actions.LIST_PROFILE_OF_USER,
    actions.DETAIL_PROFILE
]
