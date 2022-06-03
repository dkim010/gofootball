import os
import requests
from datetime import datetime
from dateutil.relativedelta import relativedelta
from dateutil import parser
from pprint import pprint
from collections import defaultdict

from slack import Slack


SLACK_WEBHOOK = os.environ['SLACK_WEBHOOK']
BASE_URL = os.environ['BASE_URL']
STADIUM_GROUP = os.environ['STADIUM_GROUP']
WEEKDAYS = {1, 2, 3} # 화요일, 수요일, 목요일
START_TIME = '20:00'


def get_stadium_group_info(stadium_group_id):
    '''retrieve stadium gropu information'''
    api_url = f'{BASE_URL}/api/v2/rental/stadium-groups/'
    params = {
        'id': f'{stadium_group_id}',
        'date': '',
    }
    resp = requests.get(api_url, params=params)
    resp_json = resp.json()
    return resp_json['results'][0]


def get_schedules(stadium_id, dt, start_time):
    '''retrieve schedule info for specific stadium'''
    api_url = f'{BASE_URL}/api/v2/rental/stadiums/{stadium_id}/products/'
    params = {
        'date': f'{dt}',
    }
    resp = requests.get(api_url, params=params)
    resp_json = resp.json()
    result = None
    for sched in resp_json['results']:
        if sched['start_time'] == start_time:
            result = sched
            break
    return result


def date_range(weekdays):
    '''date iterator'''
    now = datetime.now().date()
    end = datetime(year=now.year, month=now.month, day=1).date() \
        + relativedelta(months=2) \
        - relativedelta(days=1)
    that = now
    while that <= end:
        if weekdays and that.weekday() in weekdays:
            yield str(that)
        that += relativedelta(days=1)


def get_weekname(dt):
    '''get korean weekname'''
    weeknames = {
        0: '월요일',
        1: '화요일',
        2: '수요일',
        3: '목요일',
        4: '금요일',
        5: '토요일',
        6: '일요일',
    }
    return weeknames[parser.parse(dt).weekday()]


def main():
    # collect reserv. info.
    results = defaultdict(dict)
    dts = [dt for dt in date_range(WEEKDAYS)]
    info = get_stadium_group_info(STADIUM_GROUP)
    name = info['name']
    for stadium in info['stadiums']:
        for dt in dts:
            sched = get_schedules(stadium['id'], dt, START_TIME)
            if sched:
                results[dt][(stadium['id'], stadium['name'])] = sched
    # send results to slack
    msgbuilder = list()
    for dt in results:
        for stadium_id, stadium_name in results[dt]:
            sched = results[dt][(stadium_id, stadium_name)]
            if sched['product_status'] == 'READY':
                text = f'{stadium_name} - {dt} ({get_weekname(dt)}) 예약 가능!'
                hyperlink = f'{BASE_URL}/rental/{sched["id"]}/order/'
                text = f'<{hyperlink}|{text}>'
                msgbuilder.append(text)
    title = f'{name} 예약 가능한 구장'
    text = '\n\n'.join(msgbuilder)
    slack = Slack(url=SLACK_WEBHOOK, username='엔살매니저', icon_emoji=':soccer:')
    slack.send(title, text, color='good', with_hostname=False)


if __name__ == '__main__':
    main()
