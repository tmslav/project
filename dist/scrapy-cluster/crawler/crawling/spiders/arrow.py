# -*- coding: utf-8 -*-
from urlparse import urljoin
import datetime
import time
import logging

import scrapy
from scrapy import Request
from crawling.items import DetailsItem, AvailabilityItem, PriceItem
from scrapy.exceptions import CloseSpider
from scrapy.shell import open_in_browser as o
from redis_spider import RedisSpider
import ujson

from crawling.spider_utils import standard_meta,catch_exception

PRICE_QUOTE = -1
FACTORY_LEAD_TIME_DEFAULT = "unknown"
FACTORY_LEAD_UOM_DEFAULT = "unknown"
PACKAGE_DEFAULT = "none"
PACKAGING_DEFUALT = "none"
VERSION_DEFAULT = 'none'
TYPE_DEFAULT = 'none'
PART_DETAIL_DEFAULT = 'none'
PRICE_TYPE_DEFAULT = 'default'
QUANTITY_DEFAULT = '-1'
PRICE_DEFAULT = '-1'
STOCK_DEFAULT = '0'


class ArrowSpider(RedisSpider):
    name = "arrow"
    site_name = "arrow"
    start_url = "https://www.arrow.com/en/product-category-sitemap"
    base_url = "https://www.arrow.com/"

    # def start_requests(self):
    #     yield Request(self.start_url)

    @catch_exception
    def parse(self, response):
        links = response.xpath("//h2[@class='Sitemap-heading']/a/@href").extract()
        for link in links:
            yield Request(urljoin(self.base_url, link), callback=self.parse_1, dont_filter=True,meta=standard_meta(response))

    @catch_exception
    def parse_1(self, response):
        links = response.xpath("//ul[@class='CategoryListings-subItems']/li/a/@href").extract()
        for link in links:
            yield Request(urljoin(self.base_url, link), self.parse_2,meta=standard_meta(response))

    @catch_exception
    def parse_2(self, response):
        link = response.xpath("//a/@href").re("search\?prodline\=(.*)")
        url_pattern = "https://www.arrow.com/productsearch/searchajax?page={}&q=&prodline={}"
        if link and link[0] != 'Register':
            yield Request(url_pattern.format(1, link[0]), self.parse_3,meta=standard_meta(response))

    @catch_exception
    def parse_3(self, response):
        try:
            pd = ujson.loads(response.body)
        except:
            logging.info("cant parse json for url={}".format(response.url))
            return
        if pd['data'].get('totalResultCount'):
            number_of_products = pd['data']['totalResultCount'] / 50
            url_pattern = response.url.replace("page=1", "page={}")

            for i in range(1, number_of_products + 1):
                yield Request(url_pattern.format(i), self.parse_4, dont_filter=True,meta=standard_meta(response))

    @catch_exception
    def parse_4(self, response):
        try:
            pd = ujson.loads(response.body)
        except:
            logging.info("cant parse json for url={}".format(response.url))
            return
        results = pd['data']['results']
        for result in results:
            yield Request(urljoin(self.base_url, result['partUrl']), self.parse_item, meta=standard_meta(response,{'pd': result}))

    @catch_exception
    def parse_item(self, response):
        pd = response.meta['pd']
        i = DetailsItem()
        i['site_name'] = self.name
        i['site_url'] = self.base_url
        i['site_part_id'] = pd['partId']
        i['manuf_part_id'] = pd['partNumber']
        i['manuf_name'] = pd['manufacturer']
        i['description'] = pd['description']
        i['datasheet_link'] = urljoin(self.base_url, pd['datasheetUrl'])
        i['image_url'] = pd['imageUrl'] if pd['imageUrl'] else "none"
        i['page_url'] = response.url
        part_detail = response.xpath("//ul[@class='Part-Specifications-list']").extract()
        if part_detail:
            i['part_detail'] = part_detail[0]
        else:
            i['part_detail'] = PART_DETAIL_DEFAULT
        i['package'] = PACKAGE_DEFAULT
        i['packaging'] = PACKAGING_DEFUALT
        i['version'] = VERSION_DEFAULT
        i['type'] = TYPE_DEFAULT
        i['date_created'] = self.timestamp()
        url = response.url + "/buyingoptions?cur=USD"
        return Request(url, self.parse_price, meta=standard_meta(response,{'pd': i}))

    def parse_price(self, response):
        prices = response.xpath("//dt[@data-quantity and @data-price]")
        i = response.meta['pd']
        for price in prices:
            pi = PriceItem()
            pi['site_name'] = self.name
            pi['site_part_id'] = i['site_part_id']
            pi['date_created'] = self.timestamp()
            pi['price_type'] = PRICE_TYPE_DEFAULT
            quantity = price.xpath("@data-quantity").extract()
            pi['quantity'] = quantity[0] if quantity else QUANTITY_DEFAULT
            price = price.xpath("@data-price").extract()
            pi['price'] = price[0] if price else PRICE_DEFAULT
            i['price_data'].append(pi)
        avail = AvailabilityItem()
        avail['site_name'] = self.name
        avail['site_part_id'] = i['site_part_id']
        avail['date_created'] = self.timestamp()
        stock = response.xpath("//@data-product-quantity-max").extract()
        avail['stock'] = stock[0] if stock else STOCK_DEFAULT
        try:
            factory_leadtime, factory_lead_uom, _, _ = response.xpath("//strong").re("lead time.*(\d+)\s+(\w+)")
        except:
            factory_lead_uom = FACTORY_LEAD_UOM_DEFAULT
            factory_leadtime = FACTORY_LEAD_TIME_DEFAULT

        avail['factory_leadtime'] = factory_leadtime
        avail['factory_lead_uom'] = factory_lead_uom
        i['inventory_data'].append(avail)
        yield i

    def timestamp(self):
        return datetime.datetime.now()
