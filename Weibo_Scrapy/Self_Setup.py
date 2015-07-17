# _*_coding=utf-8_*_
'''
Created on 2015.6.25

@author: Lei.Tai 邰磊

主要功能：自动运行爬取历史和现在微博
'''

from Main import Weibo
from shutil import move
from os import remove
from pymongo import MongoClient
import os

#Get file address now
rootPath = os.path.abspath('../')
#file_address = os.path.dirname(os.path.abspath(__file__))

# # get cookies
# chromeCookies = Get_Chrome_Cookies()
# Cookies = chromeCookies.get_cookies(".weibo.cn")

# main url
url= 'http://weibo.cn/'

# setup file to get uid and start weibo id
setup_file = 'setup.txt' 
copy_file = rootPath + '\\copy\\setup.txt'

#get on server mongodbmain
client = MongoClient('54.223.178.198', 27110)
db = client['weibo-database']
collection = db['weibo-collection']

#check the total number of uid
f = open(setup_file, 'r')
a = f.readlines()
Total_number = len(a)
f.close()

weibo_scrapy = Weibo(url, '')
#Scrapy Sina
while True:
    for n_count in xrange(Total_number):
        f = open(setup_file, 'r')
        a = f.readlines()
        Total_number = len(a)
        f.close()
        list_id_time = []
        
        for n_dummy in xrange(Total_number):
            list_id_time.append(a[n_dummy].split())
            if (len(list_id_time[n_dummy]) ==1):
                list_id_time[n_dummy].append(' ')
        
        f = open(copy_file,'w')
        uid_n = list_id_time[n_count]
        weibo_scrapy.uid  = uid_n[0]
        weibo_scrapy.home_url = weibo_scrapy.main_url + weibo_scrapy.uid
        print "we are going to scrapy this uid: ", weibo_scrapy.uid
        weibo_scrapy.request_check(weibo_scrapy.home_url)
        weibo_scrapy.get_name()
        #print len(uid_n)
        uid_n[1] =  weibo_scrapy.statuses(uid_n[1])
        list_id_time[n_count][1] = uid_n[1]
        
        for n_dummy in xrange(Total_number):
            f.write(list_id_time[n_dummy][0] +' '+  list_id_time[n_dummy][1]+' ' + '\n')
        f.close()
    
        remove(setup_file)
        move(copy_file,setup_file)