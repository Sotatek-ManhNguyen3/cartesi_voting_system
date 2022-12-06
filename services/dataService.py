import datetime
import json
from constants import metadata
from constants.consts import STATUS_TOKEN
from services.connection import *
from services.sampleData import CANDIDATES
from lib.helpers import get_now_str
from services.restoreDataService import start_backup


def backup_table(table):
    query = f'select * from {table}'
    return select_data(query, ())


def count_active_campaign_by_token(token):
    now = get_now_str()
    query = 'select count(*) as count from campaigns where accept_token = ? and end_time > ?'
    return select_data(query, (token, now))


def check_token_can_vote(token):
    query = f'select * from tokens where address = ? and status = ? and can_vote = 1'
    return select_data(query, (token, STATUS_TOKEN["ACTIVE"]))


def check_token_can_create_campaign(token):
    query = f'select * from tokens where address = ? and can_create_campaign = 1 and status = {STATUS_TOKEN["ACTIVE"]}'
    return select_data(query, (token,))


def list_token():
    query = 'select * from tokens'
    return select_data(query, ())


def delete_token(address):
    query = 'delete from tokens where address = ?'
    return update_data(query, (address,))


def change_status_token(address, status):
    query = 'update tokens set status = ? where address = ?'
    return update_data(query, (status, address))


def update_token(id_update, address, name, fee, icon, status, can_vote, can_create_campaign):
    status = 1 if status is None else status
    can_vote = 1 if can_vote is None else can_vote
    can_create_campaign = 0 if can_create_campaign is None else can_create_campaign
    icon = '' if icon is None else icon
    query = 'update tokens ' \
            'set address = ?, name = ?, fee = ?, icon = ?, status = ?, can_vote = ?, can_create_campaign = ? ' \
            'where id = ?'
    return update_data(query, (address, name, fee, icon, status, can_vote, can_create_campaign, id_update))


def create_token(address, name, fee, icon, status, can_vote, can_create_campaign):
    status = 1 if status is None else status
    can_vote = 1 if can_vote is None else can_vote
    can_create_campaign = 0 if can_create_campaign is None else can_create_campaign
    icon = '' if icon is None else icon

    query = 'insert into tokens (address, name, fee, icon, status, can_vote, can_create_campaign)' \
            ' values (?, ?, ?, ?, ?, ?, ?)'
    return update_data(query, (address, name, fee, icon, status, can_vote, can_create_campaign))


def get_token(address, status=STATUS_TOKEN['ACTIVE']):
    if status is None:
        query = 'select * from tokens where address = ? limit 1'
        return select_data(query, (address,))
    else:
        query = 'select * from tokens where address = ? and status = ? limit 1'
        return select_data(query, (address, status))


def get_token_can_deposit(address):
    query = f'select * from tokens where address = ? and status != {STATUS_TOKEN["DISABLED"]}'
    return select_data(query, (address,))


def update_role(id_update, user, manage_user, manage_token, manage_post, manage_system):
    query = 'update roles set user = ?, manage_user = ?, manage_token = ?, manage_post = ?, manage_system = ? ' \
            'where id = ?'
    return update_data(query, (user, manage_user, manage_token, manage_post, manage_system, id_update))


def delete_role(user):
    query = 'delete from roles where user = ?'
    return update_data(query, (user,))


def list_role(roles):
    condition = ''

    if len(roles):
        condition = ' where'
        for role in roles:
            condition = f' {role} = 1'

    query = 'select * from roles' + condition
    return select_data(query, ())


def create_role(user, manage_user, manage_token, manage_post, manage_system):
    query = 'insert into roles (user, manage_user, manage_token, manage_post, manage_system) values (?, ?, ?, ?, ?)'
    return insert_data(query, (user, manage_user, manage_token, manage_post, manage_system))


def get_role(user):
    query = 'select * from roles where user=? limit 1'
    return select_data(query, (user,))


def remove_notification_data(user):
    query = 'select id from notifications where user = ? order by id desc limit 1 offset ?'
    result = select_data(query, (user, metadata.MAX_NOTIFICATIONS))
    if len(result) == 0:
        return

    id_need_delete = result[0]['id']
    query = 'delete from notifications where user = ? and id <= ?'
    return update_data(query, (user, id_need_delete))


def fetch_notifications(user, page, limit):
    query_data = 'select * from notifications where user = ? order by id desc limit ? offset ?'
    query_total = 'select count(*) as total from notifications where user = ?'
    return {
        'data': select_data(query_data, (user, limit, (page - 1) * limit)),
        'page': page,
        'limit': limit,
        'total': select_data(query_total, (user,))[0]['total']
    }


def save_notification_data(user, action, payload, time, status):
    query = 'insert into notifications (user, action, payload, time, status) values (?, ?, ?, ?, ?)'
    return insert_data(query, (user, action, payload, time, status))


def get_action_histories_data(user, page, limit, action='all'):
    query_data = 'select * from action_logs where user = ?'
    query_total = 'select count(*) as total from action_Logs where user = ?'
    query_data_param = (user,)
    query_total_param = (user,)

    if action != 'all':
        query_data = query_data + ' and action = ?'
        query_total = query_total + ' and action = ?'
        query_data_param += (action,)
        query_total_param += (action,)

    query_data = query_data + ' order by id DESC limit ? offset ?'
    query_data_param += (limit, (page - 1) * limit)

    return {
        'data': select_data(query_data, query_data_param),
        'page': page,
        'limit': limit,
        'total': select_data(query_total, query_total_param)[0]['total']
    }


def log_action_data(user, action, payload, time):
    query = 'insert into action_logs (user, action, payload, time) values (?, ?, ?, ?)'
    return insert_data(query, (user, action, json.dumps(payload), time))


def save_executed_voucher(user, voucher_id):
    query = 'insert into executed_voucher (user, voucher_id) values (?, ?)'
    return insert_data(query, (user, voucher_id))


def list_executed_vouchers(user):
    query = 'select * from executed_voucher where user = ?'
    return select_data(query, (user,))


def update_withdrawn_amount_user(user, amount, token):
    query = 'update deposit set withdrawn_amount = withdrawn_amount + ? where user = ? and contract_address = ?'
    return update_data(query, (amount, user, token))


def update_used_amount_user(user, token, amount=metadata.DEFAULT_FEE_IN_SYSTEM):
    query = 'update deposit set used_amount = used_amount + ? where user = ? and contract_address = ?'
    return update_data(query, (amount, user, token))


def get_total_vote_of_campaign(campaign_id):
    query = 'select sum(votes) as total_vote from candidates where campaign_id=? '
    result = select_data(query, (campaign_id,))
    print(result)
    return result[0]['total_vote']


def detail_candidate(campaign_id, candidate_id):
    query = 'select * from candidates where campaign_id=? and id=?'
    candidate = select_data(query, (campaign_id, candidate_id))

    if len(candidate) == 0:
        return None
    else:
        return candidate[0]


def voting_result(campaign_id):
    query = 'select * from candidates where campaign_id=?'
    return select_data(query, (campaign_id,))


def update_deposit_amount(user, amount, token):
    query = 'update deposit set amount = amount + ? where user = ? and contract_address = ?'
    return update_data(query, (amount, user, token))


def create_deposit_info(user, amount, token):
    query = 'insert into deposit (user, amount, contract_address) values (?, ?, ?)'
    return insert_data(query, (user, amount, token))


def get_deposit_info(user):
    query = 'select * from deposit where user = ?'
    return select_data(query, (user,))


def get_deposit_info_of_token(user, token):
    query = 'select * from deposit where user = ? and contract_address = ?'
    return select_data(query, (user, token))


def delete_campaign_info(campaign_id):
    query = 'delete from campaigns where id =?'
    return update_data(query, (campaign_id,))


def delete_candidate_in_campaign(candidate_id, campaign_id):
    query = 'delete from candidates where id=? and campaign_id=?'
    return update_data(query, (candidate_id, campaign_id))


def delete_all_candidates_of_campaign(campaign_id):
    query = 'delete from candidates where campaign_id=?'
    return update_data(query, (campaign_id,))


def delete_voting_of_candidate(candidate_id, campaign_id):
    query = 'delete from voting_info where candidate_id=? and campaign_id=?'
    return update_data(query, (candidate_id, campaign_id))


def update_campaign_info(campaign_id, name, description, start_time, end_time, accept_token, fee):
    query = 'update campaigns ' \
            'set name = ?, description = ?, start_time = ?, end_time = ?, accept_token = ?, fee = ? ' \
            'where id = ?'
    return update_data(query, (name, description, start_time, end_time, accept_token, fee, campaign_id))


def update_time_campaign(campaign_id, start_time, end_time):
    query = 'update campaigns set start_time = ?, end_time = ? where id = ?'
    return update_data(query, (start_time, end_time, campaign_id))


def list_campaign(page, limit, condition, user, time, my_campaign):
    query_my_campaign = 'and c.creator = "' + user + '" ' if my_campaign else ''
    if condition == 'ON_GOING':
        additional_condition = ' where start_time <= "' + str(time) + '" and end_time >= "' + str(time) + '" ' \
                               + query_my_campaign
    elif condition == 'FINISHED':
        additional_condition = ' where end_time <= "' + str(time) + '" ' + query_my_campaign
    elif condition == 'VOTED':
        additional_condition = ' where c.id in (select campaign_id from voting where user="' + user + '") ' \
                               + query_my_campaign
    else:
        additional_condition = ' where c.creator = "' + user + '" ' if my_campaign else ''

    query = 'select c.*, stat3.name winning_candidate_name, stat3.votes votes_of_candidate,stat4.total_vote as total_vote\
                from campaigns c\
                left join (select *\
                from candidates c3\
                where id in (select max(id)\
                from candidates c2\
                join\
                (select max(votes) max_vote, campaign_id\
                from candidates\
                    group by campaign_id) stat\
                on c2.campaign_id = stat.campaign_id and c2.votes = stat.max_vote where c2.votes != 0\
                group by c2.campaign_id)) stat3\
                on c.id = stat3.campaign_id\
                left join (select sum(votes) as total_vote, campaign_id from candidates group by campaign_id) stat4\
                on stat4.campaign_id = c.id\
                ' + additional_condition + ' order by c.id DESC limit ? offset ?'
    query_total = 'select count(*) total\
                from campaigns c\
                left join (select *\
                from candidates c3\
                where id in (select max(id)\
                from candidates c2\
                join\
                (select max(votes) max_vote, campaign_id\
                from candidates\
                    group by campaign_id) stat\
                on c2.campaign_id = stat.campaign_id and c2.votes = stat.max_vote\
                group by c2.campaign_id)) stat3\
                on c.id = stat3.campaign_id' + additional_condition
    result = {
        "data": select_data(query, (limit, (page - 1) * limit)),
        "page": page,
        "limit": limit,
        "total": select_data(query_total, ())[0]['total']
    }
    return result


def get_campaign(campaign_id):
    query = 'select * from campaigns where id = ?'
    return select_data(query, (campaign_id,))


def add_candidates(list_candidate):
    query = 'insert into candidates (name, campaign_id, brief_introduction, avatar) values (?, ?, ?, ?)'
    return insert_multiple_data(query, list_candidate)


def create_campaign(creator, description, start_time, end_time, name, accept_token, fee):
    query = 'insert into campaigns (creator, name, description, start_time, end_time, accept_token, fee) ' \
            'values (?, ?, ?, ?, ?, ?, ?);'
    result = insert_data(query, (creator, name, description, start_time, end_time, accept_token, fee))
    if 'error' in result.keys():
        return result
    else:
        query = 'Select * from campaigns where id = ?'
        result['campaign'] = select_data(query, (result['id'],))[0]
        return result


def increase_votes(candidate_id, campaign_id):
    query = 'update candidates set votes = votes + 1 where id=? and campaign_id=?'
    return update_data(query, (candidate_id, campaign_id))


def vote_candidate(user, candidate_id, campaign_id, comment):
    query = 'insert into voting (candidate_id, campaign_id, user, voting_time, comment) values (?, ?, ?, ?, ?)'
    return update_data(
        query,
        (candidate_id, campaign_id, user, datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'), comment)
    )


def list_voter(campaign_id, page, limit):
    query = 'select ' \
            'v.user, v.comment, v.voting_time, v.candidate_id, c.name, c.avatar, c.votes, c.brief_introduction ' \
            'from voting v left join candidates c on v.candidate_id = c.id ' \
            'where v.campaign_id = ? ' \
            'order by voting_time desc ' \
            'limit ? offset ?'
    return select_data(query, (campaign_id, limit, (page - 1) * limit))


def voted_candidate(user, campaign_id):
    query = 'select * from voting join candidates on voting.candidate_id = candidates.id ' \
            'where voting.user = ? and voting.campaign_id = ?'
    voted = select_data(query, (user, campaign_id))
    if len(voted) == 0:
        return {'error': 'You did not vote yet'}

    return voted[0]


def list_all_candidates(campaign_id):
    query = 'select * from candidates where campaign_id = ?'
    return select_data(query, (campaign_id,))


def get_candidate(candidate_id, campaign_id):
    query = 'select * from candidates where id=? and campaign_id=?'
    return select_data(query, (candidate_id, campaign_id))


def update_data(query, data):
    conn = init_conn()

    try:
        with conn:
            cur = conn.cursor()
            cur.execute(query, data)
            return {'message': 'Success'}
    except Exception as e:
        result = "EXCEPTION: " + e.__str__()
        print("NOTICE EXCEPTION" + e.__str__())
        return {'error': result}


def select_data(query, data):
    conn = init_conn()

    try:
        with conn:
            cur = conn.cursor()
            result = cur.execute(query, data)
            return result.fetchall()
    except Exception as e:
        result = {'error': "EXCEPTION: " + e.__str__()}
        print("NOTICE EXCEPTION" + e.__str__())
        return result


def insert_data(query, data):
    conn = init_conn()

    try:
        with conn:
            cur = conn.cursor()
            cur.execute(query, data)
            return {'message': 'success', 'id': cur.lastrowid}
    except Exception as e:
        result = {'error': "EXCEPTION: " + e.__str__()}
        print("NOTICE EXCEPTION" + e.__str__())
        return result


def insert_multiple_data(query, data):
    conn = init_conn()

    try:
        with conn:
            cur = conn.cursor()
            cur.executemany(query, data)
            print('success')
            return {'message': 'Success'}
    except Exception as e:
        result = {'error': "EXCEPTION: " + e.__str__()}
        print("NOTICE EXCEPTION" + e.__str__())
        return result


def create_base_tables():
    conn = init_conn()
    cur = conn.cursor()

    sql_query = "SELECT name FROM sqlite_master WHERE type='table';"
    result = cur.execute(sql_query)
    tables = result.fetchall()
    if len(tables) == 0:
        print("Metadata does not exist")
        # Table campaign
        query_campaign_table = "CREATE TABLE campaigns(" \
                               "id INTEGER PRIMARY KEY AUTOINCREMENT," \
                               "creator TEXT NOT NULL," \
                               "name TEXT NOT NULL," \
                               "description TEXT," \
                               "start_time TEXT NOT NULL," \
                               "end_time TEXT NOT NULL," \
                               "accept_token TEXT NOT NULL," \
                               "fee INTEGER NOT NULL DEFAULT 0);"
        cur.execute(query_campaign_table)

        # Table candidates
        query_candidates_table = "CREATE TABLE candidates(" \
                                 "id INTEGER PRIMARY KEY AUTOINCREMENT," \
                                 "name TEXT NOT NULL," \
                                 "avatar TEXT NOT NULL," \
                                 "campaign_id INTEGER NOT NULL," \
                                 "votes INTEGER NOT NULL DEFAULT 0," \
                                 "brief_introduction TEXT," \
                                 "FOREIGN KEY (campaign_id) REFERENCES campaigns (id))"
        cur.execute(query_candidates_table)

        query_index_candidates_campaign_id = "CREATE INDEX index_candidates_campaign_id on candidates(campaign_id)"
        cur.execute(query_index_candidates_campaign_id)

        # Table voting
        query_voting_table = "CREATE TABLE voting(" \
                             "id INTEGER PRIMARY KEY AUTOINCREMENT," \
                             "candidate_id INTEGER NOT NULL," \
                             "campaign_id INTEGER NOT NULL," \
                             "user TEXT NOT NULL," \
                             "voting_time TEXT NOT NULL," \
                             "comment TEXT," \
                             "FOREIGN KEY (candidate_id) REFERENCES candidates (id)," \
                             "FOREIGN KEY (campaign_id) REFERENCES campaigns (id))"
        cur.execute(query_voting_table)

        query_index_voting_campaign_id = "CREATE INDEX index_voting_campaign_id on voting(campaign_id)"
        cur.execute(query_index_voting_campaign_id)

        query_index_voting_campaign_id_voting_time = \
            "CREATE INDEX index_voting_campaign_id_voting_time on voting(campaign_id, voting_time)"
        cur.execute(query_index_voting_campaign_id_voting_time)

        query_index_voting_user = "CREATE INDEX index_voting_user on voting(user)"
        cur.execute(query_index_voting_user)

        # Table deposit
        query_deposit_table = "CREATE TABLE deposit(" \
                              "id INTEGER PRIMARY KEY AUTOINCREMENT," \
                              "user TEXT NOT NULL," \
                              "amount INTEGER NOT NULL, " \
                              "used_amount INTEGER NOT NULL DEFAULT 0, " \
                              "withdrawn_amount INTEGER NOT NULL DEFAULT 0, " \
                              "contract_address TEXT NOT NULL)"
        cur.execute(query_deposit_table)

        query_index_deposit_user = "CREATE INDEX index_deposit_user on deposit(user)"
        cur.execute(query_index_deposit_user)

        # Table executed_vouchers
        query_executed_voucher = "CREATE TABLE executed_voucher(" \
                                 "id INTEGER PRIMARY KEY AUTOINCREMENT," \
                                 "user TEXT NOT NULL," \
                                 "voucher_id TEXT NOT NULL)"
        cur.execute(query_executed_voucher)

        query_index_executed_voucher_user = "CREATE INDEX index_executed_voucher_user on executed_voucher(user)"
        cur.execute(query_index_executed_voucher_user)

        # Table action_logs
        query_action_logs = "CREATE TABLE action_logs(" \
                            "id INTEGER PRIMARY KEY AUTOINCREMENT," \
                            "user TEXT NOT NULL," \
                            "action TEXT NOT NULL," \
                            "payload TEXT NOT NULL," \
                            "time TEXT NOT NULL)"
        cur.execute(query_action_logs)

        query_index_action_logs_user = "CREATE INDEX index_action_logs_user on action_logs(user)"
        cur.execute(query_index_action_logs_user)

        # Table notifications
        query_notifications = "CREATE TABLE notifications(" \
                              "id INTEGER PRIMARY KEY AUTOINCREMENT," \
                              "user TEXT," \
                              "action TEXT NOT NULL," \
                              "payload TEXT NOT NULL," \
                              "time TEXT NOT NULL," \
                              "status TEXT NOT NULL)"
        cur.execute(query_notifications)

        query_index_notifications_user = "CREATE INDEX index_notifications_user on notifications(user)"
        cur.execute(query_index_notifications_user)

        # Table roles
        query_roles = "CREATE TABLE roles(" \
                      "id INTEGER PRIMARY KEY AUTOINCREMENT," \
                      "user TEXT NOT NULL UNIQUE," \
                      "manage_user INTEGER NOT NULL DEFAULT 1," \
                      "manage_token INTEGER NOT NULL DEFAULT 1," \
                      "manage_post INTEGER NOT NULL DEFAULT 1," \
                      "manage_system INTEGER NOT NULL DEFAULT 1)"
        cur.execute(query_roles)

        # Table tokens
        query_tokens = "CREATE TABLE tokens(" \
                       "id INTEGER PRIMARY KEY AUTOINCREMENT," \
                       "address TEXT NOT NULL UNIQUE," \
                       "name TEXT NOT NULL," \
                       "fee INTEGER," \
                       "icon TEXT," \
                       "status INTEGER NOT NULL DEFAULT 1," \
                       "can_vote INTEGER DEFAULT 1," \
                       "can_create_campaign INTEGER DEFAULT 0)"
        cur.execute(query_tokens)

        if start_backup():
            print('Have data backup')
            conn.commit()
            conn.close()
            return

        # For local
        query_create_roles = 'INSERT INTO roles (user) values ("0xf39fd6e51aad88f6f4ce6ab8827279cfffb92266")'
        insert_data(query_create_roles, ())
        # For testnet
        query_create_roles = 'INSERT INTO roles (user) values ("0x1f5bc6c2a6259d00e5447cebb3b2bc0bb7b03996")'
        insert_data(query_create_roles, ())

        campaign = create_campaign(
            "0x8B39e23A121bAc9221698cD22ae7A6a80D64b1DC",
            'This is the default campaign of the system.',
            "2000-01-01 00:00:00",
            "2099-01-01 00:00:00",
            "Which is the most favorite coin?",
            metadata.CTSI_LOCAL,
            10
        )

        query = []
        for candidate in CANDIDATES:
            query.append([
                candidate['name'],
                campaign['id'],
                candidate['brief_introduction'] if 'brief_introduction' in candidate.keys() else '',
                candidate['avatar']
            ])

        add_candidates(query)
        conn.commit()
        conn.close()
    else:
        print("Metadata exists")
