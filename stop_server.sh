#encoding=utf-8
#########################################################################
# File Name: stop_server.sh
# Author: GuoTianyou
# mail: fortianyou@gmail.com
# Created Time: 日 10/ 8 21:42:39 2017
#! /bin/bash

#########################################################################

id=(`cat process_id`)
echo $id
kill -9 $id
id2=$[id+1]
kill -9 $id2
