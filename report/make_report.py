import requests
from bs4 import BeautifulSoup
from jinja2 import FileSystemLoader, Environment
from lxml.html import etree
import os
import sys
import json
import time


def get_code_compile_result(jenkins_job_name, jenkins_buile_id):
    jenkins_build_url = 'http://192.168.18.31:8080/job/' + jenkins_job_name + '/' + jenkins_buile_id + '/consoleText/'
    response = requests.get(jenkins_build_url).content
    if response.find('程序包下载地址'.encode('utf-8')) >= 0:
        return 'PASS', '代码编译过程暂无详情'
    else:
        return 'FAIL', '代码编译过程暂无详情'


def get_code_scan_result(sonar_project_name):
    login_url = 'http://192.168.112.102:9000/api/authentication/login'
    login_headers = {
        'Accept': 'application/json',
        'Content-type': 'application/x-www-form-urlencoded'
    }
    login_data = 'login=admin&password=admin'
    login_response = requests.post(url=login_url,
                                   data=login_data,
                                   headers=login_headers)
    cookie = login_response.cookies
    status_url = 'http://192.168.112.102:9000/api/ce/component'
    status_params = 'componentKey=' + sonar_project_name
    for i in range(20):
        status_response = requests.get(url=status_url,
                                       params=status_params,
                                       cookies=cookie).json()
        run_status = status_response.get('current').get('status')
        if run_status == 'SUCCESS':
            break
        else:
            time.sleep(30)
    if run_status != 'SUCCESS':
        return 'ERROR', '获取单元测试信息失败，请求超时'
    project_url = 'http://192.168.112.102:9000/api/measures/component'
    project_params = 'componentKey=' + sonar_project_name + '&metricKeys=quality_gate_details,bugs,vulnerabilities,code_smells'
    project_response = requests.get(url=project_url,
                                    params=project_params,
                                    cookies=cookie).json()
    measures = project_response.get('component').get('measures')
    if measures:
        dict = {}
        for measure in measures:
            key = measure['metric']
            value = measure['value']
            dict[key] = value
        quality_gate = dict.get('quality_gate_details')
        status = json.loads(quality_gate)['level'] if quality_gate else ''
        bugs = dict.get('bugs') if dict.get('bugs') else ''
        vulnerabilities = dict.get('vulnerabilities') if dict.get(
            'vulnerabilities') else ''
        code_smells = dict.get('code_smells') if dict.get(
            'code_smells') else ''
        if status == 'OK':
            return 'PASS', '问题： ' + bugs + '</br>' + '漏洞： ' + vulnerabilities + '</br>' + '优化点： ' + code_smells
        else:
            return 'FAIL', '问题： ' + bugs + '</br>' + '漏洞： ' + vulnerabilities + '</br>' + '优化点： ' + code_smells
    else:
        return 'ERROR', '获取代码扫描信息失败，返回异常'


def get_unit_test_result(sonar_project_name):
    login_url = 'http://192.168.112.102:9000/api/authentication/login'
    login_headers = {
        'Accept': 'application/json',
        'Content-type': 'application/x-www-form-urlencoded'
    }
    login_data = 'login=admin&password=admin'
    login_response = requests.post(url=login_url,
                                   data=login_data,
                                   headers=login_headers)
    cookie = login_response.cookies
    status_url = 'http://192.168.112.102:9000/api/ce/component'
    status_params = 'componentKey=' + sonar_project_name
    for i in range(20):
        status_response = requests.get(url=status_url,
                                       params=status_params,
                                       cookies=cookie).json()
        run_status = status_response.get('current').get('status')
        if run_status == 'SUCCESS':
            break
        else:
            time.sleep(30)
    if run_status != 'SUCCESS':
        return 'ERROR', '获取单元测试信息失败，请求超时'
    project_url = 'http://192.168.112.102:9000/api/measures/component'
    project_params = 'componentKey=' + sonar_project_name + '&metricKeys=quality_gate_details,coverage,tests,test_failures,skipped_tests,test_execution_time'
    project_response = requests.get(url=project_url,
                                    params=project_params,
                                    cookies=cookie).json()
    measures = project_response.get('component').get('measures')
    if measures:
        dict = {}
        for i in measures:
            key = i.get('metric')
            value = i.get('value')
            dict[key] = value
        quality_gate = dict.get('quality_gate_details')
        result_status = json.loads(quality_gate).get(
            'level') if quality_gate else ''
        coverage = dict.get('coverage') if dict.get('coverage') else ''
        tests = dict.get('tests') if dict.get('tests') else ''
        test_failures = dict.get('test_failures') if dict.get(
            'test_failures') else ''
        skipped_tests = dict.get('skipped_tests') if dict.get(
            'skipped_tests') else ''
        test_execution_time = str(
            int(int(dict.get('test_execution_time')) /
                1000)) if dict.get('test_execution_time') else ''
        if result_status == 'OK':
            return 'PASS', '覆盖度(%)： ' + coverage + '</br>' + '单元测试数： ' + tests + '</br>' + '失败数： ' + test_failures + '</br>' + '忽略数： ' + skipped_tests + '</br>' + '持续时间(s)： ' + test_execution_time
        else:
            return 'FAIL', '覆盖度(%)： ' + coverage + '</br>' + '单元测试数： ' + tests + '</br>' + '失败数： ' + test_failures + '</br>' + '忽略数： ' + skipped_tests + '</br>' + '持续时间(s)： ' + test_execution_time
    else:
        return 'ERROR', '获取单元测试信息失败，返回异常'


def get_auto_deploy_result(auto_deploy_report_path):
    return 'NOTSUPPORT', '环境部署过程暂无详情'


def get_auto_test_result(auto_test_report_path):
    if (os.path.exists(auto_test_report_path)):
        file = open(auto_test_report_path, 'r', encoding='UTF-8')
        html = BeautifulSoup(file, 'html.parser')
        file.close()
        p = html.find_all('p')[1].text
        passed = html.find(attrs={'class': 'passed'}).text
        failed = html.find(attrs={'class': 'failed'}).text
        skipped = html.find(attrs={'class': 'skipped'}).text
        if int(failed[0:-7]) == 0:
            return 'PASS', '运行描述： ' + '</br>' + p + '</br>' + '--' + passed + '</br>' + '--' + failed + '</br>' + '--' + skipped
        else:
            return 'FAIL', '运行描述： ' + '</br>' + p + '</br>' + '--' + passed + '</br>' + '--' + failed + '</br>' + '--' + skipped
    else:
        return 'ERROR', '测试被人为中断或测试代码出错，未能生成报告'


def get_load_test_result(load_test_report_path):
    if (os.path.exists(load_test_report_path)):
        parser = etree.HTMLParser(encoding='utf-8')
        html = etree.parse(load_test_report_path, parser=parser)
        cbft_name = html.xpath(
            '/html/body/div/div[2]/div/table/tbody/tr[1]/td[1]/text()')[0]
        cbft_status = html.xpath(
            '/html/body/div/div[2]/div/table/tbody/tr[1]/td[2]/text()')[0]
        cbft_tps = html.xpath(
            '/html/body/div/div[2]/div/table/tbody/tr[1]/td[3]/text()')[0]
        cbft_cpu = html.xpath(
            '/html/body/div/div[2]/div/table/tbody/tr[1]/td[4]/text()')[0]
        cbft_memory = html.xpath(
            '/html/body/div/div[2]/div/table/tbody/tr[1]/td[5]/text()')[0]
        cbft_bwup = html.xpath(
            '/html/body/div/div[2]/div/table/tbody/tr[1]/td[6]/text()')[0]
        cbft_bwdown = html.xpath(
            '/html/body/div/div[2]/div/table/tbody/tr[1]/td[7]/text()')[0]
        wasm_name = html.xpath(
            '/html/body/div/div[2]/div/table/tbody/tr[3]/td[1]/text()')[0]
        wasm_status = html.xpath(
            '/html/body/div/div[2]/div/table/tbody/tr[3]/td[2]/text()')[0]
        wasm_tps = html.xpath(
            '/html/body/div/div[2]/div/table/tbody/tr[3]/td[3]/text()')[0]
        wasm_cpu = html.xpath(
            '/html/body/div/div[2]/div/table/tbody/tr[3]/td[4]/text()')[0]
        wasm_memory = html.xpath(
            '/html/body/div/div[2]/div/table/tbody/tr[3]/td[5]/text()')[0]
        wasm_bwup = html.xpath(
            '/html/body/div/div[2]/div/table/tbody/tr[3]/td[6]/text()')[0]
        wasm_bwdown = html.xpath(
            '/html/body/div/div[2]/div/table/tbody/tr[3]/td[7]/text()')[0]
        cbft = '场景：' + cbft_name + '<br>' + \
               '状态：' + cbft_status + '<br>' + \
               '每秒事务数：' + cbft_tps + '<br>' + \
               '处理器(%)：' + cbft_cpu + '<br>' + \
               '内存(%)：' + cbft_memory + '<br>' + \
               '带宽上行(Mb/s)：' + cbft_bwup + '<br>' + \
               '带宽下行(Mb/s)：' + cbft_bwdown
        wasm = '场景：' + wasm_name + '<br>' + \
               '状态：' + wasm_status + '<br>' + \
               '每秒事务数：' + wasm_tps + '<br>' + \
               '处理器(%)：' + wasm_cpu + '<br>' + \
               '内存(%)：' + wasm_memory + '<br>' + \
               '带宽上行(Mb/s)：' + wasm_bwup + '<br>' + \
               '带宽下行(Mb/s)：' + wasm_bwdown
        if cbft_status == 'success' and wasm_status == 'success':
            TestResult = 'PASS'
        else:
            TestResult = 'FAIL'
        return TestResult, cbft + '<br><br>' + wasm
    else:
        return 'ERROR', '测试被人为中断或测试代码出错，未能生成报告'


def get_stability_test_result(stability_test_report_path):
    return 'NOTSUPPORT', 'HTML报告尚未完成，详情暂不输出'


if __name__ == "__main__":
    # trigger = 'liuxing'
    # action_type = 'test'
    # build_target = 'test'
    # jenkins_job_name = 'PlatON/job/RUN'
    # jenkins_buile_id = '118'
    # sonar_project_name = 'PlatON'
    # test_type = 'all'
    trigger = sys.argv[1]
    action_type = sys.argv[2]
    build_target = sys.argv[3]
    jenkins_job_name = sys.argv[4]
    jenkins_buile_id = sys.argv[5]
    sonar_project_name = sys.argv[6]
    test_type = sys.argv[7]
    auto_deploy_report_path = './files/PlatON_auto_deploy.html'
    auto_test_report_path = './files/PlatON_auto_test.html'
    load_test_report_path = './files/performance_result.html'
    stability_test_report_path = ''
    code_compile_display = ''
    code_compile_result = ''
    code_compile_detail = ''
    code_scan_display = ''
    code_scan_result = ''
    code_scan_detail = ''
    unit_test_display = ''
    unit_test_result = ''
    unit_test_detail = ''
    auto_deploy_display = ''
    auto_deploy_result = ''
    auto_deploy_detail = ''
    auto_test_display = ''
    auto_test_result = ''
    auto_test_detail = ''
    load_Test_display = ''
    load_Test_result = ''
    load_test_detail = ''
    stability_test_display = ''
    stability_test_result = ''
    stability_test_detail = ''
    if test_type == 'all':
        code_compile_result, code_compile_detail = get_code_compile_result(
            jenkins_job_name, jenkins_buile_id)
        code_scan_result, code_scan_detail = get_code_scan_result(
            sonar_project_name)
        unit_test_result, unit_test_detail = get_unit_test_result(
            sonar_project_name)
        auto_deploy_result, auto_deploy_detail = get_auto_deploy_result(
            auto_deploy_report_path)
        auto_test_result, auto_test_detail = get_auto_test_result(
            auto_test_report_path)
        # load_Test_result, load_test_detail = get_load_test_result(load_test_report_path)
        # stability_test_result, stability_test_detail = get_stability_test_result(stability_test_report_path)
        load_Test_display = 'hiddenRow'
        stability_test_display = 'hiddenRow'
    elif test_type == 'baseline':
        code_compile_result, code_compile_detail = get_code_compile_result(
            jenkins_job_name, jenkins_buile_id)
        auto_deploy_result, auto_deploy_detail = get_auto_deploy_result(
            auto_deploy_report_path)
        auto_test_result, auto_test_detail = get_auto_test_result(
            auto_test_report_path)
        code_scan_display = 'hiddenRow'
        unit_test_display = 'hiddenRow'
        load_Test_display = 'hiddenRow'
        stability_test_display = 'hiddenRow'
    elif test_type == 'none':
        code_compile_result, code_compile_detail = get_code_compile_result(
            jenkins_job_name, jenkins_buile_id)
        code_scan_display = 'hiddenRow'
        unit_test_display = 'hiddenRow'
        auto_deploy_display = 'hiddenRow'
        auto_test_display = 'hiddenRow'
        load_Test_display = 'hiddenRow'
        stability_test_display = 'hiddenRow'
    else:
        raise Exception
    dict = {}
    dict['trigger'] = trigger
    dict['action_type'] = action_type
    dict['build_target'] = build_target
    dict['test_type'] = test_type
    dict['code_compile_display'] = code_compile_display
    dict['code_compile_result'] = code_compile_result
    dict['code_compile_detail'] = code_compile_detail
    dict['code_scan_display'] = code_scan_display
    dict['code_scan_result'] = code_scan_result
    dict['code_scan_detail'] = code_scan_detail
    dict['unit_test_display'] = unit_test_display
    dict['unit_test_result'] = unit_test_result
    dict['unit_test_detail'] = unit_test_detail
    dict['auto_deploy_display'] = auto_deploy_display
    dict['auto_deploy_result'] = auto_deploy_result
    dict['auto_deploy_detail'] = auto_deploy_detail
    dict['auto_test_display'] = auto_test_display
    dict['auto_test_result'] = auto_test_result
    dict['auto_test_detail'] = auto_test_detail
    dict['load_Test_display'] = load_Test_display
    dict['load_Test_result'] = load_Test_result
    dict['load_test_detail'] = load_test_detail
    dict['stability_test_display'] = stability_test_display
    dict['stability_test_result'] = stability_test_result
    dict['stability_test_detail'] = stability_test_detail
    tpl_path = './report_template.html'
    report_path = './files/jenkins_ci_report.html'
    env = Environment(loader=FileSystemLoader(os.path.dirname(tpl_path)))
    tpl = env.get_template(os.path.basename(tpl_path))
    if os.path.exists(os.path.dirname(report_path)) is False:
        os.makedirs(os.path.dirname(report_path))
    with open(report_path, 'w+', encoding='UTF-8') as file:
        render_content = tpl.render(dict)
        file.write(render_content)
        file.close()
