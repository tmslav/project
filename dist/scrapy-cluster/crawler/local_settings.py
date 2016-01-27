print "Local settings imported"
# Enable and configure HTTP caching (disabled by default)
# See http://scrapy.readthedocs.org/en/latest/topics/downloader-middleware.html#httpcache-middleware-settings
#HTTPCACHE_ENABLED=True
#HTTPCACHE_EXPIRATION_SECS=40
#HTTPCACHE_DIR='httpcache'
#HTTPCACHE_IGNORE_HTTP_CODES=[]
#HTTPCACHE_STORAGE='scrapy.extensions.httpcache.FilesystemCacheStorage'
CONCURRENT_REQUESTS=32
LOG_LEVEL='DEBUG'
DUPEFILTER_DEBUG = True

REDIS_HOST = 'localhost'
REDIS_PORT = '6379'

# Kafka server information
KAFKA_HOSTS = 'localhost'
KAFKA_TOPIC_PREFIX = 'demo'
#RANDOMIZE_DOWNLOAD_DELAY = True
#DOWNLOAD_DELAY = 0
