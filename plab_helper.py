from __future__ import annotations

import requests
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class PlabHelper:
    def __init__(self, base_url: str):
        self.base_url = base_url

    def _get_stadium_info(self, stadium_id: int) -> dict:
        """just for testing"""
        url = f'{self.base_url}/api/v2/stadium-groups/{stadium_id}/'
        res = requests.get(url, verify=False, timeout=10)
        res.raise_for_status()
        return res.json()

    def get_stadium_name(self, stadium_id: int) -> str:
        return self._get_stadium_info(stadium_id)['name']

    def get_order_url(self, product_id: int) -> str:
        return f'{self.base_url}/rental/{product_id}/order'

    def get_schedules(
        self,
        stadium_id: int,
        date: str,
        start_time_list: list[str],
    ) -> dict[str, any]:
        """get schedules for the stadium"""
        url = f'{self.base_url}/api/v2/stadium-groups/{stadium_id}/products/?date={date}'
        res = requests.get(url, verify=False, timeout=10)
        res.raise_for_status()
        res_json = res.json()
        schedules = []
        stadium_group = res_json['results'][0]
        stadium_group_id = stadium_group['id']
        stadium_group_name = stadium_group['name']
        for stadium in stadium_group['stadiums']:
            stadium_id = stadium['id']
            stadium_name = stadium['name']
            for product in stadium['products']:
                if product['start_t'] not in start_time_list:
                    continue
                if product['product_status'] == 'SOLDOUT':
                    continue
                schedules.append(dict(
                    stadium_group_id=stadium_group_id,
                    stadium_group_name=stadium_group_name,
                    stadium_id=stadium_id,
                    stadium_name=stadium_name,
                    product_id=product['id'],
                    date=product['date'],
                    start_t=product['start_t'],
                    product_status=product['product_status'],
                ))
        return schedules
#        return pl.DataFrame(schedules,
#                            schema={
#                                'stadium_group_id': pl.Int64,
#                                'stadium_group_name': str,
#                                'stadium_id': pl.Int64,
#                                'stadium_name': str,
#                                'product_id': pl.Int64,
#                                'date': str,
#                                'start_t': str,
#                                'product_status': str,
#                            })
