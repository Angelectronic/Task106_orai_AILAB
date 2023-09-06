import scrapy
import requests
import json

class NhatotSpider(scrapy.Spider):
    name = "nhatot"
    allowed_domains = ["www.nhatot.com"]
    
    start_urls = ["https://www.google.com/"]        

    def parse(self, response):
        print(response.status)
        full_data = []

        # Nhà ở
        url = 'https://gateway.chotot.com/v1/public/api-pty/market-price/overview?cg=1020'
        r = requests.get(url, allow_redirects=True)
        data = r.json()
        chart = data['charts']

        for i in chart:
            del i['type_id']
            del i['type_key']
            del i['area']
            del i['ward']
            del i['background']
            del i['color']
            del i['bar_color']
            

        import datetime 
        for i in chart:
            for j in i['value']:
                # month / year
                j['time'] = datetime.datetime.fromtimestamp(j['time']).strftime("%m/%Y")

        full_data += chart

        # Căn hộ/Chung cư
        url = 'https://gateway.chotot.com/v1/public/api-pty/market-price/overview?cg=1010'
        r = requests.get(url, allow_redirects=True)
        data = r.json()
        chart = data['charts']

        for i in chart:
            del i['type_id']
            del i['type_key']
            del i['area']
            del i['ward']
            del i['background']
            del i['color']
            del i['bar_color']
            

        import datetime 
        for i in chart:
            for j in i['value']:
                # month / year
                j['time'] = datetime.datetime.fromtimestamp(j['time']).strftime("%m/%Y")

        full_data += chart

        # Nhà ở
        for city in data['statistics']:
            region = city['region']
            url = 'https://gateway.chotot.com/v1/public/api-pty/market-price/chart?cg=1020&region=' + str(region)
            r = requests.get(url, allow_redirects=True)
            city_data = r.json()
            chart = city_data['charts']
            for i in chart:
                del i['type_id']
                del i['type_key']
                del i['area']
                del i['ward']
                # del i['background']
                del i['color']
                del i['bar_color']
            
            for i in chart:
                for j in i['value']:
                    # month / year
                    j['time'] = datetime.datetime.fromtimestamp(j['time']).strftime("%m/%Y")

            full_data += chart

        # Căn hộ/Chung cư
        for city in data['statistics']:
            region = city['region']
            url = 'https://gateway.chotot.com/v1/public/api-pty/market-price/chart?cg=1010&region=' + str(region)
            r = requests.get(url, allow_redirects=True)
            city_data = r.json()
            chart = city_data['charts']
            for i in chart:
                del i['type_id']
                del i['type_key']
                del i['area']
                del i['ward']
                # del i['background']
                del i['color']
                del i['bar_color']
            
            for i in chart:
                for j in i['value']:
                    # month / year
                    j['time'] = datetime.datetime.fromtimestamp(j['time']).strftime("%m/%Y")

            full_data += chart

        url = 'https://gateway.chotot.com/v2/public/chapy-pro/market-price-index-conf'
        r = requests.get(url, allow_redirects=True)
        data = r.json()

        for city in data['regions']:
            region = list(city.keys())[0]
            district = city[region]['area']
            for i in district:
                area = list(i.keys())[0]
                
                # Nhà ở
                district_url = 'https://gateway.chotot.com/v1/public/api-pty/market-price/chart?cg=1020&region=' + str(region) + '&area=' + str(area)
                r = requests.get(district_url, allow_redirects=True)
                district_data = r.json()
                chart = district_data['charts']
                for i in chart:
                    del i['type_id']
                    del i['type_key']
                    del i['area']
                    del i['ward']
                    # del i['background']
                    del i['color']
                    del i['bar_color']

                for i in chart:
                    for j in i['value']:
                        # month / year
                        j['time'] = datetime.datetime.fromtimestamp(j['time']).strftime("%m/%Y")

                full_data += chart

                # Căn hộ/Chung cư
                district_url = 'https://gateway.chotot.com/v1/public/api-pty/market-price/chart?cg=1010&region=' + str(region) + '&area=' + str(area)
                r = requests.get(district_url, allow_redirects=True)
                district_data = r.json()
                chart = district_data['charts']
                for i in chart:
                    del i['type_id']
                    del i['type_key']
                    del i['area']
                    del i['ward']
                    # del i['background']
                    del i['color']
                    del i['bar_color']

                for i in chart:
                    for j in i['value']:
                        # month / year
                        j['time'] = datetime.datetime.fromtimestamp(j['time']).strftime("%m/%Y")

                full_data += chart

        for item in full_data:
            yield item
