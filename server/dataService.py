import datetime
import sqlite3


def update_deposit_amount(user, amount):
    query = 'update deposit set amount = amount + ? where user = ?'
    return update_data(query, (amount, user))


def create_deposit_info(user, amount):
    query = 'insert into deposit (user, amount) values (?, ?)'
    return insert_data(query, (user, amount))


def get_deposit_info(user):
    query = 'select * from deposit where user = ?'
    return select_data(query, (user,))


def voted_campaigns(user):
    query = 'select * from voting v ' \
            'inner join campaigns c on v.campaign_id = c.id ' \
            'inner join candidates cd on cd.campaign_id = v.campaign_id and cd.id = v.candidate_id ' \
            'where v.user = ?'
    return select_data(query, (user,))


def delete_candidate_in_campaign(candidate_id, campaign_id):
    query = 'delete from candidates where id=? and campaign_id=?'
    return update_data(query, (candidate_id, campaign_id))


def delete_voting_of_candidate(candidate_id, campaign_id):
    query = 'delete from voting_info where candidate_id=? and campaign_id=?'
    return update_data(query, (candidate_id, campaign_id))


def update_time_campaign(campaign_id, start_time, end_time):
    query = 'update campaigns set start_time = ?, end_time = ? where id = ?'
    return update_data(query, (start_time, end_time, campaign_id))


def list_campaign():
    query = 'select * from campaigns'
    return select_data(query, ())


def get_campaign(campaign_id):
    query = 'select * from campaigns where id = ?'
    return select_data(query, (campaign_id,))


def add_candidates(list_candidate):
    query = 'insert into candidates (name, campaign_id, avatar, brief_introduction) values (?, ?, ?, ?)'
    return insert_multiple_data(query, list_candidate)


def create_campaign(creator, description, start_time, end_time, name):
    query = 'insert into campaigns (creator, name, description, start_time, end_time) values (?, ?, ?, ?, ?);'
    result = insert_data(query, (creator, name, description, start_time, end_time))
    if 'error' in result.keys():
        return result
    else:
        query = 'Select * from campaigns where id = ?'
        result['campaign'] = select_data(query, (result['id'],))[0]
        return result


def increase_votes(candidate_id, campaign_id):
    query = 'update candidates set votes = votes + 1 where id=? and campaign_id=?'
    return update_data(query, (candidate_id, campaign_id))


def vote_candidate(user, candidate_id, campaign_id):
    query = 'insert into voting (candidate_id, campaign_id, user, voting_time) values (?, ?, ?, ?)'
    return update_data(query, (candidate_id, campaign_id, user, datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')))


def voted_candidate(user, campaign_id):
    query = 'select * from voting where user = ? and campaign_id = ?'
    voted = select_data(query, (user, campaign_id))
    if len(voted) == 0:
        return {'error': 'You did not vote yet'}

    return voted[0]


def top_candidates(campaign_id, quantity=10):
    query = "select * from candidates where campaign_id=? order by votes desc limit ?"
    return select_data(query, (campaign_id, quantity))


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
        result = "EXCEPTION: " + e.__str__()
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
        result = "EXCEPTION: " + e.__str__()
        print("NOTICE EXCEPTION" + e.__str__())
        return result


def insert_multiple_data(query, data):
    conn = init_conn()

    try:
        with conn:
            cur = conn.cursor()
            cur.executemany(query, data)
            return {'message': 'Success'}
    except Exception as e:
        result = "EXCEPTION: " + e.__str__()
        print("NOTICE EXCEPTION" + e.__str__())
        return result


def init_conn():
    conn = sqlite3.connect('voting_system.db')
    conn.row_factory = dict_factory
    return conn


def create_base_tables():
    conn = init_conn()
    cur = conn.cursor()

    sql_query = "SELECT name FROM sqlite_master WHERE type='table';"
    result = cur.execute(sql_query)
    tables = result.fetchall()
    if len(tables) == 0:
        print("Metadata does not exist")
        query_campaign_table = "CREATE TABLE campaigns(" \
                               "id INTEGER PRIMARY KEY AUTOINCREMENT," \
                               "creator TEXT NOT NULL," \
                               "name TEXT NOT NULL," \
                               "description TEXT," \
                               "start_time TEXT NOT NULL," \
                               "end_time TEXT NOT NULL);"
        cur.execute(query_campaign_table)

        query_candidates_table = "CREATE TABLE candidates(" \
                                 "id INTEGER PRIMARY KEY AUTOINCREMENT," \
                                 "name TEXT NOT NULL," \
                                 "campaign_id INTEGER NOT NULL," \
                                 "votes INTEGER NOT NULL DEFAULT 0," \
                                 "avatar TEXT," \
                                 "brief_introduction TEXT," \
                                 "FOREIGN KEY (campaign_id) REFERENCES campaigns (id))"
        cur.execute(query_candidates_table)

        query_voting_table = "CREATE TABLE voting(" \
                             "id INTEGER PRIMARY KEY AUTOINCREMENT," \
                             "candidate_id INTEGER NOT NULL," \
                             "campaign_id INTEGER NOT NULL," \
                             "user TEXT NOT NULL," \
                             "voting_time TEXT NOT NULL," \
                             "FOREIGN KEY (candidate_id) REFERENCES candidates (id)," \
                             "FOREIGN KEY (campaign_id) REFERENCES campaigns (id))"
        cur.execute(query_voting_table)

        query_deposit_table = "CREATE TABLE deposit(" \
                              "id INTEGER PRIMARY KEY AUTOINCREMENT," \
                              "user TEXT NOT NULL," \
                              "amount INTEGER NOT NULL)"

        cur.execute(query_deposit_table)
        conn.commit()
        conn.close()
    else:
        print("Metadata exists")


def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d
