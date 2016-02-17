# -*- coding: utf-8 -*-
from urlparse import urljoin
import datetime

from scrapy import Request
from scrapy.loader import ItemLoader
from crawling.items import DetailsItem, AvailabilityItem, PriceItem
from redis_spider import RedisSpider
from crawling.spider_utils import standard_meta


class AvnetSpider(RedisSpider):
    name = "avnet"
    site_name = "Avnet"
    base_url = "http://avnetexpress.avnet.com/"
    start_url = "http://avnetexpress.avnet.com/store/em/EMController"

    def parse(self, response):
        links = response.xpath("//script").re("refinementURLs.*'(.*?)\';")
        for link in links:
            yield Request(
                urljoin(self.base_url, link),
                callback=self.parse_category,
                meta=standard_meta(response)
            )

    def parse_category(self, response):
        subcategories = response.xpath("//span[@class='subcatresultslist']/../@href").extract()
        if subcategories:
            for link in subcategories:
                yield Request(
                    urljoin(self.base_url, link),
                    self.parse_category,
                    meta=standard_meta(response)
                )
        else:
            # pagination
            next_page = response.xpath("//table[@id='pagingTable_top']//a[@title='Next']/@href").extract()
            if next_page:
                yield Request(urljoin(self.base_url, next_page[0]), callback=self.parse_category,
                              meta=standard_meta(response))

            for link in self.parse_overview_for_items(response):
                yield link

    def parse_overview_for_items(self, response):
        links = response.xpath("//td[@class='small dataTd']/strong/a/@href").extract()
        for link in links:
            yield Request(
                urljoin(self.base_url, link),
                callback=self.parse_item,
                meta=standard_meta(response),
                priority=10
            )

    def parse_item(self, response):
        loader_wanda = ItemLoader(item=DetailsItem(), response=response)
        if response.meta.get('callback_result_queue'):
            hitlist = response.meta.get('callback_result_queue')

        loader_wanda.add_value('hitlist', hitlist)
        loader_wanda.add_xpath("site_part_id", "//span[@itemprop='sku']/text()")
        loader_wanda.add_value("date_created", self.timestamp())
        loader_wanda.add_value("site_name", self.site_name)
        loader_wanda.add_xpath("image_url", "//img[@id='productMainImage']/@src")
        loader_wanda.add_value("site_url", self.base_url)
        loader_wanda.add_xpath("manuf_part_id", "//span[@itemprop='sku']/text()")
        loader_wanda.add_xpath("manuf_name", "//strong[@itemprop='manufacturer']/text()")
        loader_wanda.add_xpath("description", "//p[@itemprop='description']/text()")
        loader_wanda.add_xpath("datasheet_link", "//a[@class='download']/@href")
        loader_wanda.add_value("page_url", response.url)
        loader_wanda.add_xpath("version", "//*[@itemprop='model']/text()")
        # pattern = "//strong[text()='{}']/../text()"
        pattern = "//td[text()='{}']/following-sibling::td[1]"
        regexp_pattern = "breakupLongText\(\'(.*?)\'"
        loader_wanda.add_xpath("type", pattern.format("Type"), re=regexp_pattern)
        loader_wanda.add_xpath("package", pattern.format("Package Type"), re=regexp_pattern)
        loader_wanda.add_xpath("package", pattern.format("Package"), re=regexp_pattern)
        loader_wanda.add_xpath("part_detail", "//table[@itemprop='description']")
        packaging = response.xpath("//tr[@itemtype='http://schema.org/Offer']//td[@class='filler'][2]").xpath(
            "text()").extract()
        if packaging:
            packaging = " ".join(packaging[0].split())
        else:
            packaging = ""
        loader_wanda.add_value("packaging", packaging)
        price_types = response.xpath("//tr[@itemtype='http://schema.org/Offer']")
        loader_wanda.item['inventory_data'] = []

        for price_type in price_types:
            prices = price_type.xpath("//span[@itemprop='priceSpecification']/div")
            loader_wanda.item['price_data'] = []
            pd = price_type.xpath("//*[@name='cartAdd']/@onclick").re("\(.*\)")
            if pd:
                pdd = pd[0].split(",")

                for price in prices:
                    loader_price = ItemLoader(item=PriceItem(), selector=price)
                    price_type_elem = price_type.xpath(".//td[@class='filler'][2]/text()")
                    if price_type_elem:
                        price_type_text = " ".join(price_type_elem.extract()[0].split())
                    else:
                        price_type_text = ''
                    loader_price.add_value("site_name", self.site_name)
                    loader_price.add_value("price_type", price_type_text)
                    loader_price.add_xpath("price", "@value", re="\$(\d+\.\d+)")
                    loader_price.add_value("site_part_id", " ".join(pdd[8].replace("'", "").split()))
                    price_tmp = loader_price.load_item()
                    qty = price.xpath("../../..//input[contains(@name,'qty')]/@value").extract()
                    if qty:
                        price_tmp['quantity'] = qty[0]
                    else:
                        price_tmp['quantity'] = '0'
                    price_tmp['date_created'] = self.timestamp()
                    price_tmp['quantity'] = price_tmp['quantity'].replace("+", "").replace(",", "")
                    loader_wanda.item['price_data'].append(price_tmp)

                avail = AvailabilityItem()

                if len(pdd) == 15:
                    avail['site_name'] = self.site_name
                    avail['site_part_id'] = " ".join(pdd[8].replace("'", "").split())
                    avail['stock'] = int(pdd[7]) if "null" not in pdd[7] else 0
                    avail['date_created'] = self.timestamp()
                    factory_lead_time_start = price_type.xpath(".//@leadtime")
                    if factory_lead_time_start:
                        factory_lead_time = factory_lead_time_start.re("(\d+).*?(\w+)")
                        if len(factory_lead_time) == 2:
                            avail['factory_leadtime'], avail['factory_lead_uom'] = factory_lead_time

                        if factory_lead_time_start.extract() == ['Call for Delivery']:
                            avail['factory_leadtime'] = "Call for Delivery"

                        if not avail.get("factory_leadtime"):
                            pass
                            # logging.error("err2,response.url={}".format(response.url))
                    loader_wanda.item['inventory_data'].append(avail)
                else:
                    pass
                    # logging.error("err1,response.url={}".format(response.url))
            else:
                pass  # no price found
        return loader_wanda.load_item()

    def timestamp(self):
        return datetime.datetime.now()
