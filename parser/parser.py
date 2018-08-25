import json
import os

import requests
from scrapy.selector import Selector


class Serializer(object):
    @staticmethod
    def read(_file):
        if os.path.isfile(_file):
            with open(_file, mode='r') as f:
                return json.load(f)
        else:
            return None

    @staticmethod
    def write(_file, _obj):
        with open(_file, mode='w+') as f:
            json.dump(_obj, f)


class Request(object):
    @staticmethod
    def get(_url):
        response = requests.get(_url)
        data = Selector(text=response.text)
        return data


def use_cache(func):
    def wrapper(*args, **kwargs):
        cache_file = kwargs.get('cache_file')
        if cache_file:
            serialized_result = Serializer.read(cache_file)
            if not serialized_result:
                serialized_result = func(*args)
                Serializer.write(cache_file, serialized_result)
            return serialized_result
        else:
            return func(*args)
    return wrapper


@use_cache
def download_cars(_base_url, _pages):
    _cars = list()
    for page in _pages:
        list_page = Request.get(f'{_base_url}/nowe/strona-{page}/?s=1')
        cars_on_page = list_page.xpath("//a[@class='car-notice-new group-offer']")
        for car in cars_on_page:
            details = Selector(text=car.extract())
            name = details.xpath("//h2[@class='primary-header new-car-header']/text()")
            _cars.append({
                'name': name[0].extract().strip(),
                'href': car.attrib['href'],
            })
    return _cars


@use_cache
def download_specs(_base_url, _cars):
    for car in _cars:
        car['specs'] = list()
        unique_specs = list()

        car_specs_page = Request.get(f"{_base_url}{car.get('href')}")
        car_specs = car_specs_page.xpath("//a[@class='configuration-row']")
        for spec in car_specs:
            car_version_page = Request.get(f"{_base_url}{spec.attrib['href']}")
            spec_name = car_version_page.xpath("//div[@class='name']/strong/text()")[0]
            spec_details = car_version_page.xpath("//a[contains(text(), 'Zobacz pełne dane techniczne')]")
            spec_href = spec_details.attrib['href']
            if spec_href not in unique_specs:
                unique_specs.append(spec_href)
                car['specs'].append({
                    'name': spec_name.extract(),
                    'href': spec_href,
                })
    return _cars


@use_cache
def download_params(_base_url, _specs):
    for car in _specs:
        for spec in car.get('specs'):
            spec['params'] = list()

            param_page = Request.get(f"{base_url}{spec.get('href')}")
            params_list = param_page.xpath("//div[@class='dt-row']").extract()
            for param in params_list:
                param_name_value = Selector(text=param)
                param_name = param_name_value.xpath("//div[@class='dt-row__text__content']/text()")[0]
                param_value = param_name_value.xpath("//span[@class='dt-param-value']/text()")
                if param_value:
                    spec['params'].append({
                        'name': param_name.extract(),
                        'value': param_value[0].extract(),
                    })
    return _specs


base_url = 'https://m.autocentrum.pl'
pages = range(1, 21 + 1)
cars = download_cars(base_url, pages, cache_file='cache/cars.json')
specs = download_specs(base_url, cars, cache_file='cache/specs.json')
params = download_params(base_url, specs, cache_file='cache/params.json')

sorted_cars = sorted([(
    [
        str(p['value']) for p in car['specs'][0]['params']
        if p['name'] == 'Prześwit'
    ],
    car['name'],
) for car in params])

fast_cars = sorted([(
    [
        [
            str(p['value']) for p in spec['params']
            if 'Przyspieszenie' in p['name']
        ] for spec in car['specs']
    ],
    car['name'],
) for car in params])

print('Done!')
