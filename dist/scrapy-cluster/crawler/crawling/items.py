# -*- coding: utf-8 -*-

# Define here the models for your scraped items

from scrapy import Item, Field
import scrapy
from scrapy.loader.processors import TakeFirst

class RawResponseItem(Item):
    appid = Field()
    crawlid = Field()
    url = Field()
    response_url = Field()
    status_code = Field()
    status_msg = Field()
    headers = Field()
    body = Field()
    links = Field()
    attrs = Field()



class DetailsItem(scrapy.Item):
    # define the fields for your item here like:
    site_name = scrapy.Field(output_processor=TakeFirst())
    site_url = scrapy.Field(output_processor=TakeFirst())
    site_part_id = scrapy.Field(output_processor=TakeFirst())
    manuf_part_id = scrapy.Field(output_processor=TakeFirst())
    manuf_name = scrapy.Field(output_processor=TakeFirst())
    description = scrapy.Field(output_processor=TakeFirst())
    datasheet_link = scrapy.Field(output_processor=TakeFirst())
    image_url = scrapy.Field()
    page_url = scrapy.Field(output_processor=TakeFirst())
    id = scrapy.Field(output_processor=TakeFirst())
    part_detail = scrapy.Field(output_processor=TakeFirst())
    package = scrapy.Field(output_processor=TakeFirst())
    packaging = scrapy.Field(output_processor=TakeFirst())
    type = scrapy.Field(output_processor=TakeFirst())
    version = scrapy.Field(output_processor=TakeFirst())
    date_created = scrapy.Field(output_processor=TakeFirst())
    inventory_data = scrapy.Field()
    price_data = scrapy.Field()
    def __init__(self,*args,**kwargs):
        super(DetailsItem,self).__init__(*args,**kwargs)
        self['inventory_data'] = []
        self['price_data'] = []


class AvailabilityItem(scrapy.Item):
    site_name = scrapy.Field(output_processor=TakeFirst())
    site_part_id = scrapy.Field(output_processor=TakeFirst())
    date_created = scrapy.Field()

    stock = scrapy.Field(output_processor=TakeFirst())
    factory_leadtime = scrapy.Field(output_processor=TakeFirst())
    factory_lead_uom = scrapy.Field(output_processor=TakeFirst())
    other_text = scrapy.Field(output_processor=TakeFirst())

class PriceItem(scrapy.Item):
    site_name = scrapy.Field(output_processor=TakeFirst())
    site_part_id = scrapy.Field(output_processor=TakeFirst())
    date_created = scrapy.Field()

    price_type = scrapy.Field(output_processor=TakeFirst())
    quantity = scrapy.Field(output_processor=TakeFirst())
    price = scrapy.Field(output_processor=TakeFirst())