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
from scrapy.shell import open_in_browser

PRICE_QUOTE = -1
FACTORY_LEAD_TIME_DEFAULT = "unknown"
FACTORY_LEAD_UOM_DEFAULT = "unknown"


class MouserSpider(scrapy.Spider):
    name = "mouser"
    site_name = "Mouser"
    base_url = "http://www.mouser.com/"
    base_url2 = "http://www2.mouser.com"
    first_url = "http://www.mouser.com/Electronic-Components/"

    headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Cache-Control': 'no-cache',
        'Connection': 'keep-alive',
        'Pragma': 'no-cache',
        'Accept-Encoding': 'gzip, deflate, sdch',
        'Accept-Language': 'en-US,en;q=0.8,hr;q=0.6',
        'Upgrade-Insecure-Requests': '1'
    }
    default_headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Encoding': 'gzip, deflate, sdch',
        'Accept-Language': 'en-US,en;q=0.8,hr;q=0.6',
        'Cache-Control': 'no-cache',
        'Connection': 'keep-alive',
        'Host': 'mouser.com',
        'Pragma': 'no-cache',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/48.0.2564.103 Safari/537.36'
    }
    payload = "p=%7B%22appName%22%3A%22Netscape%22%2C%22platform%22%3A%22MacIntel%22%2C%22cookies%22%3A1%2C%22syslang%22%3A%22en-US%22%2C%22userlang%22%3A%22en-US%22%2C%22cpu%22%3A%22%22%2C%22productSub%22%3A%2220030107%22%2C%22setTimeout%22%3A0%2C%22setInterval%22%3A0%2C%22plugins%22%3A%7B%220%22%3A%22WidevineContentDecryptionModule%22%2C%221%22%3A%22ChromePDFViewer%22%2C%222%22%3A%22ShockwaveFlash%22%2C%223%22%3A%22NativeClient%22%2C%224%22%3A%22ChromePDFViewer%22%7D%2C%22mimeTypes%22%3A%7B%220%22%3A%22WidevineContentDecryptionModuleapplication%2Fx-ppapi-widevine-cdm%22%2C%221%22%3A%22application%2Fpdf%22%2C%222%22%3A%22ShockwaveFlashapplication%2Fx-shockwave-flash%22%2C%223%22%3A%22FutureSplashPlayerapplication%2Ffuturesplash%22%2C%224%22%3A%22NativeClientExecutableapplication%2Fx-nacl%22%2C%225%22%3A%22PortableNativeClientExecutableapplication%2Fx-pnacl%22%2C%226%22%3A%22PortableDocumentFormatapplication%2Fx-google-chrome-pdf%22%7D%2C%22screen%22%3A%7B%22width%22%3A1440%2C%22height%22%3A900%2C%22colorDepth%22%3A24%7D%2C%22fonts%22%3A%7B%220%22%3A%22HoeflerText%22%2C%221%22%3A%22Monaco%22%2C%222%22%3A%22Georgia%22%2C%223%22%3A%22TrebuchetMS%22%2C%224%22%3A%22Verdana%22%2C%225%22%3A%22AndaleMono%22%2C%226%22%3A%22Monaco%22%2C%227%22%3A%22CourierNew%22%2C%228%22%3A%22Courier%22%7D%7D"

    def __init__(self, *args, **kwargs):
        # self.download_delay = 0
        super(MouserSpider, self).__init__(*args, **kwargs)

    def start_requests(self):
        headers = deepcopy(self.default_headers)
        headers['X-Distil-CS'] = 'BYPASS'
        yield Request(
            self.base_url,
            headers=headers,
            meta={'dont_redirect': True}
        )

    def parse(self, response):
        jsurl = response.xpath("//script/@src").extract()[0]
        url = urljoin(self.base_url, jsurl)
        yield Request(
            url,
            callback=self.parse_1,
            headers=self.default_headers,
        )

    def parse_1(self, response):
        parse_1_headers = deepcopy(self.default_headers)
        parse_1_headers['X-Distil-Ajax'] = response.headers['X-Ah']
        jsurl = response.headers['X-Ju']

        return Request(urljoin(self.base_url, jsurl),
                       headers=parse_1_headers, callback=self.parse_2, body=self.payload, method='POST')

    def parse_2(self, response):
        url_pattern = "distil_identify_cookie.html?uid={}&d_ref=/&qs=".format(response.headers['X-Uid'])
        body_pattern = "uid={}&d_ref=/&qs=".format(response.headers['X-Uid'])
        return Request(urljoin(self.base_url, url_pattern), body=body_pattern, headers=self.default_headers,
                       callback=self.parse_4, method='POST',
                       meta={'dont_redirect': True, 'handle_httpstatus_list': [302]})

    def parse_4(self, response):
        parse_4_headers = deepcopy(self.default_headers)
        parse_4_headers['Cookie'] = response.request.headers['Cookie']
        parse_4_headers['Referer'] = 'http://mouser.com/'
        return Request(self.base_url.replace("www.", ""), headers=parse_4_headers,
                       meta={'dont_redirect': True,
                             'handle_httpstatus_list': [302], },
                       callback=self.parse_5, dont_filter=True)

    def parse_5(self, response):
        import ipdb;ipdb.set_trace()
        jsurl = response.xpath("//script/@src").extract()[0]
        url = urljoin(self.base_url, jsurl)
        yield Request(
            url,
            callback=self.parse_6,
            headers=self.default_headers, dont_filter=True)

    def parse_6(self, response):
        import ipdb;
        ipdb.set_trace()

    def parse_9(self, response):
        import ipdb;
        ipdb.set_trace()
        next_url = response.xpath("//a[text()='Next']/@href").extract()
        if next_url:
            print "next_url", next_url
            yield Request(urljoin(self.base_url2, next_url[0]), self.parse_9)

        products = response.xpath("//a[contains(@id,'_lnkMouserPartNumber')]/@href").extract()
        for link in products:
            yield Request(urljoin(self.base_url2, link).replace("../../../../", ""), self.parse_item)

    def parse_item(self, response):
        import ipdb;
        ipdb.set_trace()
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
                            price_value = min(
                                map(lambda x: float(x.replace(",", "")), div.xpath(".//span").re("\$(.*)\<")))
                        except:
                            price_value = PRICE_QUOTE
                        prices.setdefault(price_type if price_type else "default", []).append(
                            (quantity, price_value))
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
            self.processed_items += 1
            if self.processed_items == self.drop_count_items:
                raise CloseSpider("Sample collected")
            return i
        except:
            import traceback
            traceback.print_exc()
            print "cant parse url = {}".format(response.url)

    def timestamp(self):
        return datetime.datetime.fromtimestamp(time.time()).strftime('%m/%d/%Y %H:%M:%S')
