from base64 import b64encode

import requests

from ..structure import Brand


class BrandsSpider(object):
    """
    爬取品牌相关数据。
    """
    url = 'https://www.autohome.com.cn/ashx/AjaxIndexCarFind.ashx?type=11'

    def __init__(self):
        self._brands = []
        """:type: list[Brand]"""

    @property
    def brands(self, logo=True):
        with requests.session() as req:
            resp = req.get(self.url)
            for _b in resp.json()['result']['branditems']:
                brand = Brand(_b['id'], _b['name'], _b['bfirstletter'],
                              _b['logo'])
                if logo:
                    logo_resp = req.get(_b['logo'])
                    brand.brand_logo = b64encode(logo_resp.content).decode()
                self._brands.append(brand)
                yield brand
