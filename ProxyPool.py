#! /usr/bin/env python
# -*- coding: utf-8 -*-

import requests
import random
import time
from bs4 import BeautifulSoup

header = {'User-Agent':'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/31.0.1650.63 Safari/537.36'}


class GatherProxy(object):
    url = 'http://www.xicidaili.com/nn/'

    def getelite(self, pages=1):
        # Get Elite Anomy proxy
        # Pages define how many pages to get
        # Uptime define the uptime(L/D)
        # fast define only use fast proxy with short reponse time
        proxies = set()
        for i in range(1, pages+1):
            url_link = self.url + str(i)
            print url_link
            r = requests.get(url_link, headers=header)
            if r.status_code == 200:
                soup = BeautifulSoup(r.text, "html.parser")
                table = soup.find("table", {"id": "ip_list"})

                tr_count_for_this_page = 0
                for tr in table.find_all('tr'):
                    # 过滤表头
                    if tr_count_for_this_page == 0:
                        tr_count_for_this_page = 1
                        continue

                    td = tr.find_all('td')
                    if td[6].find(attrs={'class': 'fast'}):  # find_all(attrs={'class': 'olt'})[0]
                        if td[5].text == 'HTTPS':
                            proxies.add(td[1].text + ':' + td[2].text)

            else:
                print 'request url error %s -status code: %s:' % (url_link, r.status_code)
            # sleep for a while
            time.sleep(1)
        return proxies


class ProxyPool(object):
    # A proxypool class to obtain proxy
    gatherproxy = GatherProxy()

    def __init__(self):
        self.pool=set()

    def updateGatherProxy(self, pages=1):
        # Use GatherProxy to update proxy pool
        self.pool.update(self.gatherproxy.getelite(pages=pages))

    def removeproxy(self,proxy):
        # Remove a proxy from pool
        if proxy in self.pool:
            self.pool.remove(proxy)

    def randomchoose(self):
        # Random Get a proxy from pool
        if self.pool:
            return random.sample(self.pool, 1)[0]
        else:
            self.updateGatherProxy()
            return random.sample(self.pool, 1)[0]

    def getproxy(self):
        # Get a dict format proxy randomly
        proxy = self.randomchoose()
        proxies = {'http': 'http://'+proxy, 'https': 'https://'+proxy}
        # proxies = {'https': 'https://'+proxy}
        # r=requests.get('http://icanhazip.com',proxies=proxies,timeout=1)
        try:
            r = requests.get('http://dx.doi.org', proxies=proxies, timeout=1)
            if r.status_code == 200:
                print 'User Proxy:', proxies
                return proxies
            else:
                self.removeproxy(proxy)
                return self.getproxy()
        except:
            self.removeproxy(proxy)
            return self.getproxy()
