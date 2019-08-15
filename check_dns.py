#!/usr/bin/env python
#encoding:utf8

# pip install dnspython IPy

import json
import requests
from IPy import IP
import dns.resolver

def send_to_rebot(context):
    '''
    发送消息
    :param context: 消息内容
    :return: 如果解析成功则返回IP, 解析失败则返回False
    '''
    ddurl = 'https://oapi.dingtalk.com/robot/send?access_token=xxx'  #钉钉群机器人webhook
    data = json.dumps({"actionCard": {
        "title": "苹果域名解析异常",
        "text": context,
        "hideAvatar": "0",
        "btnOrientation": "0",
        "btns": [
            {
                "title": "通知消息",
                "actionURL": "http://ops.hupu.io/domain/"
            }
        ]
    },
        "msgtype": "actionCard"
    })
    header = {'Content-Type': 'application/json; charset=utf-8'}
    requests.post(ddurl, data=data, headers=header)

def GetArecordIp(domain_name):
    '''
     域名解析主机A记录
    :param domain_name: 输入要要解析的域名,例: www.qq.com
    :return: 如果解析成功则返回IP, 解析失败则返回False
    '''
    address = []
    try:
        host_a = dns.resolver.query(domain_name, 'A')
        for i in host_a.response.answer:
            for j in i:
                j = str(j)
                try:
                    IP(j)
                    address.append(str(j))
                except Exception as e:
                    pass
        return True, dict(domain=domain_name, address=address)
    except:
        return False, dict(domain=domain_name)

if __name__ == '__main__':
    domin_list = ['buy.itunes.apple.com', 'sandbox.itunes.apple.com']
    ips_list = ['17.154.66.0/24', '17.154.67.0/24']
    # 设置重试次数
    num = 3
    # 解析出IP列表
    for domain in domin_list:
        for i in range(num):
            code, result = GetArecordIp(domain)
            if code:
                break
        else:
            mes = u'### 苹果支付域名解析异常通知: \n\n 域名: {0} \n\n 描述: 域名解析失败(重试{1}次) \n\n 监控节点: Hostname \n\n'.format(result.get('domain'), num)
            send_to_rebot(mes)
        # 验证解析IP是否在阿里路由列表
        for resolv_ip in result.get('address'):
            for ip in ips_list:
                if resolv_ip in IP(ip):
                    break
            else:
                mes = u'### 苹果支付域名解析异常通知: \n\n 域名: {0} \n\n 解析IP: {1} \n\n 监控节点: Hostname \n\n'.format(result.get('domain'), resolv_ip)
                send_to_rebot(mes)