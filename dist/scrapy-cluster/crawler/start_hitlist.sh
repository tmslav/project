#!/bin/bash
tmux new-session -d -s my_server
tmux send-keys -t my_server:0 "bash" C-m
tmux send-keys -t my_server:0 ". /home/ubuntu/project/env/bin/activate" C-m
tmux send-keys -t my_server:0 "cd /home/ubuntu/project/crawler/crawling" C-m
tmux send-keys -t my_server:0 "scrapy runspider spiders/digikey.py -a name='digikey_hitlist' --loglevel=INFO" C-m
tmux new-window -n avnet
tmux send-keys -t my_server:1 "bash" C-m
tmux send-keys -t my_server:1 ". /home/ubuntu/project/env/bin/activate" C-m
tmux send-keys -t my_server:1 "cd /home/ubuntu/project/crawler/crawling" C-m
tmux send-keys -t my_server:1 "scrapy runspider spiders/avnet.py -a name='avnet_hitlist' --loglevel=INFO" C-m
tmux new-window -n arrow
tmux send-keys -t my_server:2 "bash" C-m
tmux send-keys -t my_server:2 ". /home/ubuntu/project/env/bin/activate" C-m
tmux send-keys -t my_server:2 "cd /home/ubuntu/project/crawler/crawling" C-m
tmux send-keys -t my_server:2 "scrapy runspider spiders/arrow.py -a name='arrow_hitlist' --loglevel=INFO" C-m
tmux new-window -n htop
tmux send-keys -t my_server:3 "htop" C-m