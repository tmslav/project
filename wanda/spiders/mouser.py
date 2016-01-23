# -*- coding: utf-8 -*-
from urlparse import urljoin
import datetime
import time
from copy import deepcopy
import logging

import scrapy
from scrapy import Request
from wanda.items import DetailsItem, AvailabilityItem, PriceItem
from scrapy.exceptions import CloseSpider

PRICE_QUOTE = -1
FACTORY_LEAD_TIME_DEFAULT = "unknown"
FACTORY_LEAD_UOM_DEFAULT = "unknown"


class MouserSpider(scrapy.Spider):
    name = "mouser"
    site_name = "Mouser"
    base_url = "http://www.mouser.com/"
    base_url2 = "http://www2.mouser.com"
    first_url = "http://www.mouser.com/Electronic-Components/"
    start_url = "https://www.mouser.com/api/CrossDomain/GetContext?syncDomains=www2&returnUrl=http:%2f%2feu.mouser.com%2flocalsites.aspx&async=False&setPrefSub=True&clearPrefSub=False"
    drop_count_items = 90000
    processed_items = 0
    headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Cache-Control': 'no-cache',
        'Connection': 'keep-alive',
        'Pragma': 'no-cache',
        'Accept-Encoding': 'gzip, deflate, sdch',
        'Accept-Language': 'en-US,en;q=0.8,hr;q=0.6',
        'Upgrade-Insecure-Requests': '1'
    }
    def __init__(self,*args,**kwargs):
        #self.download_delay = 0
        super(MouserSpider,self).__init__(*args,**kwargs)

    def start_requests(self):
        yield Request(
            self.start_url,
        )

    def parse(self, response):
        yield Request(
            self.first_url,
            callback=self.parse_1
        )

    def parse_1(self, response):
        url = "http://www.mouser.com/api/Preferences/SetSubdomain?subdomainName=www2"
        body = "subdomainName=www2"
        headers = {"X-Requested-With": "XMLHttpRequest"}
        return Request(url, body=body, headers=headers, callback=self.parse_2, method='POST')

    def parse_2(self, response):
        url = "http://www.mouser.com/api/Preferences/SetCurrency?subdomainName=www2&currencyCode=USDe"
        body = "subdomainName=www2&currencyCode=USD"
        headers = {"X-Requested-With": "XMLHttpRequest"}
        return Request(url, body=body, headers=headers, callback=self.parse_4, method='POST', dont_filter=True, )

    def parse_4(self, response):
        cookie = map(lambda x: " ".join(x.split()), response.request.headers.get("Cookie").split(";"))
        # cookie[3]=cookie[3].replace("ps=www&CNB=1","")
        cookie = 'preferences=pl=en-GB&pc_eu=EUR&ps=www2&CNB=1&pc_www2=zzz'
        custom_header = deepcopy(self.headers)
        custom_header['Cookie'] = cookie
        custom_header['Referer'] = "http://eu.mouser.com/localsites.aspx"
        return Request("http://www.mouser.com/Electronic-Components/", headers=custom_header, callback=self.parse_5,
                       meta={'dont_redirect': True, 'handle_httpstatus_list': [302], 'cookiefix': cookie,
                             'dont_merge_cookies': True},
                       dont_filter=True, )

    def parse_5(self, response):
        custom_header = deepcopy(self.headers)
        new_cookies = response.headers.get("Set-Cookie").split(";")[0]
        custom_header['Cookie'] = "preferences=pl=en-GB&pc_eu=EUR&ps=www2&CNB=1&pc_www2=zzz"
        custom_header['Referer'] = 'http://eu.mouser.com/localsites.aspx'
        return Request(response.headers.get("Location"), headers=custom_header, callback=self.parse_6, dont_filter=True,
                       meta={'dont_redirect': True, 'handle_httpstatus_list': [302], 'dont_merge_cookies': True,
                             'custom_header': custom_header})

    def parse_6(self, response):
        url = response.xpath("//script[@defer]/@src").extract()[0]
        return Request(urljoin("http://www2.mouser.com/",url), callback=self.parse_7,
                       headers=response.meta['custom_header'], meta={'dont_redirect': True,'response_headers':response.headers,'headers' : response.request.headers})

    def parse_7(self,response):
        custom_headers = response.meta['headers']
        custom_headers['X-Distil-Ajax'] = response.headers['X-Ah']
        return Request(
            "http://www2.mouser.com/Electronic-Components/",headers=custom_headers,callback=self.parse_8
        )

    def parse_8(self, response):
        links = response.xpath("//li[@class='sub-cat']/a/@href").extract()
        for link in links:
            return Request(
                urljoin(self.base_url2, link).replace("../", ""),
                callback=self.parse_9
            )

    def parse_9(self, response):
        next_url = response.xpath("//a[text()='Next']/@href").extract()
        if next_url:
            print "next_url",next_url
            yield Request(urljoin(self.base_url2, next_url[0]), self.parse_9)

        products = response.xpath("//a[contains(@id,'_lnkMouserPartNumber')]/@href").extract()
        for link in products:
            yield Request(urljoin(self.base_url2, link).replace("../../../../", ""), self.parse_item)

    def parse_item(self, response):
        import ipdb;ipdb.set_trace()
        try:
            i = DetailsItem()

            i['site_name'] = self.site_name
            i['site_url'] = self.base_url
            i['site_part_id'] = response.xpath("//div[@id='divMouserPartNum']/text()").extract()[0]
            i['manuf_part_id'] = response.xpath("//div[@id='divManufacturerPartNum']/h1/text()").extract()
            i['manuf_name'] = response.xpath("//a[@class='manNameLink']/text()").extract()
            i['description'] = response.xpath("//div[@id='divDes']/text()").extract()
            i['datasheet_link'] = response.xpath("//a[contains(@id,'lnkCatalogDataSheetIcon')]/@href").extract()
            image_url = response.xpath("//img[@id='ctl00_ContentMain_img1']/@src").extract()
            if image_url:
                image_url = urljoin(self.base_url, image_url[0].replace("../../../", ""))
            else:
                image_url = ""
            i['image_url'] = [image_url]
            i['page_url'] = response.url
            # id = scrapy.Field(output_processor=TakeFirst())
            i['part_detail'] = response.xpath("//table[@class='specs']").extract()
            # package = scrapy.Field(output_processor=TakeFirst())
            i['packaging'] = response.xpath("//span[contains(@id,'ctl12_lblName')]/text()").extract()
            i['type'] = "none"
            i['version'] = 'none'
            i['date_created'] = self.timestamp()

            pricing = response.xpath("//div[contains(@id,'ctl00_ContentMain_ucP_rptrPriceBreaks_ctl')]")
            prices = {}

            pricing_div = response.xpath("//div[@class='ProductDetail']/div/div[not(contains(@id,'divChkBox'))]")
            if pricing.xpath(".//input[@type='radio']"):
                price_type = "default"
                price_all = []
                for div in pricing_div:
                    if div.xpath("@id") and "Msg" not in div.xpath("@id").extract()[0]:
                        price_type = div.xpath(".//a/text()").extract()
                        if not price_type:
                            price_type = div.xpath("./div/text()").extract()[0]
                            price_type = " ".join(price_type[0].split())
                        else:
                            price_type = price_type[0]
                        price_all.append(price_type)
                        continue
                    elif div.xpath("@id") and "Msg" in div.xpath("@id").extract()[0]:
                        pass
                    else:
                        quantity = div.xpath(".//a/text()").extract()[0]
                        price_elem = div.xpath(".//span").re("\$(.*)\<")
                        if price_elem:
                            price_value = min(map(lambda x: float(x.replace(",", "")), price_elem))
                        else:
                            price_value = PRICE_QUOTE
                    prices.setdefault(price_type, []).append((quantity, price_value))
            else:
                if pricing_div:
                    div0 = pricing_div[0]
                    price_type = None
                    if div0.xpath("@id"):
                        price_type = div0.xpath("./div/text()").extract()[0]
                        price_type = " ".join(price_type[0].split())
                    for div in pricing_div:
                        try:
                            quantity = div.xpath(".//a/text()").extract()[0]
                        except:
                            continue
                        try:
                            price_value = min(map(lambda x: float(x.replace(",", "")), div.xpath(".//span").re("\$(.*)\<")))
                        except:
                            price_value = PRICE_QUOTE
                        prices.setdefault(price_type if price_type else "default", []).append((quantity, price_value))
                else:
                    logging.info("no price for url = {}".format(response.url))

            for k, v in prices.iteritems():
                for price in v:
                    pi = PriceItem()
                    pi['site_name'] = self.site_name
                    pi['site_part_id'] = i['site_part_id']
                    pi['date_created'] = self.timestamp()
                    pi['price_type'] = k
                    pi['price'] = price[1]
                    pi['quantity'] = price[0]
                    i['price_data'].append(pi)

            avail = response.xpath("//div[@id='availability']")
            ai = AvailabilityItem()
            if avail:
                stock_string = avail.xpath("//div[@class='av-col2']").re("(.*)Can Ship")
                if stock_string:
                    string_int = int(stock_string[0].replace(",", ""))
                    ai['site_name'] = self.site_name
                    ai['site_part_id'] = i['site_part_id']
                    ai['date_created'] = self.timestamp()
                    ai['stock'] = string_int
                    factory_info = response.xpath(
                        "//b[contains(text(),'Factory Lead-Time')]/../following-sibling::div/text()")
                    if factory_info:
                        factory_info_split = factory_info.re("([\d|\,]+)\s(\w+)")
                        if len(factory_info_split) == 2:
                            ai['factory_leadtime'], ai['factory_lead_uom'] = factory_info_split
                        else:
                            ai['factory_leadtime'], ai['factory_lead_uom'] = (
                            FACTORY_LEAD_TIME_DEFAULT, FACTORY_LEAD_UOM_DEFAULT)
                    else:
                        logging.warning("no factory_info for url={}".format(response.url), loglevel=logging.INFO)
                    i['inventory_data'].append(ai)
            self.processed_items+=1
            if self.processed_items==self.drop_count_items:
                raise CloseSpider("Sample collected")
            return i
        except:
            import traceback
            traceback.print_exc()
            print "cant parse url = {}".format(response.url)


    def timestamp(self):
        return datetime.datetime.fromtimestamp(time.time()).strftime('%m/%d/%Y %H:%M:%S')
