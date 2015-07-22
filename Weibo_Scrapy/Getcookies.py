# -*- coding: utf-8 -*-
'''
Created on 2015.6.18

@author: Lei.Tai 邰磊

主要功能： 从chrome默认文件夹中提取出cookies，复制到D盘，从中提取任意需要的网站的cookies
'''
import sqlite3
import win32crypt
import os
import requests
from bs4 import BeautifulSoup

class Get_Chrome_Cookies():
    
    def __init__(self):
        pass
    
    def get_cookies(self,url):
        os.system('copy "C:\\Users\\Tyler\\AppData\\Local\\Google\\Chrome\\User Data\\Default\\Cookies"  D:\\python-chrome-cookies')
        conn = sqlite3.connect("d:\\python-chrome-cookies")
        ret_list = []
        ret_dict = {}
        for row in conn.execute("select host_key, name, path, value, encrypted_value from cookies"):
            if row[0] != url:
                continue
            ret = win32crypt.CryptUnprotectData(row[4], None, None, None, 0)
            ret_list.append((row[1], ret[1]))
            ret_dict[row[1]] = ret[1].decode()
        conn.close()
        #os.system('del "D:\\python-chrome-cookies"')
        return ret_dict



# def getcookies(url):
# 
#     conn = sqlite3.connect("d:\\python-chrome-cookies")
#     ret_list = []
#     ret_dict = {}
#     for row in conn.execute("select host_key, name, path, value, encrypted_value from cookies"):
#         if row[0] != url:
#             continue
#         ret = win32crypt.CryptUnprotectData(row[4], None, None, None, 0)
#         ret_list.append((row[1], ret[1]))
#         ret_dict[row[1]] = ret[1].decode()
#     conn.close()
#     return ret_dict


if __name__ == '__main__':
    
    cookies_c = Get_Chrome_Cookies()
    x = requests.get("http://weibo.com", cookies=cookies_c.get_cookies(".weibo.com"))
    #x = requests.get("http://www.zhihu.com", cookies=get_chrome_cookies(".zhihu.com"))
    print x.encoding
    soup = BeautifulSoup(x.text)
    print soup.prettify('utf-8')
    #print soup.title
    for link in soup.findAll('link'):
        print (link['href'])
        