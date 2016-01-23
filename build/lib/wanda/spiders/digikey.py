# -*- coding: utf-8 -*-
from urlparse import urljoin
import datetime
import time
import logging

import scrapy
from scrapy import Request
from scrapy.loader import ItemLoader
from wanda.items import DetailsItem, AvailabilityItem, PriceItem
from scrapy.exceptions import CloseSpider
from scrapy.shell import open_in_browser as o
from webbrowser import open as ol
import ujson
import ipdb


def browser(response):
    ol(response.url)


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


class ArrowSpider(scrapy.Spider):
    name = "digikey"
    site_name = "digikey"
    start_url = "http://www.digikey.com/product-search/en"
    base_url = "https://www.digikey.com/"
    drop_count_items = 142057
    processed_items = 0

    def start_requests(self):
        yield Request(self.start_url)

    def parse(self, response):
        links = response.xpath("//li/a[contains(@href,'product-search')]/@href").extract()
        for link in links:
            yield Request(urljoin(self.base_url,link)+"?pageSize=500",self.parse_1)
    def parse_1(self,response):
        next = response.xpath("//a[@class='Next']/@href").extract()
        if next:
            yield Request(urljoin(self.base_url,next[0]),self.parse_1)
        products = response.xpath("//td[@class='digikey-partnumber']/a/@href").extract()
        for link in products:
            yield Request(urljoin(self.base_url,link),self.parse_item)

    def parse_item(self,response):
        i = DetailsItem()
        i['site_name'] = self.site_name
        i['site_url'] = self.base_url
        loader = ItemLoader(i,response=response)
        loader.add_xpath("site_part_id","//meta[@itemprop='productID']/@content")
        loader.add_xpath("manuf_part_id","//meta[@itemprop='name']/@content")
        loader.add_xpath("manuf_name","//span[@itemprop='name']/text()")
        loader.add_xpath("description","//td[@itemprop='description']/text()")
        loader.add_xpath("datasheet_link","//a[@class='lnkDatasheet']/@href")
        loader.add_xpath("image_url","//a[@class='lnkProductPhoto']/@href")
        loader.add_value("page_url",response.url)
        loader.add_xpath("part_detail","//td[@class='attributes-table-main']")
        loader.add_xpath("packaging","//th[contains(text(),'Packaging')]/following-sibling::td/text()")
        loader.add_xpath("package","//th[contains(text(),'Standard Package')]/following-sibling::td/text()")
        loader.add_value("package",PACKAGE_DEFAULT)
        loader.add_value("packaging",PACKAGING_DEFUALT)
        loader.add_xpath("type","//th[text()='Accessory Type']/following-sibling::td/text()")
        loader.add_value("version",VERSION_DEFAULT)
        loader.add_value("date_created",self.timestamp())
        i=loader.load_item()

        prices = response.xpath("//table[@id='pricing']/tr[td and not(contains(.//text(),'Call'))]")
        for price in prices:
            td = price.xpath("td")
            if len(td)==3:
                pi = PriceItem()
                pi['site_name'] = self.site_name
                pi['site_part_id'] = i['site_part_id']
                pi['date_created'] = self.timestamp()
                pi['price_type'] = i['packaging']
                pi['quantity'] = td[0].xpath("text()").extract()[0]
                pi['price'] = td[1].xpath("text()").extract()[0]
                i['price_data'].append(pi)

        avail = AvailabilityItem()
        avail['site_name'] = self.site_name
        avail['site_part_id'] = i['site_part_id']
        avail['date_created'] = self.timestamp()
        loader = ItemLoader(avail,response=response)
        loader.add_xpath("stock","//td[@id='quantityavailable']",re='":\s([\d|\,]*)')
        loader.add_value("factory_leadtime",FACTORY_LEAD_TIME_DEFAULT)
        loader.add_value("factory_lead_uom",FACTORY_LEAD_UOM_DEFAULT)
        avail = loader.load_item()
        i['inventory_data'].append(avail)
        self.processed_items+=1
        if self.processed_items==self.drop_count_items:
            raise CloseSpider("Sample collected")
        return i


    def timestamp(self):
        return datetime.datetime.fromtimestamp(time.time()).strftime('%m/%d/%Y %H:%M:%S')