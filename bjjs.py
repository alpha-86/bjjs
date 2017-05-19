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

def getListHtmlContent(page_id=307670,page_no=1):
    print('now for page:',page_id,'-',page_no,'\n')
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
    params['currentPage'] = str(page_no)
    page_id=str(page_id)
    url='http://www.bjjs.gov.cn/eportal/ui?pageId='+page_id+'&isTrue=1'
    data = doPostRequest2(url,params)
    data = urllib.parse.quote_from_bytes(data)
    data = urllib.parse.unquote(data)
    return data

def getDetailHtmlContent(url):
    url = 'http://www.bjjs.gov.cn'+url
    data = doRequest2(url)
    data = urllib.parse.quote_from_bytes(data)
    data = urllib.parse.unquote(data)
    return data

def getDataList(page_id,title,page_no,is_need_num=False):
    html = getListHtmlContent(page_id,page_no)
    parser=ListPageParser()
    parser.setTableTitle(title)
    parser.feed(html)
    parser.close()
    data_list = parser.getAllData()
    if is_need_num:
        p='总记录数:(\d+)([^\d]+)每页显示(\d+)'
        m = re.search(p,html)
        total = int(m.groups()[0])
        step = int(m.groups()[2])
        return (data_list,total,step)
    return data_list

def getDetailInfo(url):
    html = getDetailHtmlContent(url)
    parser = DetailPageParser()
    parser.feed(html)
    parser.close()
    detail_info = parser.getDetailInfo()
    return detail_info
    
def getZhuzhaiList(page_idx=1):
    zhuzhai_pageid=307670
    table_title='预售商品房住宅项目公示'

    ret_tuple = getDataList(zhuzhai_pageid,table_title,1,True)
    zhuzhai_list = ret_tuple[0]
    total_num = ret_tuple[1]
    step = ret_tuple[2]
    pages = int(total_num/step)+3
    if page_idx > 1:
        pages=min(page_idx+1,pages)
    else:
        pages=1
    for i in range(2,pages):
        zhuzhai_list = zhuzhai_list+getDataList(zhuzhai_pageid,table_title,i)
    return zhuzhai_list

class  ListPageParser(html.parser.HTMLParser):
        is_span = 0
        is_data_next = 0
        is_in_table = 0
        is_in_tr = 0
        data_row = []
        data_all = []
        is_skip_title = 0
        is_in_tr = 0
        tag_idx = ''
        table_title=''

        def setTableTitle(self,title):
            self.table_title = title

        def getAllData(self):
            return self.data_all

        def doSpanStatus(self,tag,is_endtag=0):
            if tag == 'span' and is_endtag == 0:
                self.is_span = 1
            if tag == 'span' and is_endtag == 1:
                self.is_span = 0

        def doDataNextStatus(self,data):
            if self.is_span != 1:
                return
            if self.is_data_next == 1:
                return
            data = data.strip()
            if data == self.table_title:
                self.is_data_next = 1

        def doDataTableStatus(self,tag,is_endtag=0):
            if tag != 'table' \
                or self.is_data_next == 0:
                return
            if is_endtag == 0 :
                self.is_in_table = 1
            if is_endtag == 1 :
                self.is_in_table = 0
                self.is_data_next = 0

        def transRowToDick(self,data_row):
            ret = {}
            ret['url'] = data_row[0]
            ret['name'] = data_row[1]
            ret['license'] = data_row[3]
            ret['date'] = data_row[4]
            str = data_row[0]
            ret['project_id'] = str[str.find('projectID=')+len('projectID='):str.find('&systemID')]
            return ret

        def doEachTrStatus(self,tag,is_endtag=0):
            if tag != 'tr' \
                or self.is_in_table == 0:
                return
            if self.is_skip_title == 0 and is_endtag == 0:
                return
            if self.is_skip_title == 0 \
                and is_endtag == 1:
                self.is_skip_title = 1
                return
            if is_endtag == 0:
                self.is_in_tr = 1
            if is_endtag == 1:
                self.is_in_tr = 0
                self.data_all.append(self.transRowToDick(self.data_row));
                self.data_row = [];
        
        def parseEachTr(self,tag,attrs):
            if self.is_in_tr == 0:
                return

            if type(attrs) is not type([]):
                return
            attr_key=attrs[0][0]
            attr_value=attrs[0][1]
            if attr_key == 'href':
                attr_value=attr_value.strip()
                self.data_row.append(attr_value)

        def doTdData(self,data):
            if self.is_in_tr == 0:
                return
            data = data.strip()
            if data == '':
                return
            self.data_row.append(data)


        def handle_starttag(self, tag, attrs):
            self.tag_idx=tag
            self.doSpanStatus(tag)
            self.doDataTableStatus(tag)
            self.doEachTrStatus(tag)
            self.parseEachTr(tag,attrs)


        def handle_endtag(self, tag):
            self.doSpanStatus(tag,1)
            self.doDataTableStatus(tag,1)
            self.doEachTrStatus(tag,1)

        def handle_data(self, data):
            self.doDataNextStatus(data)
            self.doTdData(data)

class  DetailPageParser(html.parser.HTMLParser):
    is_in_table = False
    key_name = False
    detail_info = dict()

    def getDetailInfo(self):
        return self.detail_info

    def isInTable(self,tag,attrs):
        if tag != 'tr' \
            or len(attrs) < 1 \
            or self.is_in_table == True:
            return
        attr_key=attrs[0][0]
        attr_value=attrs[0][1]
        if attr_key == 'class' and attr_value=='预售项目信息':
            self.is_in_table = True

    def closeTable(self,tag):
        if self.is_in_table == True \
            and tag=='table':
            self.is_in_table = False

    def getKeyName(self,tag,attrs):
        if self.is_in_table == False \
            or tag != 'td':
            return
        if type(attrs) != type([]) \
            or len(attrs) < 1:
            return
        attr_key=attrs[0][0]
        attr_value=attrs[0][1]
        if attr_key == 'id':
            self.key_name = attr_value.strip()

    def getKeyValue(self,data):
        if self.key_name == False:
            return
        key_value = data.strip()
        self.detail_info[self.key_name] = key_value
        self.key_name = False

    def handle_starttag(self, tag, attrs):
        self.isInTable(tag,attrs)
        self.getKeyName(tag,attrs)


    def handle_endtag(self, tag):
        self.closeTable(tag)


    def handle_data(self, data):
        self.getKeyValue(data)

#data = getZhuzhaiList(1)
#print(data)

data = getDetailInfo('/eportal/ui?pageId=320794&projectID=5484207&systemID=2&srcId=1')
print(data)

#print(data)
#p=MyParser()
#p.feed(data)
#p.close()
