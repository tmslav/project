import sys
sys.path.append('../../aws_db/')

import os
os.environ['DJANGO_SETTINGS_MODULE'] = 'aws_db.settings'
import django
django.setup()

REDIS_HOST = '52.90.105.198'
REDIS_PORT = '6379'

# Kafka server information
KAFKA_HOSTS = '52.90.105.198'
KAFKA_TOPIC_PREFIX = 'demo'
LOG_LEVEL="INFO"

# Scrapy Settings
# ~~~~~~~~~~~~~~~

# Scrapy settings for distributed_crawling project
#
DOWNLOADER_CLIENTCONTEXTFACTORY = 'crawling.context_factory.TLS12ContextFactory'

SPIDER_MODULES = ['crawling.spiders']
NEWSPIDER_MODULE = 'crawling.spiders'

# Enables scheduling storing requests queue in redis.
SCHEDULER = "crawling.distributed_scheduler.DistributedScheduler"

# Don't cleanup redis queues, allows to pause/resume crawls.
SCHEDULER_PERSIST = True

# how long we want the duplicate timeout queues to stick around in seconds
DUPEFILTER_TIMEOUT = 60

# how many times to retry getting an item from the queue before the spider is considered idle
SCHEUDLER_ITEM_RETRIES = 3

# Store scraped item in redis for post-processing.
ITEM_PIPELINES = {
    'crawling.pipelines.MySQLStoreToAmazonPipeline':100,
    #'crawling.pipelines.KafkaPipeline': 200,
}

SPIDER_MIDDLEWARES = {
    # disable built-in DepthMiddleware, since we do our own
    # depth management per crawl request
    'scrapy.contrib.spidermiddleware.depth.DepthMiddleware': None,
}

DOWNLOADER_MIDDLEWARES = {
    # Handle timeout retries with the redis scheduler and logger
    #'scrapy.contrib.downloadermiddleware.retry.RetryMiddleware' : None,
    'crawling.rotate_user_agent.RotateUserAgentMiddleware' :400,
    'crawling.redis_retry_middleware.RedisRetryMiddleware': 510,
}
CONCURRENT_REQUESTS=32
# Disable the built in logging in production
LOG_ENABLED = True

# Allow all return codes
HTTPERROR_ALLOW_ALL = True

RETRY_TIMES = 3

DOWNLOAD_TIMEOUT = 120

# Local Overrides
# ~~~~~~~~~~~~~~~

# try:
#     from localsettings import *
# except ImportError:
#     pass
