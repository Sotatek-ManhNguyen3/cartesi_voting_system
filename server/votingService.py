from dataService import *
from lib.helpers import get_date_time_from_string


def add_deposit_user(user, amount):
    deposit_info = get_deposit_info(user)

    if len(deposit_info) == 0:
        create_deposit_info(user, amount)
    else:
        update_deposit_amount(user, amount)

    return True


def vote(user, candidate_id, campaign_id, timestamp):
    # Validate campaign and valid time to vote
    campaign = get_campaign(campaign_id)

    if len(campaign) == 0:
        return {'error': 'Campaign does not exist'}

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

    # Vote
    result = vote_candidate(user, candidate_id, campaign_id)
    if 'error' in result.keys():
        return result

    # Increase vote in candidates table
    return increase_votes(candidate_id, campaign_id)


def create_new_campaign(creator, payload):
    try:
        if type(payload['candidates']) is not list:
            return {'error': 'Wrong input format'}

        campaign = create_campaign(creator, payload['description'],
                                   payload['start_time'], payload['end_time'], payload['name'])

        if 'error' in campaign.keys():
            return {'error': campaign}

        candidates = []
        for candidate in payload['candidates']:
            candidates.append([
                candidate['name'],
                campaign['id'],
                candidate['avatar'] if 'avatar' in candidate.keys() else '',
                candidate['brief_introduction'] if 'brief_introduction' in candidate.keys() else '',
            ])

        add_candidates(candidates)
        return campaign
    except KeyError as e:
        result = "EXCEPTION: " + e.__str__()
        print("NOTICE EXCEPTION" + e.__str__())
        return {'error': result}


def get_voted_candidate(user, campaign_id):
    campaign = get_campaign(campaign_id)
    if len(campaign) == 0:
        return {'error': 'Campaign does not exist'}

    return voted_candidate(user, campaign_id)


def change_time_campaign(user_change, campaign_id, start_time, end_time):
    campaign = get_campaign(campaign_id)
    if len(campaign) == 0:
        return {'error': 'Campaign does not exist!'}

    if campaign[0]['creator'] != user_change:
        return {'error': 'You do not have the permission!'}

    return update_time_campaign(campaign_id, start_time, end_time)


def add_candidates_to_campaign(user_change, campaign_id, candidates):
    campaign = get_campaign(campaign_id)
    if len(campaign) == 0:
        return {'error': 'Campaign does not exist!'}

    if campaign[0]['creator'] != user_change:
        return {'error': 'You do not have the permission!'}

    return add_candidates_to_database(campaign_id, candidates)


def add_candidates_to_database(campaign_id, candidates):
    converted_data = []
    for candidate in candidates:
        converted_data.append([
            candidate['name'],
            campaign_id,
            candidate['avatar'] if 'avatar' in candidate.keys() else '',
            candidate['brief_introduction'] if 'brief_introduction' in candidate.keys() else '',
        ])

    return add_candidates(converted_data)


def delete_candidate(deleter, campaign_id, candidate_id):
    campaign = get_campaign(campaign_id)
    if len(campaign) == 0:
        return {'error': 'Campaign does not exist!'}

    if campaign[0]['creator'] != deleter:
        return {'error': 'You do not have the permission!'}

    candidate = get_candidate(candidate_id, campaign_id)
    if len(candidate) == 0:
        return {'error': 'Candidate does not exist'}

    delete_voting_of_candidate(candidate_id, campaign_id)
    delete_candidate_in_campaign(candidate_id, campaign_id)


def voted_campaigns_of_user(user):
    return voted_campaigns(user)


def initialize_tables():
    create_base_tables()


def all_candidates(campaign_id):
    return list_all_candidates(campaign_id)


def top_ranked_candidates(campaign_id, quantity):
    return top_candidates(campaign_id, quantity)


def all_campaigns():
    return list_campaign()


def to_hex(value):
    return "0x" + value.encode().hex()
