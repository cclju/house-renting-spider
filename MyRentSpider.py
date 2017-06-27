#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sqlite3
import sys
import time
import os

import requests
from bs4 import BeautifulSoup
import re

import Utils
import Config
import ProxyPool


class Main(object):
    def __init__(self, config):
        self.config = config
        self.douban_headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/43.0.2357.81 Safari/537.36'
            # 'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            # 'Accept-Encoding': 'gzip, deflate, sdch',
            # 'Accept-Language': 'zh-CN,zh;q=0.8,en-US;q=0.6,en;q=0.4,en-GB;q=0.2,zh-TW;q=0.2',
            # 'Connection': 'keep-alive',
            # 'DNT': '1',
            # 'HOST': 'www.douban.com',
            # 'Cookie': self.config.douban_cookie
        }
        self.douban_cookie = {}
        self.login_retry = 1

    def login(self):
        url_login = 'https://accounts.douban.com/login'
        formdata = {
            'redir': 'https://www.douban.com',
            'form_email': '******',
            'form_password': '******',
            'login': u'登陆'
        }

        r = requests.post(url_login, data=formdata, headers=self.douban_headers)
        if r.status_code == 200:
            content = r.text
            soup = BeautifulSoup(content, 'html.parser')
            captcha = soup.find('img', id='captcha_image')  # 当登陆需要验证码的时候
            if captcha:
                print '有验证码'
                captcha_url = captcha['src']
                re_captcha_id = r'<input type="hidden" name="captcha-id" value="(.*?)"/'
                captcha_id = re.findall(re_captcha_id, content)
                print(captcha_id)
                print(captcha_url)
                captcha_text = raw_input('Please input the captcha:')
                formdata['captcha-solution'] = captcha_text
                formdata['captcha-id'] = captcha_id
            else:
                print '无验证码'

            print '正在登录中……'
            r = spider.request_session.post(url_login, data=formdata, headers=self.douban_headers)
            if r.url == 'https://www.douban.com':
                # save cookies
                # self.douban_headers['Cookie'] = r.cookies
                self.douban_cookie = r.cookies
                print '登录成功'
            else:
                print '登录失败', r.text
                if self.login_retry > 0:
                    print '重试……'
                    self.login_retry -= 1
                    self.login()

        else:
            print 'request url error %s -status code: %s:' % (url_login, r.status_code)

    def crawl_detail_page(self, cursor, i, detail_link):
        print 'detail_url_link: ', detail_link
        r = spider.request_session.get(detail_link, cookies=self.douban_cookie, headers=self.douban_headers)  # proxies=spider.proxies
        if r.status_code == 200:
            try:
                # if i == 0 and not self.douban_headers['Cookie']:
                #     print 'set cookie in crawl detail page'
                #     self.douban_headers['Cookie'] = r.cookies
                soup = BeautifulSoup(r.text, "html.parser")

                # print soup.prettify()

                topic_content = soup.find_all(attrs={'class': 'topic-content'})[1]
                if not topic_content:
                    return False
                else:
                    try:
                        content_array = []
                        result_array = topic_content.find_all(['p', 'img'])
                        for item in result_array:
                            # print item.name
                            if item.name == 'p':
                                for br in item.find_all('br'):
                                    br.replace_with('\n')
                                content_array.append(item.text)
                            if item.name == 'img':
                                img_src = item.get('src')
                                content_array.append(img_src)
                        content = ','.join(content_array)

                        try:
                            cursor.execute(spider.update_content_sql, [content, detail_link])
                            print 'Detail Page update content.'
                        except sqlite3.Error, e:
                            print 'Detail Page update content error:', e
                    except Exception, e:
                        print 'error match detail content:', e
            except Exception, e:
                print 'error match topic-content:', e
        else:
            print 'request url error %s -status code: %s:' % (detail_link, r.status_code)
        # sleep for a while
        time.sleep(self.config.douban_sleep_time)

    # i：          小组 index
    # douban_url： 小组数组
    # keyword：    包含关键字
    def crawl_list_page(self, cursor, i, douban_url, page_number, start_timestamp):
        # 构造 url
        url_link = douban_url[i]
        print 'list_url_link: ', url_link
        r = spider.request_session.get(url_link, cookies=self.douban_cookie, headers=self.douban_headers)
        if r.status_code == 200:
            try:
                # if i == 0 and page_number == 0 and not self.douban_headers['Cookie']:
                #     print 'set cookie in crawl list page'
                #     self.douban_headers['Cookie'] = r.cookies
                soup = BeautifulSoup(r.text, "html.parser")
                paginator = soup.find_all(attrs={'class': 'paginator'})[0]
                # print "paginator: ", paginator
                if (page_number != 0) and not paginator:
                    return False
                else:
                    try:
                        table = soup.find_all(attrs={'class': 'olt'})[0]
                        tr_count_for_this_page = 0
                        for tr in table.find_all('tr'):
                            # 过滤表头
                            if tr_count_for_this_page == 0:
                                tr_count_for_this_page = 1
                                continue

                            td = tr.find_all('td')
                            title_element = td[0].find_all('a')[0]
                            # 标题
                            title_text = title_element.get('title')
                            # 链接
                            link_text = title_element.get('href')
                            # 作者
                            user_name_text = td[1].find_all('a')[0].text
                            # 回应
                            reply_count = td[2].text
                            # 最后回应时间
                            last_updated_time_text = td[3].text  # 06-18 21:07
                            last_updated_timestamp = Utils.Utils.my_get_time_from_str(last_updated_time_text)

                            # 时间 检查（结束的条件是配置文件里设置的起始时间）
                            if last_updated_timestamp < start_timestamp:
                                spider.ok = False
                                print 'data at end, stop'
                                break

                            try:
                                # rent(id, title, url, user_name, content, last_updated_time, craw_time,
                                # source, reply_count)
                                cursor.execute(spider.insert_sql, [title_text, link_text,
                                                                   user_name_text,
                                                                   '',
                                                                   last_updated_timestamp,
                                                                   Utils.Utils.get_time_now(),
                                                                   Utils.Utils.my_url_name_list(i),
                                                                   reply_count])
                                print 'List Page create new data:', title_text, last_updated_timestamp, reply_count, link_text
                            except sqlite3.Error, e:
                                print 'List Page data exists:', title_text, link_text, e  # 之前添加过了而URL（设置了唯一）一样会报错
                    except Exception, e:
                        print 'error match table:', e
            except Exception, e:
                print 'error match paginator:', e
                spider.ok = False
                return False
        else:
            print 'request url error %s -status code: %s:' % (url_link, r.status_code)
        # sleep for a while
        time.sleep(self.config.douban_sleep_time)

    def run(self):
        try:
            print '========== 打开数据库... =========='
            # create database
            conn = sqlite3.connect(spider.result_sqlite_name)
            conn.text_factory = str
            cursor = conn.cursor()
            cursor.execute(spider.create_table_sql)
            # cursor.close()
            # cursor = conn.cursor()

            start_timestamp = Utils.Utils.my_get_time_from_str(self.config.start_time)

            print '========== 爬虫开始运行... =========='

            print '========== 爬取豆瓣列表页面... =========='

            # 返回待查询小组的数组（参数 0 代表初始化，每一个都从 index = 0 记录开始查找）
            # 查找的过程：取出每个小组，取出每一页（以起始时间为界），当前页所有记录匹配搜索关键字并且不在黑名单关键字的记录爬取
            douban_url = Utils.Utils.my_url_list(0)
            for i in range(len(douban_url)):
                spider.ok = True
                # 页数计数
                page_number = 0
                print 'start i ->', i

                while spider.ok:
                    print 'i, page_number: ', i, page_number

                    douban_url = Utils.Utils.my_url_list(page_number)
                    # 开始爬取
                    self.crawl_list_page(cursor, i, douban_url, page_number, start_timestamp)
                    # 下一页
                    page_number += 1
                    break  # test once
                break  # test once

            print '========== 爬取豆瓣列表页面完成！ =========='

            print '========== 爬取豆瓣详情页面... =========='
            # 获取抓取的数据
            # cursor.close()
            # cursor = conn.cursor()
            cursor.execute(spider.select_detail_link_sql)
            detail_link_values = cursor.fetchall()

            item_count = len(detail_link_values)

            index = 0
            for detail_link in detail_link_values:
                # print detail_link[0]
                self.crawl_detail_page(cursor, index, detail_link[0])
                index += 1

            print '========== 爬取豆瓣详情页面完成！ =========='

            print '========== 爬虫运行结束，开始写入结果文件 =========='

            cursor.execute(spider.select_sql)
            values = cursor.fetchall()
            print 'Result Values:\n ', values
            # 写入文件
            Utils.Utils.my_write_to_file(values, spider.result_html_name)

            cursor.close()
        except Exception, e:
            print 'Error:', e.message
        finally:
            conn.commit()
            conn.close()
            print '========================================='
            print '''
            ##########     ##########
            #        #     #        #
            #        #     #        #
            #   ##   #     #   ##   #
            #        #     #        #
            #        #     #        #
            ##########     ##########
            '''
            print '========================================='
            print '========== 结果文件写入完毕，数量 %d，请打开 %s.html 查看结果 ==========' % (item_count, spider.result_file_name)


class Spider(object):
    def __init__(self):
        # 取代理 ip
        # proxy_pool = ProxyPool.ProxyPool()
        # self.proxies = proxy_pool.getproxy()
        self.proxies = ''

        self.request_session = requests.Session()

        this_file_dir = os.path.split(os.path.realpath(__file__))[0]
        config_file_path = os.path.join(this_file_dir, 'config.ini')

        # 解析配置文件
        self.config = Config.Config(config_file_path)

        path_name = 'results'

        # 创建目录
        results_path = os.path.join(sys.path[0], path_name)
        if not os.path.isdir(results_path):
            os.makedirs(results_path)

        # 附带时间的文件名
        file_time_format = '%Y%m%d_%X'
        file_time = time.strftime(file_time_format, time.localtime()).replace(':', '')
        self.result_file_name = path_name + '/result_' + str(file_time)
        # 数据库文件名
        self.result_sqlite_name = self.result_file_name + '.sqlite'
        # 网页文件名
        self.result_html_name = self.result_file_name + '.html'

        self.create_table_sql = 'CREATE TABLE IF NOT EXISTS rent(id INTEGER PRIMARY KEY, title TEXT, url TEXT UNIQUE, user_name TEXT, content TEXT, last_updated_time timestamp, craw_time timestamp, source TEXT, reply_count TEXT)'
        self.insert_sql = 'INSERT INTO rent(id, title, url, user_name, content, last_updated_time, craw_time, source, reply_count) VALUES(NULL, ?, ?, ?, ?, ?, ?, ?, ?)'
        self.select_detail_link_sql = 'SELECT url FROM rent'
        self.update_content_sql = 'UPDATE rent SET content = ? WHERE url = ?'
        self.select_sql = 'SELECT * FROM rent ORDER BY last_updated_time DESC ,craw_time DESC'

    def run(self):
        main = Main(self.config)
        main.login()
        main.run()

        # main.crawl_detail_page('', 0, 'https://www.douban.com/group/topic/104164092/')
        # main.crawl_detail_page('', 1, 'https://www.douban.com/group/topic/104162461/')
        # main.crawl_detail_page('', 2, 'https://www.douban.com/group/topic/104175357/')

        return False

if __name__ == '__main__':
    spider = Spider()
    spider.run()

