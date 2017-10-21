#encoding=utf-8
#########################################################################
# File Name: start_server.sh
# Author: GuoTianyou
# mail: fortianyou@gmail.com
# Created Time: 日 10/ 8 21:32:11 2017
#! /bin/bash

#########################################################################
time=(`date +%Y%m%d`)
python2.7 website/manage.py runserver
#python2.7 website/manage.py runserver
echo $! > process_id
