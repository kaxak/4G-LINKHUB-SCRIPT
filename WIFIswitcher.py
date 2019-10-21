#!/usr/bin/python
# -*- coding:utf-8 -*-

import json
import requests
import time

class LinkHUB:
    def __init__(self, _ip):
        self.ip = _ip
        self.URL = 'http://{}/jrd/webapi'.format(_ip)
        self.session = requests.Session()
        self.token = None

    def Headers(self):
        headers = {}
        headers['_TclRequestVerificationKey'] = 'KSDHSDFOGQ5WERYTUIQWERTYUISDFG1HJZXCVCXBN2GDSMNDHKVKFsVBNf'
        if self.token:
            headers['_TclRequestVerificationToken'] = self.token
        headers['Content-type'] = 'application/json;charset=utf-8'
        headers['DNT'] = '1'
        headers['Host'] = self.ip
        headers['Referer'] = 'http://{}/index.html'.format(self.ip)
        headers['X-Requested-With'] = 'XMLHttpRequest'

        return headers

    def Encrypt(self, _str):
        if not isinstance(_str, str):
            _str = str(_str)

        key = 'e5dl12XYVggihggafXWf0f2YSf2Xngd1'
        n = {}
        encodedToken = ''
        
        i = 0
        while i < len(_str):
            code = ord(_str[i])
            code_t = ord(key[i % len(key)])

            n[2 * i] = 240 & code_t | 15 & code ^ 15 & code_t
            n[2 * i + 1] = 240 & code_t | code >> 4 ^ 15 & code_t

            i += 1

        for k, num in n.items():
            encodedToken += chr(num)

        return encodedToken
        

    def xhrPostMethod(self, _method, _params=''):
        try:
            r = self.session.post(
                self.URL,
                data='{"id":"12","jsonrpc":"2.0","method":"' + _method + '","params":{' + _params + '}}',
                headers=self.Headers(),
                timeout=20
            )
            if r.status_code == 200:
                rJSON = json.loads(r.text)
                return rJSON
            else :
                print('[Error]', 'http-{}'.format(r.status_code))
      
        except json.JSONDecodeError(msg, doc, pos):
            print('[Error]', msg)
        except Exception as err:
            print('[Error]', 'method {} fail'.format(_method))
        return None

    def xhrLogin(self, _pass):
        rJSON = self.xhrPostMethod('Login', '"Password":"{}","UserName":"{}"'.format(self.Encrypt(_pass), self.Encrypt('admin')))
        if 'error' in rJSON:
            print('[Error]', rJSON['error']['message'])
            return False
        else:
            print('Logged in!')
            self.token = self.Encrypt(rJSON['result']['token'])
            return rJSON

    def xhrSetWlanSettings(self, _apStatus, _ssid, _wpaKey):
        if isinstance(_apStatus, str):
            _apStatus = int(_apStatus)
        _apStatus = min(max(_apStatus, 0), 1)
        _apStatus = str(_apStatus)
        params = \
                '"show2GPassword":false,"show5GPassword":false,"showAP2G_guestPassword":false,"WiFiOffTime":0,\
                "AP2G":{\
                    "CountryCode":"US","ApStatus":'+_apStatus+',"WMode":3,"Ssid":"'+_ssid+'","SsidHidden":0,"Channel":9,"SecurityMode":4,"WepType":0,"WpaType":2,"WepKey":"","WpaKey":"'+_wpaKey+'","ApIsolation":0,"max_numsta":32,"curr_num":0,"CurChannel":9,"Bandwidth":0\
                },\
                "AP2G_guest":{\
                    "ApStatus":0,"WMode":3,"CountryCode":"CN","Ssid":"","SsidHidden":0,"Channel":0,"SecurityMode":3,"WepType":0,"WepKey":"1234567890","WpaType":1,"WpaKey":"GE747TNT","ApIsolation":0,"max_numsta":15,"curr_num":0,"CurChannel":8,"Bandwidth":0\
                },\
                "AP5G":{\
                    "WlanAPID":1,"ApStatus":0,"WMode":4,"Ssid":"","SsidHidden":0,"Channel":0,"SecurityMode":4,"WepType":1,"WepKey":"12345678","WpaType":1,"WpaKey":"1234567890","CountryCode":"CN","ApIsolation":0,"max_numsta":15,"curr_num":0\
                }'
        
        return self.xhrPostMethod('SetWlanSettings', params)

    def xhrGetWlanSettings(self):
        return self.xhrPostMethod('GetWlanSettings')

    def xhrGetSimStatus(self):
        return self.xhrPostMethod('GetSimStatus')

    def xhrGetSystemStatus(self):
        return self.xhrPostMethod('GetSystemStatus')

    def PrintWifiStatus(self):
        response = self.xhrGetSystemStatus()
        if response:
            if response["result"]["WlanState"] == 0:
                wifiStatus = 'Off'
            else:
                wifiStatus = 'On'
            print('Wi-Fi', wifiStatus)

    def GetWifiStatus(self):
        rJSON = self.xhrGetSystemStatus()
        if rJSON:
            return int(rJSON["result"]["WlanState"])


lh = LinkHUB('192.168.1.1')# Linkhub ip
lh.PrintWifiStatus()
print('Login...')
if lh.xhrLogin('yourPassword'):
    wifiStatus = lh.GetWifiStatus()
    if wifiStatus == 0:
        print('Try to turn ON')
        lh.xhrSetWlanSettings(1, 'your SSID', 'your WPA passphrase')
    elif wifiStatus == 1:
        print('Try to turn OFF')
        lh.xhrSetWlanSettings(0, 'your SSID', 'your WPA passphrase')
    print('Wait a second...')
    time.sleep(1)
    lh.PrintWifiStatus()
    time.sleep(2)
 


