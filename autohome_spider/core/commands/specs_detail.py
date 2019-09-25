import hashlib
import os

from ..structure import Brand, Factory, Series, Spec
from ..spider.specs_detail import SpecsDetailSpider
from .. import BaseCommand, CommandError


class Command(BaseCommand):
    description = '爬取车型详细数据。'

    def add_arguments(self, parser):
        """
        :type parser: ArgumentParser
        """
        parser.add_argument('--fmt', default='csv', choices=('csv', 'json'),
                            help='文件输出格式（默认：csv）')
        parser.add_argument('--specs-path', nargs='?',
                            default='dist/specs.csv',
                            help='加载本地车型数据（默认：dist/specs.csv）')

    def handle(self, *args, **options):
        fmt = options['fmt']
        specs_path = options['specs_path']

        specs = None
        if specs_path is not None:
            try:
                specs = self.load_specs(specs_path)
            except CommandError as e:
                self.stderr.write('Warning: %s\n' % e.msg)
        spider = SpecsDetailSpider(specs=specs)

        self.output(spider, fmt=fmt)

    def output(self, spider, fmt='csv'):
        """
        :type spider: SpecsDetailSpider
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
        :type spider: SpecsDetailSpider
        """
        spec_properties = [_ for _ in Spec.__slots__ if
                           _ not in ('series', 'factory', 'brand')]
        with open('specs-detail.csv', 'w+') as f:
            head_line = []
            head_line += ['brand_id', 'brand_name', 'brand_first_letter']
            head_line += ['factory_id', 'factory_name', 'factory_first_letter']
            head_line += ['series_id', 'series_name', 'series_first_letter',
                          'series_state', 'series_order']
            head_line += spec_properties
            head_line.append('md5_sum')
            f.write(','.join(head_line))
            f.write('\n')
            for spec in spider.specs:
                line = []
                line += [str(spec.brand.brand_id),
                         spec.brand.brand_name,
                         spec.brand.brand_first_letter]
                line += [str(spec.factory.factory_id),
                         spec.factory.factory_name,
                         spec.factory.factory_first_letter]
                line += [str(spec.series.series_id),
                         spec.series.series_name,
                         spec.series.series_first_letter,
                         str(spec.series.series_state),
                         str(spec.series.series_order)]
                line += [str(getattr(spec, _, '')) for _ in spec_properties]
                line = ','.join(line)
                md5_sum = hashlib.md5(line.encode()).hexdigest()
                f.write('%s,%s' % (line, md5_sum))
                f.write('\n')

    @classmethod
    def write_json(cls, spider):
        """
        :type spider: SpecsDetailSpider
        """
        # TODO(hypc): 输出到json文件
        pass

    @classmethod
    def load_specs(cls, specs_path):
        """
        :type specs_path: str
        :rtype: list[Spec]
        """
        if not os.path.exists(specs_path):
            raise CommandError('No such file: %s' % specs_path)

        specs = []
        """:typeL list[Spec]"""
        with open(specs_path, 'r') as f:
            for line in f.readlines():
                line = line.strip()
                if line.startswith('brand_id') or line == '':
                    continue
                _l = line.split(',')
                brand = Brand(int(_l[0]), _l[1], _l[2], '')
                factory = Factory(int(_l[3]), _l[4], _l[5], brand)
                series = Series(int(_l[6]), _l[7], _l[8], int(_l[9]),
                                int(_l[10]), factory)
                specs.append(Spec(int(_l[11]), _l[12], _l[13], int(_l[14]),
                                  int(_l[15]), int(_l[16]), series))
        return specs
