# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
from scrapy.exceptions import  CloseSpider

class ItemFinishPipeline(object):
    processed_items = 0
    def process_item(self, item, spider):
        return item
