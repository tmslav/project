__author__ = 'tomislav'
import functools
from scrapy.exceptions import  CloseSpider

def standard_meta(response, add_dict={}):
    ret = {}
    ret['crawlid'] = response.meta['crawlid']
    ret['appid'] = response.meta['appid']
    ret['spiderid'] = response.meta['spiderid']
    ret['expires'] = 0
    ret['priority'] = response.meta['priority'] + 10  # so we go sooner to next depth
    ret.update(add_dict)
    return ret

def catch_exception(*args,**kwargs):
    @functools.wraps(args[0])
    def new_func(spider,response):
        crawler_function = args[0]
        try:
            return crawler_function(spider,response)
        except Exception as e:
            import ipdb;ipdb.set_trace()
            raise CloseSpider
    return new_func
