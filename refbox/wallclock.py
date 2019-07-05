import requests
from datetime import datetime

def now(timezone):
    try:
        url = 'http://worldclockapi.com/api/json/{}/now'.format(timezone)
        resp = requests.get(url=url).json()
        # '2019-07-05T10:19-06:00'
        with_tz = resp['currentDateTime']
        without_tz = '-'.join(with_tz.split('-')[:3])
        return datetime.strptime(without_tz, "%Y-%m-%dT%H:%M")
    except Exception as e:
        return datetime.now()

if __name__ == '__main__':
    print(now('mst'))
