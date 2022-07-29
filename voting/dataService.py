import datetime
import sqlite3


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


def list_campaign(page, limit, condition, user):
    additional_condition = ""
    time = datetime.datetime.now()

    if condition == 'ON_GOING':
        additional_condition = ' where start_time <= "' + str(time) + '" and end_time >= "' + str(time) + '" '
    elif condition == 'FINISHED':
        additional_condition = ' where end_time <= "' + str(time) + '" '
    else:
        # Case voted
        additional_condition = ' where c.id in (select campaign_id from voting where user="' + user + '") '

    query = 'select c.*, stat3.name winning_candidate_name, stat3.votes votes_of_candidate\
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
                on c.id = stat3.campaign_id\
                ' + additional_condition + 'limit ? offset ?'
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
            print('success')
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
                                 "avatar TEXT NOT NULL," \
                                 "campaign_id INTEGER NOT NULL," \
                                 "votes INTEGER NOT NULL DEFAULT 0," \
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

        campaign = create_campaign(
            "0x8B39e23A121bAc9221698cD22ae7A6a80D64b1DC",
            'This is the default campaign of the system.',
            "2000-01-01 00:00:00",
            "2099-01-01 00:00:00",
            "Which is the most favorite coin?"
        )

        query = []
        candidates = [
            {
                "name": "BTC",
                "brief_introduction": "Bitcoin is a decentralized digital currency that can be transferred on the "
                                      "peer-to-peer bitcoin network. Bitcoin transactions are verified by network "
                                      "nodes through cryptography and recorded in a public distributed ledger called "
                                      "a blockchain. ",
                "avatar": "#4A4A4A"
            },
            {
                "name": "ETH",
                "brief_introduction": "Ethereum is a decentralized, open-source blockchain with smart contract "
                                      "functionality. Ether is the native cryptocurrency of the platform. Among "
                                      "cryptocurrencies, Ether is second only to Bitcoin in market capitalization. "
                                      "Ethereum was conceived in 2013 by programmer Vitalik Buterin. ",
                "avatar": "#F6B63C"
            },
            {
                "name": "USDT",
                "brief_introduction": "Tether, is an asset-backed cryptocurrency stablecoin. It was launched by the "
                                      "company Tether Limited Inc. in 2014. Tether Limited is owned by the Hong "
                                      "Kong-based company iFinex Inc., which also owns the Bitfinex cryptocurrency "
                                      "exchange. ",
                "avatar": "#F7882B"
            },
            {
                "name": "BNB",
                "brief_introduction": "Binance Coin (BNB) is a cryptocurrency that can be used to trade and pay fees "
                                      "on the Binance cryptocurrency exchange. The Binance Exchange is the largest "
                                      "cryptocurrency exchange in the world as of January 2018, facilitating more "
                                      "than 1.4 million transactions per second. ",
                "avatar": "#F35330"
            },
            {
                "name": "CTSI",
                "brief_introduction": "CTSI is a utility token that powers the Cartesi network, which aims to solve "
                                      "blockchain scalability and high fees using technologies such as Optimistic "
                                      "Rollups and side-chains. CTSI can be used for staking and fees for processing "
                                      "data on the network. ",
                "avatar": "#B0F5CD"
            },
            {
                "name": "DOGE",
                "brief_introduction": "Dogecoin is a cryptocurrency created by software engineers Billy Markus and "
                                      "Jackson Palmer, who decided to create a payment system as a joke, making fun "
                                      "of the wild speculation in cryptocurrencies at the time. It is considered both "
                                      "the first meme coin, and, more specifically, the first dog coin. ",
                "avatar": "#F7F7F7"
            },
            {
                "name": "SOL",
                "brief_introduction": "A sol is a type of colloid in which solid particles are suspended in a liquid. "
                                      "The particles in a sol are very small. The colloidal solution displays the "
                                      "Tyndall effect and is stable. Sols may be prepared via condensation or "
                                      "dispersion. ",
                "avatar": "#7a396d"
            },
            {
                "name": "DOT",
                "brief_introduction": "Polkadot is a protocol that connects blockchains — allowing value and data to "
                                      "be sent across previously incompatible networks (Bitcoin and Ethereum, "
                                      "for example). It's also designed to be fast and scalable. The DOT token is "
                                      "used for staking and governance; it can be bought or sold on Coinbase and "
                                      "other exchanges. ",
                "avatar": "#F4AED8"
            },
            {
                "name": "HEX",
                "brief_introduction": "Hex (HEX) is an Ethereum-based token that is marketed as the first blockchain "
                                      "certificate of deposit. Richard Heart launched Hex in 2019, utilizing an "
                                      "aggressive marketing campaign to build its userbase. Users stake HEX tokens, "
                                      "promising to leave them untouched for specified amounts of time. ",
                "avatar": "#0156D3"
            }
        ]
        for candidate in candidates:
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


def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d
