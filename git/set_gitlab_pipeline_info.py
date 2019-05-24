import requests
import sys

# project_name = sys.argv[1]
# commit_SHA = sys.argv[2]
# jobName = sys.argv[3]
# state = sys.argv[4]
# ref = sys.argv[5]
# target_url = sys.argv[6]
# description = sys.argv[7]

project_name = 'Custodian-pc'
commit_SHA = '1df9c3f4eb83ee6738949425b9bb5dc786961b21'
jobName = 'test'
state = 'success'
ref = 'develop'
target_url = ''
description = 'success'

private_token = 'Rw339e9eD6ekc7ny3Suw'
api_url = 'http://192.168.9.66/api/v4/'
headers = {'PRIVATE-TOKEN':private_token}

# getProjectID
req_url = api_url + 'projects/'
params = 'search=' + project_name
response = requests.get(url=req_url,params=params,headers=headers).json()
for project in response:
    if project['name'] == project_name:
        project_id = project['id']

# setPipelineInfo
req_url = api_url + 'projects/' + str(project_id) + '/statuses/' + commit_SHA
params = 'state=' + state + \
         '&' + 'ref=' + ref + \
         '&' + 'context=' + jobName + \
         '&' + 'target_url=' + target_url + \
         '&' + 'description=' + description

response = requests.post(url=req_url,params=params,headers=headers).json()
print(req_url)
print(response)