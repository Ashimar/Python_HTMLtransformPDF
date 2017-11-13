# coding:utf-8

from __future__ import unicode_literals

import logging
import os
import re
import time

try:
    from urllib.parse import urlparse   # py3
except:
    from urlparse import urlparse       # py2

import pdfkit
import requests
from bs4 import BeautifulSoup

html_template = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
</head>
<body>
{content}
</body>
</html>
"""

class Crawler(object):
    """爬虫基类， 所有爬虫多应该继承此基类"""

    name = None

    def __init__(self, name, start_url):
        """
        初始化
        :param name： 将要被保存为PDF的文件名称
        :param start_url: 爬虫入口UTL
        """

        self.name = name
        self.start_url = start_url
        self.domain = '{uri.scheme}://{uri.netloc}'.format(uri=urlparse(self.start_url))

    @staticmethod
    def request(url, **kwargs):
        """
        网络请求,返回response对象
        :return:
        """
        response = requests.get(url, **kwargs)
        return response

    def parse_menu(self, response):
        """
        从 response 中解析出所有目录的URL链接
        :param response:
        :return: 返回经过处理的HTML正文文本
        """
        raise NotImplementedError

    def parse_body(self, response):
        """
        解析正文，由子类实现
        :param response: 爬虫返回的respon对象
        :return: 返回经过处理的HTML正文
        """
        raise NotImplementedError

    def run(self):
        start = time.time()
        # 设置格式
        options = {
            'page-size': 'Letter',
            'margin-top': '0.75in',
            'margin-right': '0.75in',
            'margin-bottom': '0.75in',
            'margin-left': '0.75in',
            'encoding': "UTF-8",
            'custom-header': [
                ('Accept-Encoding', 'gzip')
            ],
            'cookie': [
                ('cookie-name1', 'cookie-value1'),
                ('cookie-name2', 'cookie-value2'),
            ],
            'outline-depth': 10,
        }
        htmls = []

        # print 'target url:
        # 遍历目录中的内容%s' % self.start_url
        # print '--------'
        # print self.request(self.start_url)
        # print '--------'
        # print self.parse_menu(self.request(self.start_url))
        # print '--------'
        for index, url in enumerate(self.parse_menu(self.request(self.start_url))):
            html = self.parse_body(self.request(url))
            f_name = ".".join([str(index), "html"])
            html = str(html)
            html = unicode(html, "utf-8")
            with open(f_name, 'wb') as f:
                html = html.encode("utf-8")
                f.write(html)
            htmls.append(f_name)
            # break

        # 转化为 pdf 格式
        pdfkit.from_file(htmls, self.name + '.pdf', options=options)

        for html in htmls:
            os.remove(html)
        total_time = time.time() - start
        print u'总共耗时：%f 秒' % total_time


class CrawlerLiaoxuefengPython(Crawler):
    """
    廖雪峰 Python 2 教程
    """

    def parse_menu(self, response):
        """
        解析目录结构，获取所有URL目录列表
        :param response: 爬虫返回的response对象
        :return: url 生成器
        """

        soup = BeautifulSoup(response.content, "html.parser")
        print soup.find_all(id="course")
        menu_tag = soup.find_all(id="course")[0]

        for li in menu_tag.find_all('li'):
            url = li.a.get('href')
            if not url.startswith('http'):
                url = "".join([self.domain, url])   # 补全为全路径
            yield url

    def parse_body(self, response):
        """
        解析正文
        :param response: 爬虫返回的response 对象
        :return: 返回处理饭的HTML文本
        """

        try:
            soup = BeautifulSoup(response.content, 'html.parser')
            body = soup.find_all(id="maincontent")[0]
            # 加入标题，居中显示
            # title = soup.find('h1').get_next()
            # center_tag = soup.new_tag("center")
            # title_tag = soup.new_tag('h1')
            # title_tag.string = title
            # center_tag.insert(1, title_tag)
            # body.insert(1, center_tag)

            html = str(body)
            # body中 img 标签的src 相对路径改成绝对路径
            pattern = "(<img .*?src=\")(.*?)(\")"

            def func(m):
                if not m.group(2).startswitch("http"):
                    rtn = "".join([m.group(1), self.domain, m.group(2), m.group(3)])
                    return rtn
                else:
                    return "".join([m.group(1), m.group(2), m.group(3)])

            html = re.compile(pattern).sub(func, html)

            html = unicode(html, "utf-8")
            html = html_template.format(content=html)
            print '--format之后的内容--'
            print html
            html = html.encode("utf-8")
            print '----'
            print html

            return html

        except Exception as e:
            logging.error("解析错误", exc_info=True)


if __name__ == '__main__':
    start_url = "http://www.w3school.com.cn/html5/index.asp"
    crawler = CrawlerLiaoxuefengPython("w3school HTML5 教程", start_url)
    crawler.run()





