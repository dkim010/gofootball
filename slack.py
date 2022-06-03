#-*- coding: utf-8 -*-
from __future__ import print_function
import os
from datetime import datetime
import traceback
import socket
import requests, json
try:
    from urllib.parse import urljoin
    from urllib.parse import urlencode
    import urllib.request as urlrequest
except ImportError:
    from urlparse import urljoin
    from urllib import urlencode
    import urllib2 as urlrequest


class Slack(object):
    def __init__(self, url, stamp='', title='', **kwargs):
        self.url = url
        self.stamp = stamp
        self.title = title
        self.kwargs = kwargs

        self.last_sended = 0.

    def _send(self, payload):
        headers = {'content-type': 'application/json', 'Accept-Charset': 'UTF-8'}
        data = json.dumps(payload)
        r = requests.post(self.url, data=data.encode('utf-8'), headers=headers)

    def send(self, title, text, color, title_link=None, with_hostname=True):
        # attachment
        if self.title and self.stamp:
            title = f'{title} [{self.title}, {self.stamp}]'
        elif self.title:
            title = f'{title} [{self.title}]'
        elif self.stamp:
            title = f'{title} [{self.stamp}]'
        attachment = {
            'mrkdwn': True,
            'mrkdwn_in': ['text'],
            'text': text,
            'color': color,
            'title': title,
            'title_link': title_link,
            'footer': '{}:{}'.format(socket.gethostname(), os.getcwd()) if with_hostname \
                      else None,
            }

        payload = {
            'attachments': [attachment],
        }
        for k, v in self.kwargs.items():
            if v is not None:
                payload[k] = v
        self._send(payload)

    def periodic_send(self, title, text, interval=60, color='good'):
        current = datetime.now().timestamp()
        if (current - self.last_sended) > interval:
            try:
                self.send(title, text, color)
                self.last_sended = current
            except Exception as e:
                traceback.print_exc()
