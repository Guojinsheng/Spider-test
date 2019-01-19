import os
import gevent
from gevent import monkey

monkey.patch_all()

import time
import requests
from lxml import etree
import threading
from threading import Thread

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.102 Safari/537.36"
}


# BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# 将返回的url进行解析，获取对应的小说的url
def get_book(url):
    req = requests.get(url, headers=headers)
    html = req.text

    mytree = etree.HTML(html)
    book_list = mytree.xpath('//div[@id="newscontent"]/div/ul/li')
    print(book_list)
    list = []
    for book in book_list:
        url = book.xpath('./span/a/@href')

        url = ''.join(url)
        list.append(url)
        # print(url)
    return list


# 将对应的小说的url进行进一步的解析，获取每一章的url和章节名
def get_content(url):
    req = requests.get(url, headers=headers)
    html = req.text

    mytree = etree.HTML(html)
    name = ''.join(mytree.xpath('//div[@id="info"]/h1/text()'))
    content_list = mytree.xpath('//div[@id="list"]/dl/dd')
    # print(name,content_list)
    g_list = []
    for content in content_list:
        content_name = ''.join(content.xpath('./a/text()'))
        content_url = ''.join(content.xpath('./a/@href'))
        time.sleep(0.25)
        # print(name,content_name,content_url)
        g = gevent.spawn(get_txt, name, content_name, content_url)
        g_list.append(g)
    gevent.joinall(g_list)


# 将上级反馈出来的url进行爬取，获取每一章的文字并保存在指定目录下

def get_txt(name, content_name, content_url):
    req = requests.get(content_url, headers=headers)
    html = req.text
    # print(html)

    mytree = etree.HTML(html)
    content_list = mytree.xpath('//div[@id="content"]/p')
    print(content_list)
    for content in content_list:
        content = ''.join(content.xpath('./text()'))
        print(content)
        # os.mkdir()

        save_path = './xiaoshuo'
        # 获取小说名称
        story_title = name
        # 根据小说名称创建一个文件夹,如果不存在就新建
        dir_path = save_path + '/' + story_title
        if not os.path.exists(dir_path):
            os.path.join(save_path, story_title)
            os.mkdir(dir_path)

        # 章节名称
        chapter_name = content_name
        # # 将当前章节，写入以章节名字命名的txt文件
        with open(dir_path + '/' + chapter_name + '.txt', 'a', encoding='utf-8') as f:
            f.write(content)


if __name__ == '__main__':
    start = time.time()
    book_list = get_book('https://www.biquge5200.cc/xuanhuanxiaoshuo/')
    t_list = []
    # 创建多线程
    for t in book_list:
        t = threading.Thread(target=get_content, args=(t,))
        t.start()
        time.sleep(0.5)
        t_list.append(t)
    for t in t_list:
        t.join()
    end = time.time()
    print(end - start)
