# coding=utf-8
import datetime


class Utils(object):
    @staticmethod
    def get_time_now():
        return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    @staticmethod
    def is_in_black_list(black_list, to_search):
        if (not black_list) or (black_list[0] is ''):
            return False
        for item in black_list:
            if to_search.find(item) != -1:
                print "in blacklist: " + to_search
                return True
        return False

    @staticmethod
    def get_time_from_str(time_str):
        # 13:47:32或者2016-05-25或者2016-05-25 13:47:32
        # 都转成了datetime
        if '-' in time_str and ':' in time_str:
            return datetime.datetime.strptime(time_str, "%Y-%m-%d %H:%M:%S")
        elif '-' in time_str:
            return datetime.datetime.strptime(time_str, "%Y-%m-%d")
        elif ':' in time_str:
            date_today = datetime.date.today()
            date = datetime.datetime.strptime(time_str, "%H:%M:%S")
            # date.replace(year, month, day)：生成一个新的日期对象
            return date.replace(year=date_today.year, month=date_today.month, day=date_today.day)
        else:
            return datetime.date.today()

    @staticmethod
    def url_list(page_number):
        # 分页查找（豆瓣当前是按每页 50 条显示的）
        num_in_url = str(page_number * 50)
        douban_url = [
            'https://www.douban.com/group/search?start=' + num_in_url + '&group=145219&cat=1013&sort=time&q=']
        # douban_url = ['https://www.douban.com/group/search?start=' + num_in_url +'&group=146409&cat=1013&sort=time&q=',
        #               'https://www.douban.com/group/search?start=' + num_in_url +'&group=523355&cat=1013&sort=time&q=',
        #               'https://www.douban.com/group/search?start=' + num_in_url +'&group=557646&cat=1013&sort=time&q=',
        #               'https://www.douban.com/group/search?start=' + num_in_url +'&group=383972&cat=1013&sort=time&q=',
        #               'https://www.douban.com/group/search?start=' + num_in_url +'&group=283855&cat=1013&sort=time&q=',
        #               'https://www.douban.com/group/search?start=' + num_in_url +'&group=76231&cat=1013&sort=time&q=',
        #               'https://www.douban.com/group/search?start=' + num_in_url +'&group=196844&cat=1013&sort=time&q=',
        #               'https://www.douban.com/group/search?start=' + num_in_url +'&group=259227&cat=1013&sort=time&q=']
        return douban_url

    @staticmethod
    def url_name_list(index):
        douban_url_name = [u'杭州 出租 租房 中介免入']
        return douban_url_name[index]

        # douban_url_name = [u'上海租房', u'上海招聘，租房', u'上海租房(2)', u'上海合租族_魔都租房',
        # u'上海租房@浦东租房', u'上海租房---房子是租来的，生活不是', u'上海租房@长宁租房/徐汇/静安租房',
        # u'上海租房（不良中介勿扰）']

    @staticmethod
    def write_to_file(values, result_html_name):
        try:
            local_file = open(result_html_name, 'wb')
            with local_file:
                local_file.write('''<html>
                                        <head>
                                        <meta http-equiv="Content-Type" content="text/html; charset=utf-8"/>
                                        <title>上海租房信息 | 豆瓣</title>
                                        <link rel="stylesheet" type="text/css" href="../lib/resultPage.css">
                                        </head>
                                        <body>''')
                local_file.write('<h1>上海租房信息 | </h1>')
                local_file.write('''
                                        <a href="https://www.douban.com/" target="_black">
                                        <img src="https://img3.doubanio.com/f/shire/8977fa054324c4c7f565447b003ebf75e9b4f9c6/pics/nav/lg_main@2x.png" alt="豆瓣icon"/>
                                        </a>
                                        ''')
                local_file.write('<table>')
                local_file.write(
                    '<tr><th>索引</th><th>标题</th><th>发帖时间</th><th>抓取时间</th><th>关键字</th><th>来源</th><th>回复数</th></tr>')

                #  rent(id, title, url, itemtime, crawtime, source, keyword, note)
                for row in values:
                    print row
                    local_file.writelines('<tr>')
                    for i in range(len(row)):
                        if i == 2:
                            i += 1
                            continue
                        local_file.write('<td class="column%s">' % str(i))
                        if i == 1:
                            local_file.write('<a href="' + str(row[2]) + '" target="_black">' + str(row[1]) + '</a>')
                            i += 1
                            continue
                        local_file.write(str(row[i]))
                        i += 1
                        local_file.write('</td>')
                    local_file.write('</tr>')
                local_file.write('</table>')
                local_file.write('<script type="text/javascript" src="../lib/resultPage.js"></script>')
                local_file.write('</body></html>')

        except Exception, e:
            print 'error operate file:', e

    @staticmethod
    def my_get_time_from_str(time_str):
        if '-' in time_str and ':' in time_str:  # 06-18 21:07
            date_today = datetime.date.today()
            date_with_year = str(date_today.year) + '-' + time_str
            date = datetime.datetime.strptime(date_with_year, "%Y-%m-%d %H:%M")
            return date
        elif '-' in time_str:  # 2017-06-18
            return datetime.datetime.strptime(time_str, "%Y-%m-%d")

    @staticmethod
    def my_url_list(page_number):
        # 分页查找（豆瓣当前是按每页 50 条显示的） https://www.douban.com/group/145219/discussion?start=0
        num_in_url = str(page_number * 50)
        douban_url = [
            'https://www.douban.com/group/467221/discussion?start=' + num_in_url]
        return douban_url

    @staticmethod
    def my_url_name_list(index):
        douban_url_name = [u'杭州 出租 租房 中介免入']
        return douban_url_name[index]

    @staticmethod
    def my_write_to_file(values, result_html_name):
        try:
            local_file = open(result_html_name, 'wb')
            with local_file:
                local_file.write('''<html>
                                        <head>
                                        <meta http-equiv="Content-Type" content="text/html; charset=utf-8"/>
                                        <title>租房信息 | 豆瓣</title>
                                        <link rel="stylesheet" type="text/css" href="../lib/resultPage.css">
                                        </head>
                                        <body>''')
                local_file.write('<h1>租房信息 | </h1>')
                local_file.write('''
                                        <a href="https://www.douban.com/" target="_black">
                                        <img src="https://img3.doubanio.com/f/shire/8977fa054324c4c7f565447b003ebf75e9b4f9c6/pics/nav/lg_main@2x.png" alt="豆瓣icon"/>
                                        </a>
                                        ''')
                local_file.write('<table>')
                local_file.write(
                    '<tr><th>索引</th><th>标题</th><th>作者</th><th>地区</th><th>地址</th><th>联系方式</th><th>最后回应</th><th>抓取时间</th><th>小组</th><th>回应数</th></tr>')

                # 'INSERT INTO rent(id, title, url, user_name, content, area, address, contact, last_updated_time,
                # craw_time, source, reply_count)
                for row in values:
                    local_file.writelines('<tr>')
                    for i in range(len(row)):
                        if i in [2, 4]:
                            i += 1
                            continue
                        local_file.write('<td class="column%s">' % str(i))
                        if i == 1:
                            local_file.write('<a href="' + str(row[2]) + '" target="_black">' + str(row[1]) + '</a>')
                            i += 1
                            continue
                        local_file.write(str(row[i]))
                        i += 1
                        local_file.write('</td>')
                    local_file.write('</tr>')
                local_file.write('</table>')
                local_file.write('<script type="text/javascript" src="../lib/resultPage.js"></script>')
                local_file.write('</body></html>')

        except Exception, e:
            print 'error operate file:', e

# last_updated_timestamp = Utils.my_get_time_from_str('06-19 21:07')
# start_timestamp = Utils.my_get_time_from_str('2017-06-18')
# print last_updated_timestamp
# print start_timestamp
# if last_updated_timestamp < start_timestamp:
#     print 'out of time'
# else:
#     print '22222'
