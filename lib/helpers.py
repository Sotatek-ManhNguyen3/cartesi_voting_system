import datetime
import lib.metadata
import lib.config


def get_date_time_from_string(time):
    time = time.split(' ')
    time = time[0].split('-') + time[1].split(':')
    return datetime.datetime(*[int(x) for x in time])


def get_fee(address):
    if config.environment not in metadata.FEE_IN_SYSTEM.keys():
        return metadata.DEFAULT_FEE_IN_SYSTEM

    fee_info = metadata.FEE_IN_SYSTEM[config.environment]

    for token in fee_info:
        if address == token['address']:
            return token['fee']

    return metadata.DEFAULT_FEE_IN_SYSTEM
