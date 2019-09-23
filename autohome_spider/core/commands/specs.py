import os

from ..spider.specs import SpecsSpider
from ..structure import Brand, Factory, Series
from .. import BaseCommand, CommandError


class Command(BaseCommand):
    description = '爬取车型数据。'

    def add_arguments(self, parser):
        """
        :type parser: ArgumentParser
        """
        parser.add_argument('--fmt', default='csv', choices=('csv', 'json'),
                            help='文件输出格式（默认：csv）')
        parser.add_argument('--series-path', nargs='?',
                            default='dist/series.csv',
                            help='加载本地车系数据（默认：dist/series.csv）')

    def handle(self, *args, **options):
        fmt = options['fmt']
        series_path = options['series_path']

        series = None
        if series_path is not None:
            try:
                series = self.load_series(series_path)
            except CommandError as e:
                self.stderr.write('Warning: %s\n' % e.msg)
        spider = SpecsSpider(series=series)

        self.output(spider, fmt=fmt)

    def output(self, spider, fmt='csv'):
        """
        :type spider: SpecsSpider
        :type fmt: str
        """
        if not os.path.exists('dist'):
            os.mkdir('dist')
        os.chdir('dist')
        if fmt == 'csv':
            self.write_csv(spider)
        elif fmt == 'json':
            self.write_json(spider)

    @classmethod
    def write_csv(cls, spider):
        """
        :type spider: SpecsSpider
        """
        with open('specs.csv', 'w+') as f:
            f.write(','.join([
                'brand_id,brand_name,brand_first_letter',
                'factory_id,factory_name,factory_first_letter',
                'series_id,series_name,series_first_letter',
                'series_state,series_order',
                'spec_id,spec_name,spec_year_name,spec_state',
                'spec_min_price,spec_max_price',
            ]))
            f.write('\n')
            for _s in spider.specs:
                f.write(','.join([
                    str(_s.brand.brand_id),
                    _s.brand.brand_name,
                    _s.brand.brand_first_letter,
                    str(_s.factory.factory_id),
                    _s.factory.factory_name,
                    _s.factory.factory_first_letter,
                    str(_s.series.series_id),
                    _s.series.series_name,
                    _s.series.series_first_letter,
                    str(_s.series.series_state),
                    str(_s.series.series_order),
                    str(_s.spec_id),
                    _s.spec_name,
                    _s.spec_year_name,
                    str(_s.spec_state),
                    str(_s.spec_min_price),
                    str(_s.spec_max_price),
                ]))
                f.write('\n')

    @classmethod
    def write_json(cls, spider):
        """
        :type spider: SpecsSpider
        """
        # TODO(hypc): 输出到json文件
        pass

    @classmethod
    def load_series(cls, series_path):
        """
        :type series_path: str
        :rtype: list[Series]
        """
        if not os.path.exists(series_path):
            raise CommandError('No such file: %s' % series_path)

        series = []
        """:typeL list[Series]"""
        with open(series_path, 'r') as f:
            for line in f.readlines():
                line = line.strip()
                if line.startswith('brand_id') or line == '':
                    continue
                _l = line.split(',')
                brand = Brand(int(_l[0]), _l[1], _l[2], '')
                factory = Factory(int(_l[3]), _l[4], _l[5], brand)
                series.append(Series(int(_l[6]), _l[7], _l[8], int(_l[9]),
                                     int(_l[10]), factory))
        return series
