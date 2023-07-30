# pylint:disable=missing-timeout,invalid-name
from __future__ import annotations
import os
from pprint import pprint
import json
from datetime import datetime
from dateutil.relativedelta import relativedelta
import dateutil

from slack import Slack
from plab_helper import PlabHelper


SLACK_WEBHOOK = os.environ['SLACK_WEBHOOK']
BASE_URL = os.environ['BASE_URL']
STADIUM_IDS = json.loads(os.environ['STADIUM_IDS'])
WEEKDAYS = {1, 2, 3} # 화요일, 수요일, 목요일
START_TIME = '20:00'


def date_range(weekdays, days=60):
    '''date iterator'''
    now = datetime.now().date()
    end = now + relativedelta(days=days)
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
    return weeknames[dateutil.parser.parse(dt).weekday()]


def main():
    base_url: str = os.environ['BASE_URL']
    stadium_ids: list[int] = json.loads(os.environ['STADIUM_IDS'])
    weekdays: set[int] = {1, 2, 3} # 화요일, 수요일, 목요일
    start_t: str = '20:00:00'
    slack_webhook: str = os.environ['SLACK_WEBHOOK']

    helper = PlabHelper(base_url)

    # get candidate stadium names
    stadium_id2name = {stadium_id: helper.get_stadium_name(stadium_id)
                       for stadium_id in stadium_ids}
    pprint(stadium_id2name)

    # get schedules
    schedules = []
    for stadium_id in stadium_ids:
        for date in date_range(weekdays):
            _schedules = helper.get_schedules(stadium_id=stadium_id,
                                              date=date,
                                              start_t=start_t)
            schedules.extend(_schedules)

    # translate
    for sched in schedules:
        sched['weekname'] = get_weekname(sched['date'])
        sched['order'] = helper.get_order_url(sched['product_id'])
    pprint(schedules)

    # send to slack
    msgbuilder = []
    for sched in schedules:
        stadium_full_name = sched['stadium_group_name']
        if sched['stadium_name']:
            stadium_full_name += ' - ' + sched['stadium_name']
        text = f'{stadium_full_name} - {sched["date"]} ({sched["weekname"]}) '
        text = f'<{sched["order"]}|{text}>'
        msgbuilder.append(text)

    candidates = ', '.join(stadium_id2name.values())
    title = f'앞으로 60일 간 예약 가능한 구장 일정 ({candidates})'
    text = '\n\n'.join(msgbuilder)
    slack = Slack(url=slack_webhook,
                  username='엔살매니저',
                  icon_emoji=':soccer:')
    slack.send(title, text, color='good', with_hostname=False)


if __name__ == '__main__':
    main()
