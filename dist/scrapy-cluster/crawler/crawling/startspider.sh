#!/bin/bash
#starting spider
#alias startspider=./startspider.sh
scrapy runspider spiders/$1.py
