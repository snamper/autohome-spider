import json
import os

from ..spider.brands import BrandsSpider
from .. import BaseCommand


class Command(BaseCommand):
    description = '爬取品牌相关数据。'

    def add_arguments(self, parser):
        """
        :type parser: ArgumentParser
        """
        parser.add_argument('--fmt', default='csv', choices=('csv', 'json'),
                            help='文件输出格式（默认：csv）')

    def handle(self, *args, **options):
        fmt = options['fmt']

        spider = BrandsSpider()
        spider.obtain()

        self.output(spider, fmt=fmt)

    def output(self, spider, fmt='csv'):
        """
        :type spider: BrandsSpider
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
        :type spider: BrandsSpider
        """
        with open('brands.csv', 'w+') as f:
            f.write('brand_logo,brand_id,brand_name,brand_first_letter\n')
            for _b in spider.brands:
                f.write(','.join([
                    _b.brand_logo,
                    str(_b.brand_id),
                    _b.brand_name,
                    _b.brand_first_letter,
                ]))
                f.write('\n')

    @classmethod
    def write_json(cls, spider):
        """
        :type spider: BrandsSpider
        """
        with open('brands.json', 'w+') as f:
            brands = [{
                'brand_logo': _b.brand_logo,
                'brand_id': _b.brand_id,
                'brand_name': _b.brand_name,
                'brand_first_letter': _b.brand_first_letter,
            } for _b in spider.brands]
            f.write(json.dumps(brands))
