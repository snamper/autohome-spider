import requests

from .series import SeriesSpider
from ..structure import Series, Spec


class SpecsSpider(object):
    """
    爬取车型数据。
    """
    url_tpl = 'https://www.autohome.com.cn/ashx/AjaxIndexCarFind.ashx?type=5&value={series_id}'

    def __init__(self, series=None):
        """
        :type series: list[Series]
        """
        self.specs = []
        """:type: list[Spec]"""
        self.series = series

    def obtain(self):
        if self.series is None:
            spider = SeriesSpider()
            spider.obtain()
            self.series = spider.series

        with requests.session() as req:
            for series in self.series:
                url = self.url_tpl.format(series_id=series.series_id)
                self._obtain(series, req.get(url))

    def _obtain(self, series, resp):
        for _y in resp.json()['result']['yearitems']:
            for _s in _y['specitems']:
                spec = Spec(_s['id'], _s['name'], _y['name'], _s['state'],
                            _s['minprice'], _s['maxprice'], series=series)
                self.specs.append(spec)
