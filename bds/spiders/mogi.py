import scrapy
from scrapy.item import Item, Field
import requests
import json

class LocationItem(Item):
    title = Field()
    districts = Field()

class DistrictItem(Item):
    average_price = Field()
    data = Field()
    streets = Field()
    name = Field()

class StreetItem(Item):
    average_price = Field()
    WardName = Field()
    StreetName = Field()
    PrevAvgPrice = Field()
    PriceChangedPercentage = Field()
    AveragePrice = Field()
    data = Field()

class MogiSpider(scrapy.Spider):
    name = "mogi"
    allowed_domains = ["mogi.vn"]
    start_urls = ["https://mogi.vn/gia-nha-dat"]

    def parse(self, response):
        location = response.xpath("//h2[@class='mt-location-title']")
        districts = response.xpath("//div[@class='district']")

        # city
        for loc, dist in zip(location, districts):
            item = LocationItem()

            item['title'] = loc.xpath("text()").extract()[0]
            item['districts'] = list()
            
            dist_info = dist.xpath(".//div[@class='mt-row clearfix']")

            # district
            for each_dist in dist_info:
                dist_item = DistrictItem()
                district_name = each_dist.xpath(".//a/text()").extract()[0].strip()
                dist_item['average_price'] = each_dist.xpath(".//span/text()").extract()[0].split('/')[0]
                dist_item['name'] = district_name
                
                url = each_dist.xpath(".//a/@href").extract()[0]
                district_id = url.split('qd')[-1]
                
                # district summary
                getHousePriceSummaryUrl = "https://mogi.vn/MarketPrice/GetHousePriceSummary_ByDistrict?districtId=" + district_id
                response = requests.get(getHousePriceSummaryUrl)
                dist_data = json.loads(response.text)['Data']
                
                for type in dist_data:
                    del type['AvgPriceDisplay']
                    del type['MinPriceDisplay']
                    del type['MaxPriceDisplay']
                    del type['AvgRoomDisplay']
                    del type['AvgAreaDisplay']

                dist_item['data'] = dist_data
                
                # street
                getByDistrictUrl = "https://mogi.vn/MarketPrice/GetByDistrict?districtId=" + district_id
                response = requests.get(getByDistrictUrl)
                street_data = json.loads(response.text)['Data']

                dist_item['streets'] = list()
                for street_info in street_data:
                    street_item = StreetItem()
                    
                    # street summary
                    street_name = street_info['StreetName']
                    street_item['WardName'] = street_info['WardName']
                    street_item['StreetName'] = street_info['StreetName']
                    street_item['AveragePrice'] = street_info['AvgPrice']
                    street_item['PrevAvgPrice'] = street_info['PrevAvgPrice']
                    street_item['PriceChangedPercentage'] = street_info['PriceChangedPercentage']

                    
                    # street detail by month
                    district_id = street_info['DistrictId']
                    ward_id = street_info['WardId']
                    street_id = street_info['StreetId']
                    getMonthlyByStreet = f"https://mogi.vn/MarketPrice/GetHousePriceMonthly_ByStreet?districtId={district_id}&wardId={ward_id}&streetId={street_id}"
                    response = requests.get(getMonthlyByStreet)
                    street_month_data = json.loads(response.text)['Data']

                    street_by_month = dict()
                    for entry in street_month_data:
                        if entry['MonthId'] == 0:
                            continue

                        month = str(entry['MonthId'])[4:] + "/" + str(entry['MonthId'])[:4]

                        if month not in street_by_month:
                            street_by_month[month] = dict()

                        street_by_month[month][entry['PropertyTypeName']] = entry['AvgPrice']
                        if entry['AvgPrice'] == 0:
                            street_by_month[month][entry['PropertyTypeName']] = None


                    street_item['data'] = street_by_month
                    dist_item['streets'].append(street_item)
                

                    # break
                item['districts'].append(dist_item)
                # break                
            yield item
            # break