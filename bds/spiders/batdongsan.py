from time import sleep
import scrapy
import json
import undetected_chromedriver as uc
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.remote_connection import LOGGER
from selenium.webdriver.common.service import logger as service_logger
import logging
from scrapy.selector import Selector
import requests
from bs4 import BeautifulSoup
import json
import re
LOGGER.setLevel(logging.WARNING)
service_logger.setLevel(logging.WARNING)

def getNestedKey(json, key):
    if key in json:
        return json[key]
    for k, v in json.items():
        if isinstance(v,dict):
            item = getNestedKey(v, key)
            if item is not None:
                return item
    return None

class BatdongsanSpider(scrapy.Spider):
    name = "batdongsan"
    allowed_domains = ["batdongsan.com.vn"]

    headers = {
        'authority': 'api-angel-green.batdongsan.com.vn',
        'accept': '*/*',
        'accept-language': 'vi-VN,vi;q=0.9,fr-FR;q=0.8,fr;q=0.7,en-US;q=0.6,en;q=0.5',
        'content-type': 'application/json',
        'origin': 'https://batdongsan.com.vn',
        'referer': 'https://batdongsan.com.vn/',
        'sec-ch-ua': '"Chromium";v="116", "Not)A;Brand";v="24", "Google Chrome";v="116"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-site',
    }
    total_page = 3

    def __init__(self, name=None, **kwargs):
        super().__init__(name, **kwargs)

        options = uc.ChromeOptions()
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-gpu')
        self.driver = uc.Chrome(driver_executable_path=ChromeDriverManager().install(), options=options)
    
    def start_requests(self):
        start_urls = 'https://api-angel-green.batdongsan.com.vn/graphql/bds'
        for page_number in range(1, self.total_page + 1):
            json_data = {
                'operationName': 'Query',
                'variables': {
                    'page': page_number,
                    'pageSize': 6,
                    'market': 'vn',
                    'language': 'vn',
                    'category': [
                        'price-insights',
                    ],
                    'exclude': [
                        760727,
                    ],
                },
                'query': 'query Query($page: Int, $pageSize: Int, $market: String!, $language: String, $category: [String], $exclude: [Int], $tag: String) {\n  articleList(\n    page: $page\n    pageSize: $pageSize\n    market: $market\n    language: $language\n    category: $category\n    exclude: $exclude\n    tag: $tag\n  ) {\n    totalCount\n    totalPage\n    items {\n      id\n      title\n      excerpt\n      slug\n      link\n      featuredImage\n      postDate\n      modifiedDate\n      location\n      author {\n        id\n        name\n        slug\n        link\n        profilePhoto\n        __typename\n      }\n      sponsor {\n        slug\n        name\n        picture\n        bio\n        __typename\n      }\n      category {\n        id\n        name\n        slug\n        link\n        __typename\n      }\n      tags {\n        id\n        name\n        slug\n        link\n        __typename\n      }\n      profiles {\n        id\n        name\n        slug\n        link\n        __typename\n      }\n      __typename\n    }\n    __typename\n  }\n}',
            }
            yield scrapy.Request(url=start_urls, method='POST', headers=self.headers, body=json.dumps(json_data), callback=self.parse)
            

    def parse(self, response):
        response_json = json.loads(response.body)
        for item in response_json['data']['articleList']['items']:
            url = item['link']
            abs_url = 'https://batdongsan.com.vn/phan-tich-danh-gia' + url
            
            print("Processing: ", abs_url)

            self.driver.get(abs_url)
            sleep(5)
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            sleep(5)

            page_html = self.driver.page_source
            response_obj = Selector(text=page_html)

            iframes = response_obj.xpath('//iframe[contains(@src, "infogram")]')
            for iframe in iframes:
                url = iframe.xpath('./@src').get()
                r = requests.get(url, allow_redirects=True)
                html = r.content

                soup = BeautifulSoup(html, 'html.parser')
                title = soup.title.text

                def contains_infographic_data(tag):
                    return tag.name == 'script' and 'infographicData' in tag.text

                script = soup.find_all(contains_infographic_data)[0].text
                data = re.search(r'window\.infographicData=(\{.*\})', script).group(1)
                json_data = json.loads(data)
                key = 'data'
                chart_data = getNestedKey(json_data, key)
                
                save_data = dict()
                save_data['title'] = title
                save_data['data'] = dict()

                try:
                    for i in chart_data[0][0]:
                        if i is not None and i != '':
                            save_data['data'][i['value']] = dict()

                    for i, (house, house_data) in enumerate(save_data['data'].items()):
                        for year_data in chart_data[0]:
                            if year_data[0] is not None and year_data[0] != '':
                                house_data[year_data[0]['value']] = year_data[i + 1]['value']
                except:
                    for i in chart_data[0][0]:
                        if i is not None and i != '':
                            clean = i.replace('\n', '').strip()
                            normalize = ' '.join(clean.split())
                            save_data['data'][normalize] = dict()

                    for i, (house, house_data) in enumerate(save_data['data'].items()):
                        for year_data in chart_data[0]:
                            if year_data[0] is not None and year_data[0] != '':
                                clean = year_data[0].replace('\n', '').strip()
                                normalize = ' '.join(clean.split())
                                house_data[normalize] = year_data[i + 1]
                yield save_data
            