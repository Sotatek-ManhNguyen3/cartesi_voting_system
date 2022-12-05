import glob
from services.connection import init_conn
import json


def start_backup():
    files = glob.glob('./restore/*.json')

    if len(files) == 0:
        return False

    conn = init_conn()
    for file in files:
        try:
            f = open(file)
            data = json.load(f)
            table = file.split('/')[-1].split('.')[0]

            if 'data' not in data.keys():
                continue

            columns = json.loads(data['data'][0]).keys()
            prepared_data = []

            for raw in data['data']:
                row = json.loads(raw)
                row_data = []
                for column in columns:
                    row_data.append(row[column])

                prepared_data.append(row_data)

            gen_question_mark = ', '.join(['?' for i in range(len(columns))])
            print(",".join(columns))
            print(gen_question_mark)
            print(prepared_data)
            query = f'INSERT INTO {table} ({",".join(columns)}) values ({gen_question_mark})'
            cur = conn.cursor()
            cur.executemany(query, prepared_data)
        except Exception as e:
            print(e)

    conn.commit()
    conn.close()

    return True
