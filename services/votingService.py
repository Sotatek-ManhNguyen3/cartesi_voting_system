from constants.historyActions import ACTIONS
from services.dataService import *
from lib.helpers import get_date_time_from_string, get_var, remove_duplicate, get_date_time_from_timestamp
from services.logService import log_action, format_action_histories
from constants import metadata, consts
import json

BASE_AMOUNT = 1000000000000000000


# ============================================== Profile ==============================================
def create_profile(user, payload, timestamp):
    time = get_date_time_from_timestamp(timestamp)
    res = create_profile_data(
        user,
        payload['name'],
        payload['description'],
        get_var(payload, 'website'),
        json.dumps(get_var(payload, 'social_media')),
        payload['thumbnail'],
        consts.PROFILE_TYPE['ORG']
    )

    managers = [user.lower()]
    for manager in payload['managers']:
        managers.append(manager.strip().lower())

    create_profile_managers(res['id'], remove_duplicate(managers))
    users_join_profile(res['id'], remove_duplicate(managers), time)

    # Log action create profile
    log_action(user, ACTIONS['CREATE_PROFILE'], {
        'profile': get_detail_profile_data(res['id']),
        'time': time
    }, timestamp)

    return res


def update_profile(editor, profile_id, payload, timestamp):
    time = get_date_time_from_timestamp(timestamp)
    profile = get_detail_profile_data(profile_id)

    if profile is None:
        return {'error': 'Profile not found!'}

    old_managers = list(map(lambda data: data['user'], get_managers_of_profile(profile_id)))

    # Validate if the editor is manager of the profile
    if editor not in old_managers:
        return {'error': 'You can not edit this profile'}

    # Update profile data
    update_profile_data(
        profile_id,
        payload['name'],
        payload['description'],
        get_var(payload, 'website'),
        json.dumps(get_var(payload, 'social_media')),
        payload['thumbnail']
    )

    # Remove old new_managers from list follower of profile
    delete_user_profile_by_users(old_managers)

    # Remove old new_managers
    delete_profile_managers(profile_id)
    new_managers = [profile['creator'].lower()]
    for manager in payload['managers']:
        new_managers.append(manager.lower())

    # Add new managers of profile
    create_profile_managers(profile['id'], remove_duplicate(new_managers))

    # Add new managers as followers of profile
    users_join_profile(profile['id'], new_managers, time)

    # Log action update profile
    log_action(editor, ACTIONS['UPDATE_PROFILE'], {
        'profile': profile,
        'time': time
    }, timestamp)

    return {'message': 'Update profile info successfully'}


def delete_profile(user, profile_id, timestamp):
    profile = get_detail_profile_data(profile_id)

    if profile is None:
        return {'error': 'Profile not found!'}

    managers = list(map(lambda data: data['user'], get_managers_of_profile(profile_id)))

    if user not in managers:
        return {'error': 'You can not delete this profile!'}

    count = count_campaign_of_profile(profile_id)

    if count > 0:
        return {'error': 'You can not delete this profile because it contains campaigns!'}

    # Log action delete profile
    log_action(user, ACTIONS['DELETE_PROFILE'], {
        'profile': profile,
        'time': get_date_time_from_timestamp(timestamp)
    }, timestamp)

    delete_profile_data(profile_id)
    return {
        'message': f'Delete profile {profile["name"]} successfully!',
        'profile': profile
    }


def detail_profile(profile_id, user):
    profile = get_detail_profile_data(profile_id)

    if profile is None:
        return {'error': 'Profile not found!'}

    profile['managers'] = list(map(lambda data: data['user'], get_managers_of_profile(profile_id)))
    profile['has_joined'] = get_user_profile(user, profile_id) is not None
    return profile


def get_profile_default_of_user(user):
    profile = get_profile_default_of_user_data(user)

    if profile is not None:
        return profile

    create_profile_data(user, user, 'Default profile', None, None, '', consts.PROFILE_TYPE['USER'])
    profile = get_profile_default_of_user_data(user)
    create_profile_managers(profile['id'], [user])

    return profile


def is_manager_of_profile(user, profile_id):
    managers = list(map(lambda item: item['user'], get_managers_of_profile(profile_id)))

    return user in managers


def list_profile_of_manager(manager):
    profile_ids = list_profile_id_of_user_data(manager, True)

    return {
        'data': list_profile_from_ids(profile_ids)
    }


def join_profile(user, profile_id, timestamp):
    # Check if profile exists
    profile = get_detail_profile_data(profile_id, True)

    if profile is None:
        return {'error': 'Invalid profile!'}

    # Check if user already joined this profile
    user_profile = get_user_profile(user, profile_id)

    if user_profile is not None:
        return {'error': 'You joined this profile before!'}

    user_join_profile(user, profile_id, timestamp)

    # Save log action
    log_action(user, ACTIONS['JOIN_PROFILE'], {
        'profile': profile,
        'time': get_date_time_from_timestamp(timestamp)
    }, timestamp)

    return {'message': f'You successfully joined profile {profile["name"]}'}


def leave_profile(user, profile_id, timestamp):
    # Check if profile exists
    profile = get_detail_profile_data(profile_id, True)

    if profile is None:
        return {'error': 'Invalid profile!'}

    # Check if user already joined this profile
    user_profile = get_user_profile(user, profile_id)

    if user_profile is None:
        return {'error': 'You haven\'t join this profile yet!'}

    # Check if that user is manager of profile
    managers = list(map(lambda row: row['user'], get_managers_of_profile(profile_id)))
    if user in managers:
        return {'error': 'You are the manager of this profile. '
                         'You can not unjoin this profile unless you are removed from list managers'}

    user_leave_profile(user, profile_id)

    # Save log action
    log_action(user, ACTIONS['LEAVE_PROFILE'], {
        'profile': profile,
        'time': get_date_time_from_timestamp(timestamp)
    }, timestamp)

    return {'message': f'You left profile {profile["name"]}!'}


def can_deposit_token(token_address):
    token = get_token_can_deposit(token_address)
    return len(token) != 0


def get_fee(token_address, status=STATUS_TOKEN['ACTIVE']):
    token = get_token(token_address, status)
    if len(token) == 0:
        return metadata.DEFAULT_FEE_IN_SYSTEM

    return token[0]['fee']


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
        'time': get_date_time_from_timestamp(timestamp)
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
        'token': token,
        'time': get_date_time_from_timestamp(timestamp)
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
    role = get_role(user)
    return {
        'deposit_info': get_deposit_info(user),
        'is_admin': len(role) != 0,
        'role': None if len(role) == 0 else role[0]
    }


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
        'time': get_date_time_from_timestamp(timestamp)
    }, timestamp)

    return True


# Vote for a candidate
# Rules:
# Only user with free coin greater than the config fee can vote
# User can only vote for 1 candidate per 1 campaign
# Can not vote if the time vote is not in the acceptable time range
def vote(user, candidate_id, campaign_id, timestamp, comment=None):
    # Validate campaign and valid time to vote
    campaign = get_campaign(campaign_id)

    if len(campaign) == 0:
        return {'error': 'Campaign does not exist'}

    # Validate if the user has deposit asset or not
    deposit_info = get_deposit_info(user)
    if len(deposit_info) == 0:
        return {'error': 'You need to deposit to the system before voting!'}

    campaign = campaign[0]

    # Validate whether user join profile or not
    if campaign['profile_type'] == consts.PROFILE_TYPE['ORG'] \
            and not does_user_belong_to_profile(user, campaign['profile_id']):
        return {'error': 'You have to join profile before voting!'}

    token_address = campaign['accept_token']
    fee = campaign['fee']

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
    have_enough_money = do_user_have_enough_money(user, token_address, fee)
    if not have_enough_money:
        return {'error': f'You do not have enough coin to vote! '
                         f'You need at least {fee} unused coin!'}

    # Vote
    result = vote_candidate(user, candidate_id, campaign_id, comment, timestamp)
    if 'error' in result.keys():
        return result

    # Log vote
    log_action(user, ACTIONS['VOTE'], {
        'campaign': campaign,
        'candidate': candidate[0],
        'time': str(now),
        'comment': comment
    }, timestamp)

    deduct_money_from_user(user, token_address, fee)
    # Log deduct money
    log_action(user, ACTIONS['DECREASE_TOKEN'], {
        'amount': fee,
        'token': token_address,
        'time': get_date_time_from_timestamp(timestamp),
        'reason': 'you voted for a candidate'
    }, timestamp)

    # Increase vote in candidates table
    return increase_votes(candidate_id, campaign_id)


def does_user_belong_to_profile(user, profile_id):
    if get_user_profile(user, profile_id) is None:
        return False

    return True


# =========================================== Campaign ===========================================
# Create new campaign
def create_new_campaign(creator, payload, timestamp, token_address):
    try:
        if not can_use_token_to_create_campaign(token_address):
            return {'error': f'Can not use token {token_address} to create campaign!'}

        if not can_use_token_to_vote(payload['accept_token']):
            return {'error': f'Can not use token {payload["accept_token"]} to vote!'}

        if type(payload['candidates']) is not list:
            return {'error': 'Wrong input format'}

        profile_id = get_var(payload, 'profile_id')
        if profile_id is None:
            profile_id = get_profile_default_of_user(creator)['id']
        else:
            if not is_manager_of_profile(creator, profile_id):
                return {'error': 'You dont have permission to create campaign in this profile!'}

        profile = get_detail_profile_data(profile_id)

        # Validate money
        create_fee = get_fee(token_address, None)
        have_enough_money = do_user_have_enough_money(creator, token_address, create_fee)
        if not have_enough_money:
            return {'error': f'You do not have enough coin to vote! '
                             f'You need at least {create_fee} unused coin!'}

        campaign = create_campaign(
            creator,
            payload['description'],
            payload['start_time'],
            payload['end_time'],
            payload['name'],
            payload['accept_token'],
            payload['fee'],
            profile_id,
            profile['type']
        )

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
            'time': get_date_time_from_timestamp(timestamp)
        }, timestamp)

        deduct_money_from_user(creator, token_address, create_fee)

        # Log deduct money
        log_action(creator, ACTIONS['DECREASE_TOKEN'], {
            'amount': create_fee,
            'token': token_address,
            'time': get_date_time_from_timestamp(timestamp),
            'reason': 'create campaign'
        }, timestamp)

        return campaign
    except KeyError as e:
        result = "EXCEPTION: " + e.__str__()
        print("NOTICE EXCEPTION" + e.__str__())
        return {'error': result}


def delete_campaign(campaign_id, user, timestamp):
    can_delete = can_change_campaign_info(user, campaign_id, timestamp)

    if 'error' in can_delete.keys():
        return can_delete

    delete_all_candidates_of_campaign(campaign_id)

    # Log delete campaign
    log_action(user, ACTIONS['DELETE_CAMPAIGN'], {
        'campaign': get_campaign(campaign_id)[0],
        'time': get_date_time_from_timestamp(timestamp)
    }, timestamp)

    campaign = get_campaign(campaign_id)[0]
    delete_campaign_info(campaign_id)

    return {
        'message': f'Delete campaign {campaign["name"]} successfully',
        'campaign': campaign
    }


def can_use_token_to_vote(token):
    token = check_token_can_vote(token)
    return len(token) != 0


def can_use_token_to_create_campaign(token):
    token = check_token_can_create_campaign(token)
    return len(token) != 0


# Get voted candidate for a campaign
def get_voted_candidate(user, campaign_id):
    campaign = get_campaign(campaign_id)
    if len(campaign) == 0:
        return {'error': 'Campaign does not exist'}

    return voted_candidate(user, campaign_id)


# Edit existing campaign
# Rules:
# Only the managers of the profile of the campaign can edit
# Can not edit campaign info if the campaign is running
def edit_campaign(user_change, campaign_id, timestamp, payload):
    can_change_campaign = can_change_campaign_info(user_change, campaign_id, timestamp)

    if 'error' in can_change_campaign.keys():
        return can_change_campaign

    if not can_use_token_to_vote(payload['accept_token']):
        return {'error': f'Can not use token {payload["accept_token"]} to vote!'}

    # Validate new profile id
    profile_id = get_var(payload, 'profile_id')
    if profile_id is None:
        profile_id = get_profile_default_of_user(user_change)['id']
    else:
        if not is_manager_of_profile(user_change, profile_id):
            return {'error': 'You dont have permission to create campaign in this profile!'}

    profile = get_detail_profile_data(profile_id)

    update_campaign_info(
        campaign_id,
        payload['name'],
        payload['description'],
        payload['start_time'],
        payload['end_time'],
        payload['accept_token'],
        payload['fee'],
        profile_id,
        profile['type']
    )
    # Delete old candidates and recreate with new data
    delete_all_candidates_of_campaign(campaign_id)
    add_candidates_to_database(campaign_id, payload['candidates'])

    # Log edit campaign
    log_action(user_change, ACTIONS['EDIT_CAMPAIGN'], {
        'campaign': get_campaign(campaign_id)[0],
        'time': get_date_time_from_timestamp(timestamp)
    }, timestamp)

    return {'message': 'Update campaign successfully'}


# Validate if a user can change campaign info
def can_change_campaign_info(user_change, campaign_id, timestamp):
    campaign = get_campaign(campaign_id)
    if len(campaign) == 0:
        return {'error': 'Campaign does not exist!'}

    campaign = campaign[0]

    if campaign['creator'] != user_change:
        return {'error': 'You do not have the permission!'}

    # If the campaign is already started, then user can not change the campaign info
    start_time = get_date_time_from_string(campaign['start_time'])
    now = datetime.datetime.fromtimestamp(timestamp)
    if now.__gt__(start_time):
        return {'error': 'You can not change the on going campaign!'}

    # Validate if user_change is manager of linked profile
    if campaign['profile_type'] == consts.PROFILE_TYPE['USER']:
        if campaign['creator'] != user_change:
            return {'error': 'You do not have the permission!'}
    elif campaign['profile_id'] not in list_profile_id_of_user_data(user_change):
        return {'error': 'You do not have the permission!'}

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
    campaign = get_campaign(campaign_id)
    return {
        'candidates': list_all_candidates(campaign_id),
        'campaign': campaign,
        'voted': None if 'error' in voted.keys() else voted,
        'profile': get_detail_profile_data(campaign[0]['profile_id']) if len(campaign) == 1 else None
    }


def all_campaigns(page, limit, condition, user, timestamp, my_campaign):
    time = datetime.datetime.fromtimestamp(timestamp)
    return list_campaign(page, limit, condition, user, time, my_campaign, None, consts.PROFILE_TYPE['USER'], False)


def followed_campaigns(user, page: int, limit: int, profile_id: int):
    return list_campaign(page, limit, None, user, None, None, profile_id, consts.PROFILE_TYPE['ORG'], True)


def to_hex(value):
    return "0x" + value.encode().hex()
