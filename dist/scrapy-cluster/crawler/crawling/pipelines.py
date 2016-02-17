# -*- coding: utf-8 -*-

# Define your item pipelines here

import json
import datetime as dt

import redis
from kafka import KafkaClient, SimpleProducer
from crawling.redis_queue import RedisPriorityQueue
from app_aws_db.models import AvailabilityItem, DetailsItem, PriceItem


class KafkaPipeline(object):
    """Pushes serialized item to appropriate Kafka topics."""

    def __init__(self, producer, topic_prefix, aKafka):
        self.producer = producer
        self.topic_prefix = topic_prefix
        self.topic_list = []
        self.kafka = aKafka

    @classmethod
    def from_settings(cls, settings):
        kafka = KafkaClient(settings['KAFKA_HOSTS'])
        producer = SimpleProducer(kafka)
        topic_prefix = settings['KAFKA_TOPIC_PREFIX']
        return cls(producer, topic_prefix, kafka)

    @classmethod
    def from_crawler(cls, crawler):
        return cls.from_settings(crawler.settings)

    def process_item(self, item, spider):
        datum = dict(item)
        datum["timestamp"] = dt.datetime.utcnow().isoformat()
        prefix = self.topic_prefix
        appid_topic = "{prefix}.crawled_{appid}".format(prefix=prefix,
                                                        appid=datum["appid"])
        firehose_topic = "{prefix}.crawled_firehose".format(prefix=prefix)
        try:
            message = json.dumps(datum)
        except:
            message = 'json failed to parse'

        self.checkTopic(appid_topic)
        self.checkTopic(firehose_topic)

        self.producer.send_messages(appid_topic, message)
        self.producer.send_messages(firehose_topic, message)

        return item

    def checkTopic(self, topicName):
        if topicName not in self.topic_list:
            self.kafka.ensure_topic_exists(topicName)
            self.topic_list.append(topicName)


class MySQLStoreToAmazonPipeline(object):
    def __init__(self, redis_conn):
        self.redis_conn = redis_conn

    @classmethod
    def from_settings(cls, settings):
        REDIS_HOST = settings.get("REDIS_HOST")
        REDIS_PORT = settings.get("REDIS_PORT")
        redis_conn = redis.Redis(host=REDIS_HOST, port=REDIS_PORT)
        return cls(redis_conn)

    @classmethod
    def from_crawler(cls, crawler):
        return cls.from_settings(crawler.settings)

    def process_item(self, item, spider):
        # return deferToThread(self._proces_item,item,spider)
        return self._proces_item(item, spider)

    def _proces_item(self, item, spider):
        filtered = {k: v for k, v in item.iteritems() if k != 'inventory_data' and k != 'price_data' and k != 'hitlist'}
        item1 = DetailsItem.objects.create(**filtered)
        if item.get("hitlist"):
            queue = RedisPriorityQueue(self.redis_conn, item.get("hitlist") + ":results")
            queue.push(item, 100)

        for i in item['inventory_data']:
            item2 = AvailabilityItem.objects.create(**i)
        for i in item['price_data']:
            item3 = PriceItem.objects.create(**i)
        return item
