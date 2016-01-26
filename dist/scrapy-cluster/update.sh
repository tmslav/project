#!/usr/bin/env bash
scp -i  ~/Downloads/pem/amazon_test.pem  -r /Users/tomislav/Documents/projects_odesk/test/dist/scrapy-cluster/*  ubuntu@$1:/home/ubuntu/project/
