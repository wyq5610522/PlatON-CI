#!/usr/bin/python3.5
# -*- coding: UTF-8 -*-
import json
import requests
import socket

net = '192.168.18.31'
# local = '127.0.0.1'
host = net
port = 18080
# url = 'http://192.168.18.31:8080/job/PlatON/job/RUN/buildWithParameters'
url = 'http://192.168.18.31:8080/job/Testing/job/Test_Github/buildWithParameters'
token = '1165670d92241176b11f64f05335843b3b'

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server.bind((host, port))
server.listen(5)

while True:
    sock, addr = server.accept()
    byte = sock.recv(40960)
    str = bytes.decode(byte)
    list = str.split('\r\n')
    dict = {}
    dict['method'] = list[0].split(' / ')[0]
    if dict['method'] == 'POST':
        dict['protocol'] = list[0].split(' / ')[1]
        for param in list[1:-1]:
            if param.find(': ') != -1:
                key = param.split(': ')[0]
                value = param.split(': ')[1]
                dict[key] = value
        data_all = list[-1]
        data_len = int(dict['Content-Length'])
        while len(data_all) < data_len:
            data = bytes.decode(sock.recv(40960))
            data_all = data_all + data
        dict['data'] = data_all
        content = b'HTTP/1.1 200 ok\r\nContent-Type: text/html\r\n\r\n'
        sock.sendall(content)
        print('POST Response: 200')

        if dict['X-GitHub-Event'] == 'pull_request':
            print('GitHub Event Is Pull Request')
            data_json = json.loads(dict['data'])
            project_owner = data_json['pull_request']['head']['repo']['owner'][
                'login']
            project_name = data_json['pull_request']['head']['repo']['name']
            project_url = 'https://github.com/' + project_owner + '/' + project_name
            trigger = data_json['pull_request']['head']['user']['login']
            trigger_type = 'Pull Request'
            source_branch = data_json['pull_request']['head']['ref']
            target_branch = data_json['pull_request']['base']['ref']
            build_branch = source_branch
            commit_SHA = data_json['pull_request']['head']['sha']
            submit_title = 'Test_title'
            submit_detail = 'Test_detail'
            print('project_url:', project_url)
            print('project_name:', project_name)
            print('project_owner:', project_owner)
            print('trigger:', trigger)
            print('trigger_type:', trigger_type)
            print('source_branch:', source_branch)
            print('target_branch:', target_branch)
            print('build_branch:', build_branch)
            print('submit_title:', submit_title)
            print('submit_detail:', submit_detail)
            file = open('jenkins_cache', 'w+', encoding='UTF-8')
            file.write('project_url=' + project_url + '\n' + 'trigger=' +
                       trigger + '\n' + 'trigger_type=' + trigger_type + '\n' +
                       'source_branch=' + source_branch + '\n' +
                       'target_branch=' + target_branch + '\n' +
                       'branch_name=' + build_branch + '\n' + 'commit_SHA=' +
                       commit_SHA + '\n' + 'submit_title=' + submit_title +
                       '\n' + 'submit_detail=' + submit_detail)
            file.close()
            params = ('&token=' + token + '&build_platform=' + 'all' +
                      '&build_target=' + build_branch + '&build_mode=' +
                      'make all' + '&build_version' + '0.7' + '&build_tests' +
                      'none' + '&build_packs' + 'false' + '&build_gitscm' + 'github')
            response = requests.get(url=url, params=params)
            print('Jenkins Response:', response)

        elif dict['X-GitHub-Event'] == 'push':
            print('GitHub Event Is Push')
            data_json = json.loads(dict['data'])
            project_owner = data_json['repository']['owner']['name']
            project_name = data_json['repository']['name']
            project_url = 'https://github.com/' + project_owner + '/' + project_name
            trigger = data_json['pusher']['name']
            trigger_type = 'Push'
            source_branch = data_json['ref'].split('/')[-1]
            target_branch = source_branch
            build_branch = target_branch
            commit_SHA = data_json['head_commit']['id']
            submit_title = 'Test_title'
            submit_detail = 'Test_detail'
            print('project_url:', project_url)
            print('project_name:', project_name)
            print('project_owner:', project_owner)
            print('trigger:', trigger)
            print('trigger_type:', trigger_type)
            print('source_branch:', source_branch)
            print('target_branch:', target_branch)
            print('build_branch:', build_branch)
            print('submit_title:', submit_title)
            print('submit_detail:', submit_detail)
            file = open('jenkins_cache', 'w+', encoding='UTF-8')
            file.write('project_url=' + project_url + '\n' + 'trigger=' +
                       trigger + '\n' + 'trigger_type=' + trigger_type + '\n' +
                       'source_branch=' + source_branch + '\n' +
                       'target_branch=' + target_branch + '\n' +
                       'branch_name=' + build_branch + '\n' + 'commit_SHA=' +
                       commit_SHA + '\n' + 'submit_title=' + submit_title +
                       '\n' + 'submit_detail=' + submit_detail)
            file.close()
            params = ('&token=' + token + '&build_platform=' + 'all' +
                      '&build_target=' + build_branch + '&build_mode=' +
                      'make all' + '&build_version' + '0.7' + '&build_tests' +
                      'none' + '&build_packs' + 'false' + '&build_gitscm' + 'github')
            response = requests.get(url=url, params=params)
            print('Jenkins Response:', response)

    elif dict['method'] == 'GET':
        content = b'HTTP/1.1 200 ok\r\nContent-Type: text/html\r\n\r\n'
        sock.sendall(content)
        print('GET Response: 200')
    else:
        content = b'HTTP/1.1 404 Not Found\r\nContent-Type: text/html\r\n\r\n'
        sock.sendall(content)
        print('Unknow Response: 404')
    sock.close()