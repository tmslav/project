__author__ = 'tomislav'
import requests
from celery.contrib import rdb

from celery.task import task, periodic_task
from .models import Results, DetailModel
from app_aws_db.models import DetailsItem
from datetime import timedelta
from .redis_queue import RedisPriorityQueue
import redis
from scrapy import Selector
from urlparse import urljoin
import random

REDIS_HOST = 'localhost'
REDIS_PORT = '6379'

SPIDER_URL_TEMPLATES = {
    'arrow': ('https://www.arrow.com/productsearch/searchajax?q={}', 'parse_4'),
    'avnet': (
    'http://avnetexpress.avnet.com/store/em/EMController?langId=-1&storeId=500201&catalogId=500201&term={}&x=36&y=18&searchType=&advAction=&N=0&Ne=100000&action=products',
    'parse_overview_for_items'),
    'digikey': ('http://www.digikey.com/product-search/en?keywords={}', 'parse_item')
}

redis_conn = redis.Redis(host=REDIS_HOST, port=REDIS_PORT)


def submit_csv(csv, search_name, *args, **kwargs):
    size = len(csv)
    res = Results.objects.create(status='processing', search_name=search_name)
    for line in csv:
        DetailModel.objects.create(csv_id=res, part_id=line.replace('\n', ''))


@periodic_task(run_every=timedelta(seconds=2))
def process_results():
    res = Results.objects.filter(status='processing')
    if res:
        res = res[0]
        res.status = 'started'
        res.save()
        listings = res.detailmodel_set.all()
        for listing in listings:
            listing.status = 'started'
            listing.save()


@periodic_task(run_every=timedelta(seconds=6))
def process_started():
    started = DetailModel.objects.filter(status='started').first()
    if started:
        started.status = 'searchrds'
        started.save()
        item = DetailsItem.objects.filter(site_part_id=started.part_id).first()
        if item:
            started.status = 'foundrds'
            started.save()
            started.site_name = item.site_name
            started.url = item.page_url
            started.save()
        else:
            started.status = 'notfoundrds'
            started.save()
    else:
        pass
        # check if there is a processed items for some rds


@periodic_task(run_every=timedelta(seconds=2))
def process_notfoundrds():
    notfoundrds = DetailModel.objects.filter(status='notfoundrds').first()
    if notfoundrds:
        for spider_name, properties in SPIDER_URL_TEMPLATES.iteritems():
            url_pattern, func = properties
            notfoundrds.status = 'onhitlist'
            notfoundrds.save()
            queue_request(url_pattern.format(notfoundrds.part_id), spider_name, func)
        notfoundrds.csv_id.in_queue += 1
        notfoundrds.csv_id.save()


@periodic_task(run_every=timedelta(seconds=5))
def process_onhitlist():
    onhitlist = DetailModel.objects.filter(status='onhitlist').first()
    if onhitlist:
        item = DetailsItem.objects.filter(site_part_id=onhitlist.part_id).all()
        if item:
            onhitlist.status = 'hitlistfound'
            onhitlist.url = item[0].page_url
            onhitlist.site_name = item[0].site_name
            onhitlist.csv_id.inqueue -= 1
        else:
            pass


@periodic_task(run_every=timedelta(seconds=4))
def update_count():
    items = Results.objects.all()
    for item in items:
        parts_found_rds = item.detailmodel_set.filter(status='foundrds').count()
        parts_send_hitlist = item.detailmodel_set.filter(status='onhitlist').count()
        parts_found_hitlist = item.detailmodel_set.filter(status='hitlistfound').count()
        item.parts_found_in_rds = parts_found_rds
        item.parts_send_to_hitlist = parts_send_hitlist
        item.parts_found_by_hitlist_add_to_rds = parts_found_hitlist
        total_parts = item.detailmodel_set.count()
        not_found = total_parts - parts_found_rds - parts_found_hitlist
        item.parts_not_found = not_found
        percent = (parts_found_rds + parts_found_hitlist) / float(total_parts) * 100
        item.percent_found = percent
        if parts_found_rds + parts_found_hitlist == total_parts:
            item.status = 'done'
        else:
            item.status = 'working'
        item.save()


def queue_request(url, spider_id, func):
    spiderid = spider_id + "_hitlist"
    req_dict = {
        # urls should be safe (safe_string_url)
        'callback': func,
        'url': url,
        'method': 'GET',
        '_encoding': None,
        'priority': 10,
        'dont_filter': True,
        'meta': {'appid': spiderid, 'spiderid': spiderid,
                 'crawlid': "".join(map(str, random.sample(xrange(10000), 3)))}
    }
    queue = RedisPriorityQueue(redis_conn, spiderid + ":queue")
    print req_dict
    queue.push(req_dict, 100)
