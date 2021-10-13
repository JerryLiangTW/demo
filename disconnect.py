import json
import requests
import cryptocode
import pprint
from requests.api import request
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

def disconnect(mac):
    # 使用config新增登入資訊
    login = open('config.txt','r')
    config_login = login.read()
    config_login_dic = eval(config_login)
    username = "jerryapi"

    ip = config_login_dic[username][0]
    client_id = config_login_dic[username][1]
    passwordencode = config_login_dic[username][2]
    password = cryptocode.decrypt(passwordencode,'netease')

    # 登入
    url = "https://{}/api/".format(ip)
    payload = {
        "grant_type": "password",
        "client_id": client_id,
        "username": username,
        "password": password
    }
    headers = {
        "Accept": "application/json",
        "Authorization": "Bearer <TOKEN>",
        "Content-Type": "application/json"
    }

    response = requests.request("POST", url + 'oauth', json=payload, headers=headers, verify=False, timeout=10)
    response = response.json()
    #print(response)
    token = response['access_token']
    #print(token)

    #踢除
    querystring = {"async":"true"}
    payload = {"filter": {"mac_address": "{}".format(mac)}}
    headers = {
        "Accept": "application/json",
        "Authorization": "Bearer " + token,
        "Content-Type": "application/json"
    }

    result = requests.request("POST", url + 'session-action/disconnect/mac/{}'.format(mac),json=payload, headers=headers, params=querystring, verify=False, timeout=10)
    result_json = result.json()
    #pprint.pprint(result_json)