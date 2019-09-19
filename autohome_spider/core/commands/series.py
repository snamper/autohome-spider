import os

from ..structure import Brand
from ..spider.series import SeriesSpider
from .. import BaseCommand, CommandError


class Command(BaseCommand):
    description = '爬取汽车厂商以及车系相关数据。'

    def add_arguments(self, parser):
        """
        :type parser: ArgumentParser
        """
        parser.add_argument('--fmt', default='csv', choices=('csv', 'json'),
                            help='文件输出格式（默认：csv）')
        parser.add_argument('--brands-path', nargs='?', help='加载本地品牌数据')

    def handle(self, *args, **options):
        fmt = options['fmt']
        brands_path = options['brands_path']

        brands = None
        if brands_path:
            brands = self.load_brands(brands_path)

        spider = SeriesSpider(brands=brands)
        spider.obtain()

        self.output(spider, fmt=fmt)

    def output(self, spider, fmt='csv'):
        """
        :type spider: SeriesSpider
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
        :type spider: SeriesSpider
        """
        with open('factories.csv', 'w+') as f:
            f.write(','.join([
                'brand_id,brand_name,brand_first_letter',
                'factory_id,factory_name,factory_first_letter',
            ]))
            f.write('\n')
            for _f in spider.factories:
                f.write(','.join([
                    str(_f.brand.brand_id),
                    _f.brand.brand_name,
                    _f.brand.brand_first_letter,
                    str(_f.factory_id),
                    _f.factory_name,
                    _f.factory_first_letter,
                ]))
                f.write('\n')

        with open('series.csv', 'w+') as f:
            f.write(','.join([
                'brand_id,brand_name,brand_first_letter',
                'factory_id,factory_name,factory_first_letter',
                'series_id,series_name,series_first_letter',
                'series_state,series_order',
            ]))
            f.write('\n')
            for _s in spider.series:
                f.write(','.join([
                    str(_s.brand.brand_id),
                    _s.brand.brand_name,
                    _s.brand.brand_first_letter,
                    str(_s.factory.factory_id),
                    _s.factory.factory_name,
                    _s.factory.factory_first_letter,
                    str(_s.series_id),
                    _s.series_name,
                    _s.series_first_letter,
                    str(_s.series_state),
                    str(_s.series_order),
                ]))
                f.write('\n')

    @classmethod
    def write_json(cls, spider):
        """
        :type spider: SeriesSpider
        """
        # TODO(hypc): 输出到json文件
        pass

    @classmethod
    def load_brands(cls, brands_path):
        """
        :type brands_path: str
        :rtype: list[Brand]
        """
        if not os.path.exists(brands_path):
            raise CommandError('No such file: %s' % brands_path)

        brands = []
        """:typeL list[Brand]"""
        with open(brands_path, 'r') as f:
            for line in f.readlines():
                line = line.strip()
                if line.startswith('brand_logo') or line == '':
                    continue
                _l = line.split(',')
                brands.append(Brand(int(_l[1]), _l[2], _l[3], ''))
        return brands
