#!/bin/bash
tmux new-session -d -s my_server
tmux send-keys -t my_server:0 "bash" C-m
tmux send-keys -t my_server:0 ". /home/ubuntu/project/env/bin/activate" C-m
tmux send-keys -t my_server:0 "cd /home/ubuntu/project/crawler/crawling" C-m
tmux send-keys -t my_server:0 "scrapy runspider spiders/avnet.py --loglevel=INFO" C-m
tmux new-window -n htop
tmux send-keys -t my_server:1 "htop" C-m#!/usr/bin/env bash