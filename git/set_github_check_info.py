#!/usr/bin/python3
# -*- coding: UTF-8 -*-
import requests
# import sys

# project_owner = sys.argv[1]
# project_name = sys.argv[2]
# checker_name = sys.argv[3]
# checker_token = '8f70a010cd546a4c6f3e61d1cdba5628fb339d4b'
# commit_SHA = sys.argv[5]
# result_state = sys.argv[6]  # pending, success, failure, error
# result_url = sys.argv[7]
# result_desc = sys.argv[8]

project_owner = 'shinnng'
project_name = 'PlatON-CI'
checker_name = 'shinnng'
checker_token = '4f6026be8f416e4d203dd4871df70f1197ae9a82'
commit_SHA = 'aff10fca4115f07f77821d9eac9fa7516f6b3fee'
result_state = 'pending'
result_url = 'http://www.baidu.com'
result_desc = 'this is a test!'

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