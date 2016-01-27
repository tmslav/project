#import redis
import functools

from scrapy import signals
from scrapy.exceptions import DontCloseSpider
from scrapy.spiders import Spider
from crawling.redis_queue import RedisPriorityQueue


class ErrorCatcher(type):
    def __new__(cls, name, bases, dct):
        for m in dct:
            if hasattr(dct[m], '__call__'):
                dct[m] = catch_exception(dct[m])
        return type.__new__(cls, name, bases, dct)


class RedisSpider(Spider):
    '''
    Base Spider for doing distributed crawls coordinated through Redis
    '''
    redis_conn = None # the redis connection
    queue = None # the queue to use for crawling
    spider = None # the spider using this scheduler
    queue_class = None # the class to use for the queue
    dupefilter = None # the redis dupefilter
    item_retries = 0 # the number of extra tries to get an item

    def __init__(self,*args,**kwargs):
        super(RedisSpider,self).__init__(*args,**kwargs)

    def _set_crawler(cls, crawler):
        crawler.signals.connect(cls.spider_idle, signal=signals.spider_idle)
        crawler.signals.connect(cls.engine_stopped, signal=signals.engine_stopped)

    def spider_idle(self):
        raise DontCloseSpider("dont_close")

    def engine_stopped(self):
        import subprocess
        subprocess.call(["sudo", "shutdown", "-h", "now"])

    def parse(self, response):
        '''
        Parse a page of html, and yield items into the item pipeline

        @param response: The response object of the scrape
        '''
        raise NotImplementedError("Please implement parse() for your spider")

    def reconstruct_headers(self, response):
        """
        Purpose of this method is to reconstruct the headers dictionary that
        is normally passed in with a "response" object from scrapy.

        Args:
            response: A scrapy response object

        Returns: A dictionary that mirrors the "response.headers" dictionary
        that is normally within a response object

        Raises: None
        Reason: Originally, there was a bug where the json.dumps() did not
        properly serialize the headers. This is method is way to circumvent
        the known issue
        """

        header_dict = {}
        # begin reconstructing headers from scratch...
        for key in response.headers.keys():
            key_item_list = []
            key_list = response.headers.getlist(key)
            for item in key_list:
                key_item_list.append(item)
            header_dict[key] = key_item_list
        return header_dict


