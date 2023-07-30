# -*- coding: utf-8 -*-
# pylint:disable=missing-timeout,unused-import,invalid-name
from __future__ import print_function

import json
import os
import socket
import traceback
from datetime import datetime

import requests

try:
    import urllib.request as urlrequest
    from urllib.parse import urlencode, urljoin
except ImportError:
    from urllib import urlencode

    import urllib2 as urlrequest
    from urlparse import urljoin


class Slack:
    def __init__(self, url, stamp='', title='', **kwargs):
        self.url = url
        self.stamp = stamp
        self.title = title
        self.kwargs = kwargs

        self.last_sended = 0.

    def _send(self, payload):
        headers = {'content-type': 'application/json',
                   'Accept-Charset': 'UTF-8'}
        data = json.dumps(payload)
        _ = requests.post(self.url, data=data.encode('utf-8'), headers=headers)

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
            'footer': f'{socket.gethostname()}:{os.getcwd()}' if with_hostname
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
            except Exception:
                traceback.print_exc()
