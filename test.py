import os

from slack import Slack


SLACK_WEBHOOK = os.environ['SLACK_WEBHOOK']
BASE_URL = os.environ['BASE_URL']
STADIUM_GROUP = os.environ['STADIUM_GROUP']


def main():
    title = '테스트메시지'
    text = []
    text.append(f'{BASE_URL=}')
    text.append(f'{STADIUM_GROUP=}')
    text.append(f'{SLACK_WEBHOOK=}')
    text = '\n'.join(text)
    print(text)
    slack = Slack(url=SLACK_WEBHOOK, username='엔살매니저', icon_emoji=':soccer:')
    slack.send(title, text, color='good', with_hostname=False)


if __name__ == '__main__':
    main()
