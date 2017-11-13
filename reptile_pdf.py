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

def parse_url_to_html(url):
    response =requests.get(url)

    soup = BeautifulSoup(response.content, "html.parser")
    # class => 'class_'
    # id => 'id'
    body = soup.find_all(id='maincontent')[0]
    html = str(body)

    '''
    此处出现编码问题，
      File "reptile_pdf.py", line 42, in parse_url_to_html
    html = html.encode("utf-8")
UnicodeDecodeError: 'ascii' codec can't decode byte 0xe6 in position 34: ordinal not in range(128)

    解决：采用 unicode 强转 unicode(html, "utf-8")
    '''

    html = unicode(html, "utf-8")

    html = html_template.format(content=html)
    html = html.encode("utf-8")

    with open("a.html", 'wb') as f:
        f.write(html)


# parse_url_to_html(u'http://www.w3school.com.cn/html5/index.asp')


def parser_menu_html(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    menu = soup.find_all(id='course')[1]
    urls = []
    for li in menu.find_all('li'):
        url = u'http://www.liaoxuefeng.com' + li.a.get('href')
        urls.append(url)

    return urls



def save_pdf():
    """
    把所有html文件转换成pdf文件
    """
    options = {
        'page-size': 'Letter',
        'encoding': "UTF-8",
        'custom-header': [
            ('Accept-Encoding', 'gzip')
        ]
    }
    # parse_url_to_html(u'http://www.w3school.com.cn/html5/index.asp')
    # htmls_url = parser_menu_html(u'http://www.w3school.com.cn/html5/index.asp')

    file_name = "廖雪峰python 教程.pdf"
    pdfkit.from_file(['a.html'], file_name, options=options)

save_pdf()