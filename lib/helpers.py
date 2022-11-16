import datetime


def get_date_time_from_string(time):
    time = time.split(' ')
    time = time[0].split('-') + time[1].split(':')
    return datetime.datetime(*[int(x) for x in time])


def get_now_str():
    return datetime.datetime.strftime("%Y-%m-%d %H:%M:%S")
