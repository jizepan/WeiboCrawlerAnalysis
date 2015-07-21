# -*- coding:utf-8 -*-
'''
Created on 2015.6.18

@author: Lei.Tai

Get all of the weibo in history and now from weibo UID
'''
import requests
from bs4 import BeautifulSoup
from bs4 import element
#from getcookies import Get_Chrome_Cookies
#from _mysql import result
import string
import sys
import re
from datetime import date
from datetime import datetime
from pymongo import MongoClient
import os
import time

#get the file address relative
rootPath = os.path.abspath('../')
#sys.path.append(rootPath+"\\Weibo_Scrapy")
#file_address = os.path.dirname(os.path.abspath(__file__)) + r'\result'+'\\'
file_address = rootPath + r'\result'+'\\'

#Set standard of encoding for Chinese Input
reload(sys) 
sys.setdefaultencoding('utf-8')

#server
client = MongoClient('54.223.178.198', 27110)
db = client['weibo-database']
collection = db['weibo-collection']

Cookies_default = {'_T_WM':'59dd96edf8a384849f4aa87db6872e41', 'SUB':'_2A254lxFWDeTxGeNI6FYV9yfNzzWIHXVYe78erDV6PUJbrdBeLWP8kW1L5HRza0vtGEw0AR8k3D_YPVnBGA..', 'SUHB':'0N21q-v5V84CQy', 'SSOLoginState':'1435721990'}

headers_default = {
                   'Connection': 'keep-alive',
                    'Accept': r'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                    'User-Agent': r'Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/43.0.2357.130 Safari/537.36',
                    'Accept-Encoding': r'gzip, deflate, sdch',
                    'Accept-Language': r'zh-CN,zh;q=0.8,en;q=0.6'
                   }
class Weibo():
    '''
    Log in Weibo, get the important information here, through login your weibo ID from cookies
    '''
    
    def __init__(self, main_url, uid, log_cookies= Cookies_default,collection=collection):
        self.main_url = main_url
        self.cookies = log_cookies
        self.uid = uid
        self.name = ''
        self.collection = collection
        #微博主页url
        self.home_url = self.main_url + self.uid
        
    def request_check(self,url,params={}):
        '''
        Check if the ID is abandoned
        '''
        #self.cookies_parse()
        time.sleep(0.5)
        respond_request = requests.get(url, params = params, headers = headers_default, cookies=self.cookies)
        while(respond_request.history):    
            print "redirect happen: ", respond_request.history
            self.cookies_parse()
            respond_request = requests.get(url, params = params, headers = headers_default, cookies = self.cookies)
        self.soup = BeautifulSoup(respond_request.content)
        return self.soup
    
    def cookies_parse(self):
        cookies = raw_input('New updated cookies: ')
        cookies_array = cookies.split() 
        for item in cookies_array:
            if '=' not in item:
                cookies_array.remove(item)
        for dummy_i in xrange(len(cookies_array)):    
            cookies_array[dummy_i]= string.replace(cookies_array[dummy_i], ';', '', 1)
            cookies_array[dummy_i] = cookies_array[dummy_i].split('=')
        self.cookies = dict(cookies_array)
        
    def statuses(self, start_id = ' '):
        '''
        time id coding problem
        location getting
        '''
        url = self.main_url + self.uid
        print 'Main url: ', url
        #got name and pages
        check_url = self.main_url + self.uid
        count_flag =0
        while(len(self.soup.body.contents)<100 and count_flag<10):
            self.request_check(check_url)
            count_flag+=1    
        self.name = self.get_name()
        pages = self.get_pages(self.soup)
        
        print self.name, '\' weibo has ', pages, 'pages'
        f = open(file_address+self.name+'weibo', 'a')
        
        start_flag = 0
        first_id = start_id
        
        # all of the pages
        for x in xrange (1,pages):
            payload = {'page': str(x)}
            #get method of request，with payload keyvalue to some page
            page_soup = self.request_check(url, params=payload)
            count_flag=0
            while (self.get_pages(page_soup) != pages and count_flag<10):
                print "not enough: "
                page_soup = self.request_check(url, params=payload)
                count_flag+=1
            for div_tag in page_soup.body.children:
                if (div_tag['class'] == ['c']):
                    weibo_text = ''
                    for tag in div_tag.find_all('span'):
                        if (tag['class'] == ['ctt']):
                            #find weibo main tag， tag_p is the text tag of weibo 'div' tag
                            tag_p = tag.parent
                            

                            #find weibo ID
                            weibo_tag = tag_p.parent
                            weibo_id = weibo_tag['id']
                            #RE，match weibo like:_45646546&
                            id_re = re.search(r'(?<=[_]).+$',weibo_id)
                            if id_re:
                                weibo_id = id_re.group()
                            
                            top_flag = 0
                            for tag in div_tag.find_all('span'):
                                if (tag.has_attr('class')) and (tag['class'] == ['kt']):
                                    top_flag = 1
                                    break
                            
                            write_flag=0
                            if  string.swapcase(str(weibo_id)) > string.swapcase(str(start_id)):
                                write_flag =1                                                                                 
                            
                            #Update the newest weibo ID
                            if (start_flag ==0) and (top_flag ==0) and (write_flag ==1):
                                first_id = weibo_id
                                start_flag=1
                            
                            #Stop the scrapy or not by check the weibo id
                            if (top_flag ==0) and string.swapcase(str(weibo_id)) <= string.swapcase(str(start_id)):
                                f.close()
                                return first_id
                            
                            # get weibo_time by function
                            weibo_time, time_tag = self.get_time(tag_p)
                            #print weibo_time                      
                            
                            #find the latitude and longitude in weibo place
                            lat = ''
                            longitude =''
                            weibo_place =''
                            for place_tag in tag_p.find_all('a'):
                                if 'center' in place_tag['href']:
                                    place_url = place_tag['href']
                                    #regular expression to find lat and long, like: center=65.555,45.555&
                                    place_re = re.search(r'(?<=center=)(\d|\.|\,)+(?=&)', place_url)
                                    if place_re:
                                        place_string = place_re.group().split(',')
                                        lat = place_string[0]
                                        longitude = place_string[1]
                            if (len(lat)!=0):
                                weibo_place =  lat+'&'+longitude
                            
                            #got the weibo_text
                            first_span = tag_p.find('span')
                            #if it was retwitter
                            if first_span['class'] == ['cmt']:
                                #come from and the original text
                                weibo_text = first_span.get_text('&') + first_span.next_sibling.get_text('&')
                                #reason to reweibo
                                for text_sibling in time_tag.previous_siblings:
                                    if (type(text_sibling) == element.Tag) and text_sibling.has_attr('href') and ('http://weibo.cn/attitude/' in text_sibling['href']):
                                        for final_sibling in text_sibling.previous_siblings:
                                            if type(final_sibling) == element.Tag:
                                                weibo_text = final_sibling.get_text()+weibo_text
                                            elif type(final_sibling) == element.NavigableString:
                                                weibo_text = final_sibling + weibo_text
                                        break
                            #if it was created get all of the text directly
                            elif first_span['class'] == ['ctt']:
                                weibo_text = first_span.get_text('&')
                                
                            #delete all of the space
                            weibo_text = string.replace(weibo_text, ' ', '')
                            #delete the space in pattern of $bnsp 
                            weibo_text = string.replace(weibo_text, u'\xa0', '')
                            
                            #print weibo_text
                            #save the weibo_text
                            if (write_flag == 1):
                                f.write('\n'+self.uid + ' ' + weibo_id +' ' + weibo_time + ' ' + weibo_text + ' ' + weibo_place ) 
                                weibo_data = {'uid':self.uid, 'id':weibo_id, 'time':weibo_time, 'text':weibo_text, 'place':weibo_place}
                                print 'Scrapy ', self.name, ' weibo id: ', weibo_data['id'], ' at ', weibo_data['time']
                                #print 'start_id: ', start_id
                                #self.collection.insert_one(weibo_data)
        f.close()
        return first_id
    
    def search_users(self, name, fans_flag):
        search_user_url = 'http://weibo.cn/search/user/'
        payload = {'keyword': name}
        page_soup = self.request_check(search_user_url, params=payload)
        pages = self.get_pages(page_soup)
        
        f = open(file_address+name+'_search_'+str(fans_flag), 'wb')
        for x in xrange(1, pages):
            payload = {'keyword': name, 'page': str(x)}
            #get all of the pages
            page_soup = self.request_check(search_user_url, params=payload)           
                 
            count = 1
            #find 'br' tag
            for div_tag in page_soup.body.find_all('br'):
                if (count%2==0):
                    #fans_uid_url
                    for next_fans_tag in div_tag.next_siblings:
                        if (type(next_fans_tag) == element.Tag) and (next_fans_tag.name == 'a'):
                            fans_tag = next_fans_tag
                    find_url = fans_tag['href']
                    
                    #fans_number
                    number_string = div_tag.next_sibling
                    #re to find count of fans
                    fans_re = re.search(r'\d+', number_string)
                    if fans_re:
                        print fans_re.group()
                    
                    #re to find uid, number of latter, like: /attention/add?uid=1647687670&rl=1&st=da0a1
                    fans_uid = re.search(r'(?<=uid=)\d+(?=&)',find_url)
                    if fans_uid:
                        print fans_uid.group()
                    
                    #only choose the one with more than 10000 fans
                    if (int(fans_re.group())>int(fans_flag)):
                        f.write(fans_uid.group() + '\n')
                count += 1             
        f.close()            
            
        print pages

        
    
    def search_statuses(self, keyword, pages = 30):
        url = "http://weibo.cn/search/"
        
        f = open(file_address+'search'+keyword, 'w')
        temp_pages = pages
        for x in xrange (1,temp_pages):
            payload = {'keyword': keyword,"smblog": "搜微博",'page': str(x)}
            #get method of request，with payload keyvalue to some page
            page_soup = self.request_check(url, params=payload)
            for div_tag in page_soup.body.children:
                if (div_tag['class'] == ['c']):
                    weibo_text = ''
                    for tag in div_tag.find_all('span'):
                        if (tag['class'] == ['ctt']):
                            #find weibo main tag， tag_p is the text tag of weibo 'div' tag
                            tag_p = tag.parent

                            #find weibo ID
                            weibo_tag = tag_p.parent
                            weibo_id = weibo_tag['id']
                            #RE，match weibo like:_45646546&
                            id_re = re.search(r'(?<=[_]).+$',weibo_id)
                            if id_re:
                                weibo_id = id_re.group()
                            
                            # get weibo_time by function
                            weibo_time, time_tag = self.get_time(tag_p)
                            #print weibo_time                      
                            
                            #find the latitude and longitude in weibo place
                            lat = ''
                            longitude =''
                            weibo_place =''
                            for place_tag in tag_p.find_all('a'):
                                if 'center' in place_tag['href']:
                                    place_url = place_tag['href']
                                    #regular expression to find lat and long, like: center=65.555,45.555&
                                    place_re = re.search(r'(?<=center=)(\d|\.|\,)+(?=&)', place_url)
                                    if place_re:
                                        place_string = place_re.group().split(',')
                                        lat = place_string[0]
                                        longitude = place_string[1]
                            if (len(lat)!=0):
                                weibo_place =  lat+'&'+longitude
                            
                            #got the weibo_text
                            first_span = tag_p.find('span')
                            #if it was retwitter
                            if first_span['class'] == ['cmt']:
                                #come from and the original text
                                weibo_text = first_span.get_text('&') + first_span.next_sibling.get_text('&')
                                #reason to reweibo
                                for text_sibling in time_tag.previous_siblings:
                                    if (type(text_sibling) == element.Tag) and text_sibling.has_attr('href') and ('http://weibo.cn/attitude/' in text_sibling['href']):
                                        for final_sibling in text_sibling.previous_siblings:
                                            if type(final_sibling) == element.Tag:
                                                weibo_text = final_sibling.get_text()+weibo_text
                                            elif type(final_sibling) == element.NavigableString:
                                                weibo_text = final_sibling + weibo_text
                                        break
                            #if it was created get all of the text directly
                            elif first_span['class'] == ['ctt']:
                                weibo_text = first_span.get_text('&')
                                
                            #delete all of the space
                            weibo_text = string.replace(weibo_text, ' ', '')
                            #delete the space in pattern of $bnsp 
                            weibo_text = string.replace(weibo_text, u'\xa0', '')
                            
                            print weibo_text
                            #save the weibo_text

                            f.write('\n'+ weibo_id +' ' + weibo_time + ' ' + weibo_text + ' ' + weibo_place ) 
                            weibo_data = {'uid':self.uid, 'id':weibo_id, 'time':weibo_time, 'text':weibo_text, 'place':weibo_place}
                            print 'Scrapy weibo id: ', weibo_data['id'], ' at ', weibo_data['time']
                            #print 'start_id: ', start_id
                            #self.collection.insert_one(weibo_data)
        f.close()

    def search_stag(self):
        url = 'http://weibo.cn/search/?keyword=啊啊啊&stag=搜标签'
    
    def fans(self):
        '''
        get fans of the uid user
        '''
        url = self.main_url + self.uid+'/fans'
        fans_soup = self.request_check(url,)
        pages = self.get_pages(fans_soup)

        f = open(file_address+self.name+'fans', 'wb')
        for x in xrange (1,pages):
            payload = {'page': str(x)}
            page_soup = self.request_check(url, params = payload)
            
            count = 0
            #find 'br' tag
            for div_tag in page_soup.body.find_all('br'):
                #if div_tag.prev_sibling().has_attr('href'):
                if (count%2==0):
                    fans_tag =  div_tag.parent.find('a')
                    find_url = fans_tag['href']
                    
                    #re to find uid, number of latters, like: /456123564$
                    fans_uid = re.search(r'(?<=[/])[^/]+$',find_url)
                    if fans_uid:
                        print fans_uid.group()
                    
                    f.write(fans_tag['href']+" "+fans_tag.get_text()+' '+fans_uid.group() + '\n')
                count += 1             
        f.close()
        print "get fans"
    def following(self):
        '''
        get follow of the uid user
        '''
        url = self.main_url + self.uid+ '/follow'
        fans_soup = self.request_check(url)
        pages = self.get_pages(fans_soup)

        f = open(file_address+self.name+'follow', 'wb')
        for x in xrange (1,pages):
            payload = {'page': str(x)}
            result = self.request_check(url, params=payload)
            page_soup = BeautifulSoup(result.content)
            
            count = 0
            #find 'br' tag
            for div_tag in page_soup.body.find_all('br'):
                #if div_tag.prev_sibling().has_attr('href'):
                if (count%2==0):
                    fans_tag =  div_tag.parent.find('a')
                    find_url = fans_tag['href']
                    #re to find uid
                    fans_uid = re.search(r'(?<=[/])[^/]+$',find_url)
                    if fans_uid:  
                        print fans_uid.group()
                    #if type(fans_tag) == element.Tag:
                    print fans_tag
                    f.write(fans_tag['href']+" "+fans_tag.get_text()+' '+fans_uid.group() + '\n')
                count += 1             
        f.close()
        print "get follow"
    
    def get_pages(self, BS_html):
        '''
        get the search pages
        '''
        pages = 0
        for tag in BS_html.find_all('input'):
            if  tag.has_attr('name') and (tag['name'] == 'mp'):
                pages = int(tag['value'])+1
        return pages    
    
    def get_name(self):
        '''
        get the main name
        '''
        for div_tag in self.soup.body.find_all('span'):
            if div_tag.parent['class'] ==['ut']:
                uid_name = div_tag.contents[0].split()
                #print "uid_name: ", uid_name[0]
                self.name = uid_name[0]
                return self.name
    def item(self, item):
        '''
        weibo #item#
        http://huati.weibo.com/k/邓超出轨 from PC
        get url redirect
        and the id of item
        then 
        '''
        #.com端提取话题的id
        url = "http://huati.weibo.com/k/"+item
        RedirectRes = requests.get(url)
        id_text =  RedirectRes.history[1].url
        #正则匹配 http://weibo.com/p/100808af11cd4d7396d740cfd8b8e69374de79?k=%E9%82%93%E8%B6%85%E5%87%BA%E8%BD%A8&_from_=huati_topic
        item_id_re = re.search(r'(?<=\/p\/).+(?=\?k\=)',id_text)
        if item_id_re:
            item_id = item_id_re.group()
        url = "http://m.weibo.cn/p/index?containerid="+item_id
        
        
    def comments(self):
        '''
        sibling_next of the pms
        http://weibo.cn/2834256503/CmFjuoATA
        '''
        pass
    
    def get_locations(self):
        '''
        get location of some weibo by id
        '''
        
    def get_time(self, tag_p):
        '''
        get time of the weibo
        '''
        #find weibo time
        year = str(date.today().year)
        month = str(date.today().month)
        if len(month) ==1:
            month = '0'+month
        day = str(date.today().day)
        if len(day) ==1:
            day = '0'+day
        time_flag = 0
        for s_tag in tag_p.parent.descendants:
            if (time_flag==0) and ((type(s_tag) == element.Tag) and (s_tag.name == 'span') and (s_tag['class'] == ['ct'])):
                weibo_time =  s_tag.get_text()
                time_tag = s_tag
                time_flag=1
                weibo_time_original = weibo_time
                weibo_time = weibo_time.encode('ascii', 'ignore')
         
        #match the earliest time : like:2012-04-04 13:15:56
        Full_time_re = re.match(r'\d{4}\-\d{2}\-\d{2}\s\d{2}\:\d{2}', weibo_time)
        #message of this year  : 6X5X 10:43
        This_year_re = re.match(r'\d{4}\s\d{2}\:\d{2}', weibo_time)
        #message of this day   :  XX  11:56
        Today_re = re.search(r'\d{2}\:\d{2}', weibo_time)
        #message of this hour，: 23XXX
        Recent_re = re.match(r'\d{1,2}', weibo_time_original)
         
        #which one it matched
        if Full_time_re:
            weibo_time = Full_time_re.group()
            weibo_time = string.replace(weibo_time, ' ', '-')
        elif This_year_re:
            weibo_time = This_year_re.group()
            weibo_time = year+'-'+weibo_time[0:2]+'-'+weibo_time[2:4]+'-'+weibo_time[5:]
        elif Today_re:
            weibo_time = Today_re.group()
            weibo_time = year+'-'+ month+'-'+ day+'-' + weibo_time
        elif Recent_re:
            weibo_time = int(Recent_re.group(0))
            hour = datetime.now().hour
            minute = datetime.now().minute
            if weibo_time > minute:
                hour = str(hour -1)
                minute = str(minute+60-weibo_time)
            else:
                hour = str(hour)
                minute = str(minute - weibo_time)
            if len(hour) == 1:
                hour = '0'+hour
            if len(minute) == 1:
                minute = '0'+minute
            weibo_time = year+'-'+ month+'-'+ day+'-' + hour+':'+minute
        return weibo_time, time_tag
        #print weibo_time
        
    
if __name__ == '__main__':
    
    #chromeCookies = Get_Chrome_Cookies()
    #Cookies = chromeCookies.get_cookies(".weibo.cn")
    Cookies = {u'_T_WM':u'59dd96edf8a384849f4aa87db6872e41', u'SUB':u'_2A254ljjjDeTxGedM6VcV-S3PyTmIHXVYeVirrDV6PUJbrdBeLUj3kW0qLg6ecUPP8bIiTE36WND2w6mLHQ..',u'SUHB':u'0G0v5rF1r6wR50',u'SSOLoginState':u'1435650227', u'M_WEIBOCN_PARAMS':u'uicode%3D20000174'}
    url = 'http://weibo.cn/'
    #url = "http://weibo.cn/u/5542939834"
    #url = "http://weibo.cn/u/1776514395"
    #uid = '1689944994'  
    #uid = '2041499443'  
    uid = '2041499443' 
        
    #Scrapy Zhihu
    #x = requests.get("http://www.zhihu.com", cookies=getcookies(".zhihu.com")) 
    
    #Scrapy Sina
    weibo_scrapy = Weibo(url,uid)
    #weibo_scrapy.request_check(weibo_scrapy.home_url)
    #weibo_scrapy.get_name()
    #start_id = weibo_scrapy.statuses(' ')
    weibo_scrapy.item(u'邓超出轨')
    #weibo_scrapy.fans()
    #weibo_scrapy.search_users('航空', 10000)
    #weibo_scrapy.following()