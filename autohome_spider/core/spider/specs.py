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
        self._specs = []
        """:type: list[Spec]"""
        self._series = series

    @property
    def specs(self):
        if self._series is None:
            spider = SeriesSpider()
            self._series = list(spider.series)

        with requests.session() as req:
            for series in self._series:
                url = self.url_tpl.format(series_id=series.series_id)
                yield from self._obtain(series, req.get(url))

    def _obtain(self, series, resp):
        for _y in resp.json()['result']['yearitems']:
            for _s in _y['specitems']:
                spec = Spec(_s['id'], _s['name'], _y['name'], _s['state'],
                            _s['minprice'], _s['maxprice'], series=series)
                self._specs.append(spec)
                yield spec
