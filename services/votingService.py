from constants.historyActions import ACTIONS
from services.dataService import *
from lib.helpers import get_date_time_from_string
from services.logService import log_action, format_action_histories
from constants import metadata

BASE_AMOUNT = 1000000000000000000


def is_valid_token(token_address):
    token = get_token(token_address)
    return len(token) != 0


def get_fee(token_address):
    token = get_token(token_address)
    if len(token) == 0:
        return metadata.DEFAULT_FEE_IN_SYSTEM

    return token[0]['fee']


def get_notification(user, page, limit):
    return get_notifications_data(user, page, limit)


def get_actions_histories(user, page, limit, action='all'):
    if not (action == 'all' or action in ACTIONS.keys()):
        return {'error': 'Invalid action'}

    data = get_action_histories_data(user, page, limit, action)
    data['data'] = format_action_histories(data['data'])
    return data


def get_executed_vouchers(user):
    result = list_executed_vouchers(user)
    ids = []
    for voucher in result:
        ids.append(voucher['voucher_id'])

    return {'ids': ids}


def save_executed_voucher_for_user(user, voucher_id, timestamp, amount, token):
    save_executed_voucher(user, voucher_id)
    # Log execute voucher
    log_action(user, ACTIONS['EXECUTE_VOUCHER'], {
        'voucher_id': voucher_id,
        'token': token,
        'amount': amount,
        'time': str(datetime.datetime.fromtimestamp(timestamp))
    }, timestamp)

    return {'message': 'Save successfully'}


def withdraw_money(user, amount, timestamp, token):
    is_enough_money = do_user_have_enough_money(user, token, amount)

    if not is_enough_money:
        return {'error': 'You do not have enough token!'}

    withdraw_money_from_user(user, amount, token)

    # Log withdraw money
    log_action(user, ACTIONS['WITHDRAW'], {
        'amount': amount,
        'toke': token,
        'time': str(datetime.datetime.fromtimestamp(timestamp))
    }, timestamp)

    return {'message': 'Withdraw money successfully!'}


def withdraw_money_from_user(user, amount, token):
    return update_withdrawn_amount_user(user, amount, token)


def deduct_money_from_user(user, token, amount=metadata.DEFAULT_FEE_IN_SYSTEM):
    return update_used_amount_user(user, token, amount)


def do_user_have_enough_money(user, token, amount=None):
    amount = get_fee(token) if amount is None else amount
    deposit_info = get_deposit_info_of_token(user, token)
    if len(deposit_info) == 0:
        return False

    deposit_info = deposit_info[0]
    remain_amount = deposit_info['amount'] - deposit_info['used_amount'] - deposit_info['withdrawn_amount']
    return remain_amount >= amount


def get_user_info(user):
    return {
        'deposit_info': get_deposit_info(user),
        'is_admin': len(get_role(user)) != 0
    }


def delete_campaign(campaign_id, user, timestamp):
    can_delete = can_change_campaign_info(user, campaign_id, timestamp)

    if 'error' in can_delete.keys():
        return can_delete

    delete_all_candidates_of_campaign(campaign_id)

    # Log delete campaign
    log_action(user, ACTIONS['DELETE_CAMPAIGN'], {
        'campaign': get_campaign(campaign_id)[0],
        'time': str(datetime.datetime.fromtimestamp(timestamp))
    }, timestamp)

    delete_campaign_info(campaign_id)

    return {'message': 'Delete campaign successfully'}


# Get detail of a candidate
def get_detail_candidate(campaign_id, candidate_id):
    return {
        'candidate': detail_candidate(campaign_id, candidate_id)
    }


# Get voting result
# Return voted candidate and result
def get_voting_result(user, campaign_id):
    voted = voted_candidate(user, campaign_id)

    return {
        'total_vote': get_total_vote_of_campaign(campaign_id),
        'voted_candidate': None if 'error' in voted.keys() else voted,
        'campaign': voting_result(campaign_id)
    }


# Add deposit money for user
def add_deposit_user(user, amount, token, timestamp):
    deposit_info = get_deposit_info_of_token(user, token)

    if len(deposit_info) == 0:
        create_deposit_info(user, amount, token)
    else:
        update_deposit_amount(user, amount, token)

    # Log deposit
    log_action(user, ACTIONS['DEPOSIT'], {
        'amount': amount,
        'token': token,
        'time': str(datetime.datetime.fromtimestamp(timestamp))
    }, timestamp)

    return True


# Vote for a candidate
# Rules:
# Only user with free coin greater than the config fee can vote
# User can only vote for 1 candidate per 1 campaign
# Can not vote if the time vote is not in the acceptable time range
def vote(user, candidate_id, campaign_id, token_address, timestamp):
    if not is_valid_token(token_address):
        return {'error': 'Token is invalid'}

    # Validate campaign and valid time to vote
    campaign = get_campaign(campaign_id)

    if len(campaign) == 0:
        return {'error': 'Campaign does not exist'}

    # Validate if the user has deposit asset or not
    deposit_info = get_deposit_info(user)
    if len(deposit_info) == 0:
        return {'error': 'You need to deposit to the system before voting!'}

    campaign = campaign[0]
    start_time = get_date_time_from_string(campaign['start_time'])
    end_time = get_date_time_from_string(campaign['end_time'])
    now = datetime.datetime.fromtimestamp(timestamp)
    if now.__lt__(start_time) or now.__gt__(end_time):
        return {'error': 'This campaign is closed for voting'}

    # Validate candidate
    candidate = get_candidate(candidate_id, campaign_id)
    if len(candidate) == 0:
        return {'error': 'Invalid candidate id'}

    # Validate voted candidate
    voted = voted_candidate(user, campaign_id)
    if 'error' not in voted.keys():
        return {'error': 'You can only vote for one candidate'}

    # Validate money
    have_enough_money = do_user_have_enough_money(user, token_address)
    if not have_enough_money:
        return {'error': f'You do not have enough coin to vote! You need at least {get_fee(token_address)} unused coin!'}

    # Vote
    result = vote_candidate(user, candidate_id, campaign_id)
    if 'error' in result.keys():
        return result

    # Log vote
    log_action(user, ACTIONS['VOTE'], {
        'campaign': campaign,
        'candidate': candidate[0],
        'time': str(now)
    }, timestamp)

    deduct_money_from_user(user, token_address, get_fee(token_address))
    # Log deduct money
    log_action(user, ACTIONS['DECREASE_TOKEN'], {
        'amount': get_fee(token_address),
        'token': token_address,
        'time': str(datetime.datetime.fromtimestamp(timestamp)),
        'reason': 'you voted for a candidate'
    }, timestamp)

    # Increase vote in candidates table
    return increase_votes(candidate_id, campaign_id)


# Create new campaign
def create_new_campaign(creator, payload, timestamp, token_address):
    try:
        if not is_valid_token(token_address):
            return {'error': 'Token is invalid'}

        if type(payload['candidates']) is not list:
            return {'error': 'Wrong input format'}

        # Validate money
        have_enough_money = do_user_have_enough_money(creator, token_address)
        if not have_enough_money:
            return {'error': f'You do not have enough coin to vote! You need at least {get_fee(token_address)} unused coin!'}

        campaign = create_campaign(creator, payload['description'],
                                   payload['start_time'], payload['end_time'], payload['name'])

        if 'error' in campaign.keys():
            return {'error': campaign}

        candidates = []
        for candidate in payload['candidates']:
            candidates.append([
                candidate['name'],
                campaign['id'],
                candidate['brief_introduction'] if 'brief_introduction' in candidate.keys() else '',
                candidate['avatar']
            ])

        add_candidates(candidates)

        # Log create campaign
        log_action(creator, ACTIONS['CREATE_CAMPAIGN'], {
            'campaign': campaign['campaign'],
            'time': str(datetime.datetime.fromtimestamp(timestamp))
        }, timestamp)

        deduct_money_from_user(creator, token_address, get_fee(token_address))

        # Log deduct money
        log_action(creator, ACTIONS['DECREASE_TOKEN'], {
            'amount': get_fee(token_address),
            'token': token_address,
            'time': str(datetime.datetime.fromtimestamp(timestamp)),
            'reason': 'create campaign'
        }, timestamp)

        return campaign
    except KeyError as e:
        result = "EXCEPTION: " + e.__str__()
        print("NOTICE EXCEPTION" + e.__str__())
        return {'error': result}


# Get voted candidate for a campaign
def get_voted_candidate(user, campaign_id):
    campaign = get_campaign(campaign_id)
    if len(campaign) == 0:
        return {'error': 'Campaign does not exist'}

    return voted_candidate(user, campaign_id)


# Edit existing campaign
# Rules:
# Only the creator of the campaign can edit
# Can not edit campaign info if the campaign is running
def edit_campaign(user_change, campaign_id, timestamp, payload):
    can_change_campaign = can_change_campaign_info(user_change, campaign_id, timestamp)

    if 'error' in can_change_campaign.keys():
        return can_change_campaign

    update_campaign_info(campaign_id, payload['name'], payload['description'], payload['start_time'],
                         payload['end_time'])
    delete_all_candidates_of_campaign(campaign_id)
    add_candidates_to_database(campaign_id, payload['candidates'])

    # Log edit campaign
    log_action(user_change, ACTIONS['EDIT_CAMPAIGN'], {
        'campaign': get_campaign(campaign_id)[0],
        'time': str(datetime.datetime.fromtimestamp(timestamp))
    }, timestamp)

    return {'message': 'Update campaign successfully'}


def can_change_campaign_info(user_change, campaign_id, timestamp):
    campaign = get_campaign(campaign_id)
    if len(campaign) == 0:
        return {'error': 'Campaign does not exist!'}

    if campaign[0]['creator'] != user_change:
        return {'error': 'You do not have the permission!'}

    # If the campaign is already started, then user can not change the campaign info
    start_time = get_date_time_from_string(campaign[0]['start_time'])
    now = datetime.datetime.fromtimestamp(timestamp)
    if now.__gt__(start_time):
        return {'error': 'You can not change the on going campaign!'}

    return {'message': True}


def add_candidates_to_database(campaign_id, candidates):
    converted_data = []
    for candidate in candidates:
        converted_data.append([
            candidate['name'],
            campaign_id,
            candidate['brief_introduction'] if 'brief_introduction' in candidate.keys() else '',
            candidate['avatar'] if 'avatar' in candidate.keys() else '',
        ])

    return add_candidates(converted_data)


def initialize_tables():
    create_base_tables()


def get_campaign_detail(user, campaign_id):
    voted = voted_candidate(user, campaign_id)
    return {
        'candidates': list_all_candidates(campaign_id),
        'campaign': get_campaign(campaign_id),
        'voted': None if 'error' in voted.keys() else voted
    }


def all_campaigns(page, limit, condition, user, timestamp, my_campaign):
    time = datetime.datetime.fromtimestamp(timestamp)
    return list_campaign(page, limit, condition, user, time, my_campaign)


def to_hex(value):
    return "0x" + value.encode().hex()
