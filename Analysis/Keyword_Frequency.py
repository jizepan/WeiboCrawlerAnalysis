# -*- coding:utf-8-*-
'''
关键词校出现频率统计
Author： @Tai Lei 邰磊
July 15: 关键词与实际天气联系，比如：下雨微博数量与实际降雨量之间的关系
'''


import matplotlib.pyplot as plt
import os,sys
rootPath = os.path.abspath('../')
sys.path.append(rootPath+"\\Weibo_Scrapy")
from Main import Weibo

#统Main词数量与时间的关系
class Keyword_Frequency():
    
    def __init__(self, weibo_path):
        self.path = weibo_path
        
        self.time_list = []
        
        self.hour_dict = []
        self.hour_num = []
        
        self.day_dict = []
        self.day_num = []
        
    def Get_Text(self):
        #file_address = folder+"\\"+weibo_file
        f = open(self.path, 'r')
        weibo_lines = f.readlines()[1:]
#         for item in weibo_lines:
#             if u"这个夏天有鹿晗" in item:
#                 weibo_lines.remove(item)
        #weibo_sentence = []
        #weibo_all_words = []
        #构建dict keys list
        #print weibo_lines[0]
        end_hour = weibo_lines[1].split(" ")[1][:13]
        begin_hour = weibo_lines[-1].split(" ")[1][:13]
        begin_day = weibo_lines[-1].split(" ")[1][8:10]
        
        time_flag = begin_hour
        next_day = begin_day
        self.day_dict.append(begin_day)       
        
        print end_hour
        while(time_flag <= end_hour):
            #print time_flag
            self.hour_dict.append(time_flag)
            hour_int = int(time_flag[11:])
            day_int = int(time_flag[8:10])
            if hour_int ==23:
                next_day = str(int(next_day) +1)
                if len(next_day)==1:
                    next_day = "0"+next_day
                self.day_dict.append(next_day)
                
                day_int = day_int+1
                day_int = str(day_int)
                if len(day_int) ==1:
                    day_int = "0"+ day_int
                time_flag = time_flag[:8] +  day_int[:] +"-00"
            else:
                hour_int = hour_int+1
                hour_int = str(hour_int)
                if len(hour_int) ==1:
                    hour_int = "0"+ hour_int
                time_flag =time_flag[:11] + hour_int
        
        print self.hour_dict
        print self.day_dict
        
        hour_num = [0 for dummy in xrange(len(self.hour_dict))]
        day_num = [0 for dummy in xrange(len(self.day_dict))]
        
        for item_num in xrange(min(len(weibo_lines), 10000)):
            #item = weibo_lines[item_num].decode('utf-8')
            item = weibo_lines[item_num].split()
            #if len(item) >= 3 and u"这个夏天有鹿晗"  not in weibo_lines[item_num]:       
            if   len(item) >= 3 : 
                #提取时间戳
                hour_text =  item[1][:13]
                
                if hour_text in self.hour_dict:
                    hour_num[self.hour_dict.index(hour_text)] +=1
                
                day_text = item[1][8:10]
                
                if day_text in self.day_dict:
                    day_num[self.day_dict.index(day_text)] +=1
        self.day_num = day_num
        self.hour_num = hour_num
        
        for item in xrange(len(self.hour_num)-min(24,len(self.hour_num)),len(self.hour_num)):
            plt.bar(item-len(self.hour_num)+min(24,len(self.hour_num)), self.hour_num[item])
            plt.axis([0,min(24,len(self.hour_num)),0,max(self.hour_num)])
        plt.show()

        
        for item in xrange(len(self.day_num)):
            begin_day = int(self.day_dict[0])
            plt.bar(item+begin_day, self.day_num[item])
            plt.axis([int(self.day_dict[0]),int(self.day_dict[-1]), 0, max(self.day_num)])
        plt.show()

        
if __name__ =="__main__":

    uid = '2041499443' 
    url = 'http://weibo.cn/'
    
#     weibo_scrapy = Weibo(url,uid)
#     weibo_scrapy.request_check(weibo_scrapy.home_url)
#     weibo_scrapy.get_name()
#     weibo_scrapy.search_statuses(u'北京 下雨',pages = 100)
    
    weibo_file = u"search北京 下雨"
    search_path = rootPath + '\\result\\' + weibo_file
    keyword_object = Keyword_Frequency(search_path)
    
    keyword_object.Get_Text()

    