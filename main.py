# pylint:disable=missing-timeout,invalid-name
from __future__ import annotations

import json
import os
import random
import time
import traceback
from datetime import datetime
from pprint import pprint

import dateutil.parser
from dateutil.relativedelta import relativedelta

from plab_helper import PlabHelper
from slack import Slack


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
    weekdays: set[int] = {1, 2, 3}  # 화요일, 수요일, 목요일
    start_t: str = '20:00:00'
    slack_webhook: str = os.environ['SLACK_WEBHOOK']

    helper = PlabHelper(base_url)
    slack = Slack(url=slack_webhook,
                  username='엔살매니저',
                  icon_emoji=':soccer:')

    try:
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
                time.sleep(random.randint(1, 5))

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
        title = f'앞으로 60일 간 {start_t} 에 예약 가능한 구장 일정 ({candidates})'
        text = '\n\n'.join(msgbuilder)
        slack.send(title, text, color='good', with_hostname=False)
    except Exception as err:
        traceback.print_exc()
        title = str(err)
        slack.send(title, traceback.format_exc(), color='danger',
                   with_hostname=False)


if __name__ == '__main__':
    main()
