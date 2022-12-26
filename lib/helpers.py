import datetime


def get_date_time_from_string(time):
    time = time.split(' ')
    time = time[0].split('-') + time[1].split(':')
    return datetime.datetime(*[int(x) for x in time])


# Convert timestamp to string
# Example return: "2022-11-10 08:20:21"
def get_date_time_from_timestamp(timestamp):
    return str(datetime.datetime.fromtimestamp(timestamp))


# Format date time to YYYY-MM-DD HH:MM:SS
def format_date_time(time: datetime):
    return time.strftime('%Y-%m-%d %H:%M:%S')


def gen_question_mark_for_query_in(arr):
    return ', '.join(['?' for i in range(len(arr))])


# Get value of key in dict. Return None if that key doesn't exist
def get_var(dict_var, key):
    return None if key not in dict_var.keys() else dict_var[key]


# Remove duplicate values in list
def remove_duplicate(data):
    return list(dict.fromkeys(data))
