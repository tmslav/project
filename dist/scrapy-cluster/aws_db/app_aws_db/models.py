from __future__ import unicode_literals

from django.db import models

PRICE_QUOTE = -1
FACTORY_LEAD_TIME_DEFAULT = "unknown"
FACTORY_LEAD_UOM_DEFAULT = "unknown"
PACKAGE_DEFAULT = "none"
PACKAGING_DEFUALT = "none"
VERSION_DEFAULT = 'none'
TYPE_DEFAULT = 'none'
PART_DETAIL_DEFAULT = 'none'
PRICE_TYPE_DEFAULT = 'default'
QUANTITY_DEFAULT = '-1'
PRICE_DEFAULT = '-1'
STOCK_DEFAULT = '0'
IMAGE_URL_DEFAULT = DATASHEET_LINK_DEFAULT = DESCRIPTION_DEFUALT = 'none'
CATEGORY_NAMES_DEFAULT = ""


class DetailsItem(models.Model):
    class Meta:
        db_table = 'Part'

    # define the fields for your item here like:
    site_name = models.CharField(max_length=20)
    site_url = models.CharField(max_length=50)
    site_part_id = models.CharField(max_length=50)
    manuf_part_id = models.CharField(max_length=50)
    manuf_name = models.CharField(max_length=200)
    description = models.CharField(max_length=300, default=DESCRIPTION_DEFUALT)
    datasheet_link = models.CharField(max_length=300, default=DATASHEET_LINK_DEFAULT)
    image_url = models.CharField(max_length=300, default=IMAGE_URL_DEFAULT)
    page_url = models.CharField(max_length=500)
    id = models.AutoField(primary_key=True)
    part_detail = models.CharField(max_length=5000, default=PART_DETAIL_DEFAULT)
    package = models.CharField(max_length=50, default=PACKAGE_DEFAULT)
    packaging = models.CharField(max_length=50, default=PACKAGING_DEFUALT)
    type = models.CharField(max_length=100, default=VERSION_DEFAULT)
    version = models.CharField(max_length=50, default=VERSION_DEFAULT)
    category_names = models.CharField(max_length=500,default=CATEGORY_NAMES_DEFAULT)
    date_created = models.DateTimeField()


class AvailabilityItem(models.Model):
    class Meta:
        db_table = 'Inventory'
    site_name = models.CharField(max_length=20)
    site_part_id = models.CharField(max_length=50)
    date_created = models.DateTimeField()

    stock = models.IntegerField(default=STOCK_DEFAULT)
    factory_leadtime = models.CharField(max_length=50, default=FACTORY_LEAD_TIME_DEFAULT)
    factory_lead_uom = models.CharField(max_length=50, default=FACTORY_LEAD_UOM_DEFAULT)
    other_text = models.CharField(max_length=50)


class PriceItem(models.Model):
    class Meta:
        db_table = 'Price'
    site_name = models.CharField(max_length=20)
    site_part_id = models.CharField(max_length=50)
    date_created = models.DateTimeField()

    price_type = models.CharField(max_length=50, default=PRICE_TYPE_DEFAULT)
    quantity = models.IntegerField(default=QUANTITY_DEFAULT)
    price = models.FloatField(default=PRICE_DEFAULT)
