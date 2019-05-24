# -*- coding: UTF-8 -*-
import requests
import sys


project_id = sys.argv[1]
merge_iid = sys.argv[2]
private_token = 'Rw339e9eD6ekc7ny3Suw'

url = 'http://192.168.9.66/api/v4/projects/' + project_id + '/merge_requests/' + merge_iid
headers = {'Accept':'application/json','Content-type':'application/x-www-form-urlencoded','PRIVATE-TOKEN':private_token}
params = 'render_html=true'
response = requests.get(url=url,params=params,headers=headers).json()
title = response.get('title')
description = response.get('description')
f = open('submit_info_cache', 'w')
f.write('submitInfo=' + title + '\n' + 'submitDetail=' + description)
