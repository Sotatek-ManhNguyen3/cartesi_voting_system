from dataService import get_candidate_by_id, voted_candidate, vote_candidate, increase_votes


def vote(user, candidate_id):
    candidate = get_candidate_by_id(candidate_id)
    if len(candidate) == 0:
        return {'error': 'Invalid candidate id'}

    voted = voted_candidate(user)
    if 'error' not in voted.keys():
        return {'error': 'You can only vote for one candidate'}

    result = vote_candidate(user, candidate_id)
    if 'error' in result.keys():
        return result

    return increase_votes(candidate_id)
