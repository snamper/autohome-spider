class Brand(object):
    def __init__(self, brand_id, brand_name, brand_first_letter, brand_logo):
        """
        :type brand_id: int
        :type brand_name: str
        :type brand_first_letter: str
        :type brand_logo: str
        """
        self.brand_id = brand_id
        self.brand_name = brand_name
        self.brand_first_letter = brand_first_letter
        self.brand_logo = brand_logo


class Factory(object):
    def __init__(self, factory_id, factory_name, factory_first_letter, brand):
        """
        :type factory_id: int
        :type factory_name: str
        :type factory_first_letter: str
        :type brand: Brand
        """
        self.factory_id = factory_id
        self.factory_name = factory_name
        self.factory_first_letter = factory_first_letter
        self.brand = brand


class Series(object):
    def __init__(self, series_id, series_name, series_first_letter,
                 series_state, series_order, factory, brand=None):
        """
        :type series_id: int
        :type series_name: str
        :type series_first_letter: str
        :type series_state: int
        :type series_order: int
        :type factory: Factory
        :type brand: Brand
        """
        self.series_id = series_id
        self.series_name = series_name
        self.series_first_letter = series_first_letter
        self.series_state = series_state
        self.series_order = series_order
        self.factory = factory
        self.brand = brand or factory.brand


class Spec(object):
    def __init__(self, spec_id, spec_name, spec_year_name, spec_state,
                 spec_min_price, spec_max_price, series, factory=None,
                 brand=None):
        """
        :type spec_id: int
        :type spec_name: str
        :type spec_year_name:
        :type spec_state: int
        :type spec_min_price: int
        :type spec_max_price: int
        :type series: Series
        :type factory: Factory
        :type brand: Brand
        """
        self.spec_id = spec_id
        self.spec_name = spec_name
        self.spec_year_name = spec_year_name
        self.spec_state = spec_state
        self.spec_min_price = spec_min_price
        self.spec_max_price = spec_max_price
        self.series = series
        self.factory = factory or series.factory
        self.brand = brand or series.brand
