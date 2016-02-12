from scrapy.downloadermiddlewares.retry import RetryMiddleware
from scrapy import log
from redis_queue import RedisPriorityQueue
import redis

class RedisRetryMiddleware(RetryMiddleware):

    def __init__(self, settings):
        RetryMiddleware.__init__(self, settings)
        self.redis_conn =  redis.Redis(host=settings.get('REDIS_HOST'),
                                            port=settings.get('REDIS_PORT'))

    def _retry(self, request, reason, spider):

        retries = request.meta.get('retry_times', 0) + 1
        if retries <= self.max_retry_times:
            log.msg(format="Retrying %(request)s " \
                            "(failed %(retries)d times): %(reason)s",
                    level=log.DEBUG, spider=spider, request=request,
                    retries=retries, reason=reason)
            retryreq = request.copy()
            retryreq.meta['retry_times'] = retries
            retryreq.dont_filter = True
            # our priority setup is different from super
            retryreq.meta['priority'] = retryreq.meta['priority'] - 10
            return retryreq
        else:
            self.queue = RedisPriorityQueue(self.redis_conn,spider.name + ":queue")
            log.msg("Putting back to redis queue %(request)",level=log.INFO,request=request)
            request.dont_filter=True
            req_dict = self.request_to_dict(request)
            self.queue.push(req_dict, req_dict['meta']['priority']/2)
            log.msg(format="Gave up retrying %(request)s "\
                            "(failed %(retries)d times): %(reason)s",
                    level=log.DEBUG, spider=spider, request=request,
                    retries=retries, reason=reason)

    def request_to_dict(self, request):
        '''
        Convert Request object to a dict.
        modified from scrapy.utils.reqser
        '''
        callback = getattr(request.callback,"__name__",None)
        req_dict = {
            # urls should be safe (safe_string_url)
            'callback':callback if callback else 'parse',
            'url': request.url.decode('ascii'),
            'method': request.method,
            'headers': dict(request.headers),
            'body': request.body,
            'cookies': request.cookies,
            'meta': request.meta,
            '_encoding': request._encoding,
            'priority': request.priority,
            'dont_filter': request.dont_filter,
        }
        return req_dict
