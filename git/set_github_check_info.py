#!/usr/bin/python3
# -*- coding: UTF-8 -*-
import requests
import sys

project_owner = sys.argv[1]
project_name = sys.argv[2]
checker_name = sys.argv[3]
checker_token = sys.argv[4]
commit_SHA = sys.argv[5]
result_state = sys.argv[6]
result_url = sys.argv[7]
result_desc = sys.argv[8]

# project_owner = 'shinnng'
# project_name = 'Test'
# checker_name = 'shinnng'
# checker_token = '78057e50a7e30766507ffdd8fda17224f9c0c400'
# commit_SHA = '4b86fd00aacb32bbfc6fb0309232595ba8d0feec'
# result_state = 'failure'
# result_url = 'http://www.baidu.com'
# result_desc = 'test'

url = 'https://api.github.com/repos/' + project_owner + '/' + project_name + '/statuses/' + commit_SHA
headers = {'Accept': 'application/vnd.github.antiope-preview+json'}
data = {}
data['state'] = result_state
data['target_url'] = result_url
data['description'] = result_desc
data['context'] = 'jenkins'

res = requests.post(url=url,
                    json=data,
                    headers=headers,
                    auth=(checker_name, checker_token))
print(res.text)