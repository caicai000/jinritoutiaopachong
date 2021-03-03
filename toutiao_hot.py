# /usr/bin

# Author ： LIANGZHUOWEI
# Time : 2021/2/21 0021 22:26
# Describe ：
import requests
import execjs
from retrying import retry
import time
import sqlite3
import sys
import datetime
sys.setrecursionlimit(1000000)

def get_ip():
    # 目标网址
    target_url = "http://getip.beikeruanjian.com/getip/?user_id=20210221162857377668&token=g28WRS1B30b5FGCx&server_id=8794&num=1&protocol=1&format=json&jsonipport=1&jsonexpiretime=1&jsoncity=1&jsonisp=1&dr=0&province=1&city=1&citycode="
    response = requests.get(target_url)

    # 代理设置
    proxies = {
        "http": "http://" + response.json()["data"][0]['ipport'],
        "https": "http://" + response.json()["data"][0]['ipport']
    }
    print(proxies)
    time.sleep(12)
    return proxies

headers = {
    'user-agent':"Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.182 Safari/537.36",
}

with open('./signature.js', 'r') as f:
    js_code = f.read()

def get_ttscid():
    '''
    获取到tt_scid
    :return:
    '''
    resp = requests.get('https://xxbg.snssdk.com/websdk/v1/getInfo?q=3T0OfHdkf15dHX2XPmrz7pTbonbnvttvmtW2wY6hqtH4Plj0IM%2FSiKbwlTU8IlR6zq2S7sdE8C66WYVhj%2BfZ0XkbM0r527bx6hRe6BBX%2BwGPInWpIghqolf%2BnKAxjVaen0mx0%2Bh7fjrvX3iYYBNvAQuEH%2FXfqgM05n1k0S1JwUxNB5PRwbS6X3ksPKc2Xvayihl7esPgPbqYZbngkvoalTtHoixkAjbFMLABmPM5nvyewZYoVUUMm84smUKYwGJ8xG%2BelygbpUDMmTnXT8hCj1%2BbEgi24tPWrn%2Fothitd93oVFgFUONbyp6gxVS%2BmVL4K56vHhvS28Ov0AXP%2FAIcRArmgD07NX1pvQF4O2CFRdb4YrTimzUidRFnbgXgb7Siutl658dPuUGd87zjNyNBlV58VZknOyuLK%2BT6RwkyB%2FlBk8ltID%2BfLx3zeMUkBfXxfiIfmHxkBKejkK9vqZIYDLC2ljFpq3%2FEN1cREXaci5aAPxXoMCO7V1CrQkMRK2Ok9UdYjlscI3Z%2Bb419r8f3tUgrrHU6hlQ2VsDlVEB1xVj3tReUhOHNeJBkNV6zaJKJ9jh23G%2Bs8uHkr54xKsZQ%2FEsPVB6s5ZmkAZwmK13jy05x5xNTUTW%2BMXQyTAfCoRhexWeL9INqVRid5j3%2BpS%2FRIAxlIFOSeoOi31g4Ee6lLfLkzihItK%2B6P%2F52PCK7Rh8yYnA0qXF0OqS4fJtU2ctxdjOs8UPlwfjKW2WHZjT3jvS2epkQ8l9DGQlETOZzIkBXm6y%2FV%2BnVpliFyUTE4d3%2F8G786eBcU7bFSTM62QNFJMkbLOAbKsOmmMorP5X69HeU9wT62c3rPU4APReCOb68knzSqE3jrVOdnBQHU4FxL1Pt6vTz9cPyUzLZ8TWx3HFnjUHjK5ofPTtgjQrb0JClXen2ZFZpHyVPnBu%2Fv5y1TSl%2BqYU2DTtzeqE62K97TRgpJ5AhBJGjjhQY7d%2BSpKJBuoFVtYitJzrf6y5LV9aJygst35T0TpdntiCGMSaeKB6L6PFOSeHorUkUBwIpDefmhr2rBkiqdjLDUZkgxSuPXNbFMTha6qrFT%2FQf%2FelXbkpJttes2UJmM5MngCGl6uGF%2FZbcVQzld71%2FAsYQ%2BS7F5KECJ1Kk4CgP642N8NUN%2F4RG0489%2F3fx03ii0IKG030oRNvo23WV896V&callback=_9685_{}'.format(int(time.time()*1000)),headers = headers)
    return resp.cookies.get_dict()

@retry(stop_max_attempt_number=3, wait_fixed=3000)
def get_page(cookies,url,min_behot_time=0):
    '''
    获取列表页数据
    :return:
    '''
    scid = get_ttscid()
    tt_scid = 'tt_scid=' + scid['tt_scid']
    ctx = execjs.compile(js_code).call('get_page',url,tt_scid)
    params = {
        'min_behot_time': min_behot_time,
        'category': '__all__',
        'utm_source': 'toutiao',
        'widen': '1',
        'tadrequire': 'true',
        "_signature":ctx
    }
    cookies.update({'_signature':ctx,'tt_scid':scid['tt_scid'],'ttcid':scid['ttcid']})
    resp = requests.get(url=url,headers=headers,params=params,cookies = cookies,proxies = get_ip())
    time.sleep(12)
    result = resp.json()
    next_page = result['next']['max_behot_time']
    print(resp.json())

    datalist = resp.json()

    dppath = "news.db"

    saveData2DB(datalist, dppath)

    print(datetime.datetime.now())

    get_page(cookies=cookies,url = url,min_behot_time=next_page)

    #return resp.json()

def init_db(dbpath):
    sql = '''
        create table news
        (
        id integer primary key  autoincrement,
        chinese_tag varchar ,
        title varchar ,
        source_url text,
        middle_image text

        )

    '''  # 创建数据表
    conn = sqlite3.connect(dbpath)
    cursor = conn.cursor()
    cursor.execute(sql)
    conn.commit()
    conn.close()


def saveData2DB(datalist, dppath):
    try:
        init_db(dppath)
    except sqlite3.OperationalError:
        print("table news already exists")

    conn = sqlite3.connect(dppath)
    cur = conn.cursor()

    for data in datalist["data"]:
        if 'ad_label' in data:
            continue
        c = "https://www.toutiao.com" + data['source_url']

        try:
            if 'middle_image' in data:
                d = data['middle_image']
            else:
                d = " "
            if 'chinese_tag' in data:
                a = data['chinese_tag']
            else:
                a = " "
            if 'title' in data:
                b = data['title']
            else:
                b = " "
            str = "'%s','%s','%s','%s'" % (a, b, c, d)
            sql1 = "select * from news where source_url = '%s'" % c
            print(sql1)
            data = cur.execute(sql1)
            text = ""
            for item in data:
                # print(item)
                text = item
            print(text)
            if text == "":
                sql2 = '''
                                insert into news(
                                chinese_tag,title, source_url, middle_image
                                ) VALUES(%s)''' % str
                print(sql2)
                cur.execute(sql2)
                conn.commit()
            else:
                continue
        except :
            print("错误")
            continue
    cur.close()
    conn.close()


def main(url):
    resp = requests.get('https://www.toutiao.com/', headers=headers)

    cookies = resp.cookies.get_dict()
    get_page(cookies=cookies,url=url)




if __name__ == '__main__':

    main(url = 'https://www.toutiao.com/toutiao/api/pc/feed/')

    #print(get_ip())
