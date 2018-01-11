import datetime

epoch = datetime.datetime.utcfromtimestamp(0)


def to_millis(dt):
    try:
        return (dt - epoch).total_seconds() * 1000.0
    except:
        return False


def from_millis(ms):
    try:
        return datetime.datetime.fromtimestamp(ms / 1000.0)
    except:
        return False