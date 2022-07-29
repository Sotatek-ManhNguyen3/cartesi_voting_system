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
                return {'error': key + 'is required!'}

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
    actions.TOP_CANDIDATES: {
        'quantity': {
            'type': 'int',
            'nullable': True
        },
        'campaign_id': {
            'type': 'int',
            'nullable': False
        }
    },
    actions.VOTE: {
        'candidate_id': {
            'type': 'int',
            'nullable': False
        },
        'campaign_id': {
            'type': 'int',
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
        }
    },
    actions.CHANGE_TIME_CAMPAIGN: {
        'campaign_id': {
            'type': 'int',
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
    },
    actions.ADD_CANDIDATES: {
        'campaign_id': {
            'type': 'int',
            'nullable': False
        },
        'candidates': {
            'type': 'list',
            'nullable': False
        }
    },
    actions.DELETE_CANDIDATE: {
        'campaign_id': {
            'type': 'int',
            'nullable': False
        },
        'candidate_id': {
            'type': 'int',
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
    }
}
