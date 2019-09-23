import requests

from .brands import BrandsSpider
from ..structure import Brand, Factory, Series


class SeriesSpider(object):
    """
    爬取汽车厂商以及车系相关数据。
    """
    url_tpl = 'https://www.autohome.com.cn/ashx/AjaxIndexCarFind.ashx?type=13&value={brand_id}'

    def __init__(self, brands=None):
        """
        :type brands: list[Brand]
        """
        self._factories = []
        """:type: list[Factory]"""
        self._series = []
        """:type: list[Series]"""
        self._brands = brands

    @property
    def series(self):
        if self._brands is None:
            spider = BrandsSpider()
            self._brands = list(spider.brands)

        with requests.session() as req:
            for brand in self._brands:
                url = self.url_tpl.format(brand_id=brand.brand_id)
                yield from self._obtain(brand, req.get(url))

    @property
    def factories(self):
        return self._factories

    def _obtain(self, brand, resp):
        for _f in resp.json()['result']['factoryitems']:
            factory = Factory(_f['id'], _f['name'], _f['firstletter'], brand)
            self._factories.append(factory)

            for _s in _f['seriesitems']:
                series = Series(_s['id'], _s['name'], _s['firstletter'],
                                _s['seriesstate'], _s['seriesorder'],
                                factory=factory)
                self._series.append(series)
                yield series
