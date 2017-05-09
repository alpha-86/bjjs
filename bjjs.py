import urllib.parse
import urllib.request
import socket
import time
import json
import sys
import html.parser
import re

def addHeaders(req):
    headers = {
        'Cookie':"""JSESSIONID=6ED7995353C0D602205E1A7157E68AFA; _gscu_1677760547=89111656ippkyu10; _gscs_1677760547=92418157nvgirz70|pv:4; _gscbrs_1677760547=1; Hm_lvt_9ac0f18d7ef56c69aaf41ca783fcb10c=1492418158; Hm_lpvt_9ac0f18d7ef56c69aaf41ca783fcb10c=1492418174""",
        'Host':"www.bjjs.gov.cn",
        'Origin':"http://www.bjjs.gov.cn",
        'Referer':"http://www.bjjs.gov.cn/eportal/ui?pageId=307674&isTrue=1",
        'Upgrade-Insecure-Requests':"1",
        'User-Agent':"""Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.133 Safari/537""",
    }
    for i,j in headers.items():
        req.add_header(i,j)
    return req

def doPostRequest2(url,params):
    params = urllib.parse.urlencode(params)
    params = params.encode(encoding='UTF8')
    req = urllib.request.Request(url,params)
    req = addHeaders(req)
    response = urllib.request.urlopen(req)
    data = response.read()
    return data

def doRequest2(url):
    req = urllib.request.Request(url)
    req = addHeaders(req)
    response = urllib.request.urlopen(req)
    data = response.read()
    return data

def getList():
    params = {
        "isTrue":"0",
        "projectName":"项目名称关键字",
        "rblFWType":"q",
        "txtYS":"",
        "txtZH":"",
        "txtCQZH":"证号关键字",
        "developer":"单位名称关键字",
        "txtaddress":"地址关键字",
        "isTrue":"1",
        "ddlQX":"-1",
        "rblFWType1":"q",
        "ddlYT":"1",
        "ddlFW":"-1",
        "ddlQW":"-1",
        "ddlQY":"-1",
        "ddlHX":"-1",
        "ddlJJ":"-1",
        "currentPage":"1",
        "pageSize":"15"
    }
    data = doPostRequest2('http://www.bjjs.gov.cn/eportal/ui?pageId=307674&isTrue=1',params)
    return data

class  MyParser(html.parser.HTMLParser):
        is_span = 0

        def  handle_starttag(self, tag, attrs):
            if tag == 'span':
                self.is_span=True

        def handle_data(self, data):
            if self.is_span == True:
                print(data)



data = getList()
data = urllib.parse.quote_from_bytes(data)
data = urllib.parse.unquote(data)
print(data)
p = "总记录数:(\d+).*每页显示(\d+)"
p = p.encode(encoding='utf-8')
p = str(p)
m = re.match(p,data)
print(m)
print(m.group())
#print(data)
#p=MyParser()
#p.feed(data)
#p.close()
