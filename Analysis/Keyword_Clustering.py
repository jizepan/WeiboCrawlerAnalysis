# -*- coding:utf-8-*-
'''
中文分词和微博词频统计
Author： @Tai Lei 邰磊 @Jize.pan 潘基泽
July 7: 文件建立，构建基本微博词频分析
'''

import jieba
import lda
import numpy as np
import nltk
from nltk.probability import FreqDist
from sklearn.feature_extraction.text import CountVectorizer, TfidfTransformer
import jieba.analyse
import os,sys
rootPath = os.path.abspath('../')
sys.path.append(rootPath+"\\Weibo_Scrapy")

#循环提取所有微博
# for file_item in os.listdir(folder):
#     file_address = folder + "\\"+ file_item
#     f = open(file_address, 'r')
#     line = f.readline()
#     lin2 = f.readline()

#提取全文本词汇，统计全文词频
class Clustering_analysis():
    
    def __init__(self, weibo_path, freq_path, word_path, topK =10, topics_count = 3, ottopK=5):
        self.path = weibo_path
        
        #逆向词频文件
        self.freqpath = freq_path
        
        #去掉其他地名和机场
        self.wordpath = word_path
        
        #全文词频
        self.allwords = []
        
        #全文句子，strings形式
        self.allsentence = []
        
        #句子词list形式
        self.sentencelist = []
        
        #Feature Vector 组合
        self.keywords = []
        
        #时间戳
        self.time_flag= []
        
        self.weibo_count = 0
        
        #每个文本取权重最大的关键字数量
        self.topK = topK
        
        #分成多少类
        self.topics_count = topics_count
        
        #输出多少关键词
        self.outputtopk = ottopK
        
        #极端情况微博 index hash list
        self.index_list = []
        
    def get_text_weibo(self):
        #file_address = folder+"\\"+weibo_file
        f = open(self.path, 'r')
        weibo_lines = f.readlines()
        #weibo_sentence = []
        #weibo_all_words = []
        for item_num in xrange(min(len(weibo_lines), 10000)):
            item = weibo_lines[item_num].decode('utf-8')
            item = item.split()
            if (len(item) >= 4) and (u'延误' in weibo_lines[item_num].decode('utf-8')):
            #if (len(item) >= 4):    
                weibo_text =  item[3]
                #去除数字和其他标点符号
                weibo_text = "".join([i for i in weibo_text if not (i.isdigit() or i in u",.@:#&【】;（），。、：！/\!_转发理由微博")])
                seg_list = jieba.cut(weibo_text, cut_all=False)
                sentence =  " ".join(seg_list)
                self.sentencelist.append(sentence.split(" "))
                self.allwords= self.allwords + sentence.split(" ")
                self.allsentence.append(sentence)
                self.time_flag.append(item[2])
        #print "len:", len(weibo_all_words)
        self.weibo_count = len(self.allsentence)
        return self.allwords,  self.allsentence 
    
    #统计全文词频并保存
    def text_freq(self):
        weibo_all_words = nltk.Text(self.allwords)
        total = len(weibo_all_words)
        #固定搭配词组
        #print weibo_all_words.collocations()
        
        fdist = FreqDist(weibo_all_words)
        result_list = []
        for item in sorted(fdist.keys()):
            result_list.append([item, fdist[item]])
        result_list.sort(key=lambda x:x[1])
        
        #f = open("freq_weibo.txt",'w')
        f = open(self.freqpath,'w')
        for item in result_list:
            #print item[0], (1.0*item[1]/total)*10
            f.write(item[0].encode('utf-8')+ ' ' + str((100.0*item[1]/total)) +'\n')
        f.close()
        return 0
     
    #sikit learn 计算TFIDF
    def sikit_TF_IDF(self):
        vectorizer = CountVectorizer(min_df=1)
        transformer = TfidfTransformer()
        X = vectorizer.fit_transform(self.allwords)
        tfidf = transformer.fit_transform(X)
        #word = vectorizer.get_feature_names()
        word = [u'下雪',u"下雨",u"大雨",u"延误",u"首都机场",u"预警",u"雷暴",u"大雾",u"雾霾",u"大雪",
            u'首都',u'除雪', u'除冰', u'降水',u'降水量',u'降雨',u'降雪',u'首都机场' ,u'落雨',
            u'风力',u'预测',u'预告',u'雷暴',u'雷阵雨',u'雷雨',u'雨加雪',u'阵雨',u'较大', u'转中雪',
            u'较强',u'较晚',u'阵雪',u'阴有小雨',u'转阴',u'温度',u'阴转多云',u'阴转晴',u'阴间多云'  
            u'阴天', u'最低气温', u'强冷空气',u'强势',u'强大',u'强对流', u'强降水', u'强降雨',u'强震',
            u'多云到阴',u'多云转晴',u'多云转阴',u'多云间阴',u'最低温度',u'阵风',u'雨势',u'雨天',u'雨夹雪',
            u'雨强', u'雨滴',u'雨量',u'西风',u'西北风',u'西南风',u'东北风',u'东南风',
            u'南风',u'北风',u'东风',u'偏北风',u'偏南',u'偏南风',u'偏向',u'偏西风']
        
        for i, item in enumerate(word):
            print i, item
        weight = tfidf.toarray()
        for i in range(len(weight)):
            print u"-------这里输出第",i,u"类文本的词语tf-idf权重------"  
            for j in range(len(word)):  
                print word[j],weight[i][j] 
        return 0
    
    #jieba 计算TF_IDF
    def jieba_TF_IDF(self):
        #jieba.analyse.set_idf_path("E:\\eclipse_workspace\\weibo_keywords\\freq_weibo.txt")
        jieba.analyse.set_idf_path(self.freqpath)
        #f = open('result.txt','w')
        for i, item in enumerate(self.allsentence):
            tags = jieba.analyse.extract_tags(item, topK=self.topK, withWeight=True)    
            #f.write( "第"+ str(i) + "句关键字情况" + '\n')
            for tag in tags:
                #save_string = "tag:"+ tag[0].encode('utf-8') +' ' + "weight:"+ str(tag[1]) +'\n'
                #f.write(save_string)
                
                #print tag[0],
                self.keywords.append(tag[0])
            #print " "
        #f.close()
        return 0
    
    #lda聚类分析
    def lda_cluster(self):
        self.keywords= list(set(self.keywords))
        W_matrix = np.zeros(( self.weibo_count, len(self.keywords)), dtype = int)
        for rows in xrange(self.weibo_count):
            for cols in xrange(len(self.keywords)):
                if self.keywords[cols] in self.allsentence[rows]:
                    #print self.keywords[cols]
                    #print self.allsentence[rows]
                    W_matrix[rows][cols] =1
                    #print W_matrix[rows][cols]
        
        #sikit-learn LDA
        model = lda.LDA(n_topics= self.topics_count, n_iter=150, random_state= 1) 
        model.fit(W_matrix)
        topic_word = model.topic_word_
        #输出的关键词数量
        n_top_word = self.outputtopk
        for i,  topic_dist in enumerate(topic_word):
            topic_words = np.array(self.keywords)[np.argsort(topic_dist)][:-n_top_word:-1]
            print i, ' '.join(topic_words)
        
        doc_topic = model.doc_topic_
        
        #选取第0类和第3类微博文本
        for i in xrange(len(self.allsentence)):
            if (doc_topic[i].argmax() == 0 or doc_topic[i].argmax() == 3):
                self.index_list.append(i)
    
    def Weather_Analysis(self):
        
        f= open(self.wordpath,'r')
        word_all = f.readlines()
        word_list = []
        for item in word_all:
            item = item.split()
            word_list.append(item[0].decode('utf-8'))
        
        #排除其他影响词汇
        index_list = []
        for i in self.index_list:
            a = list(set(self.sentencelist[i]) & set(word_list))
            if len(a)==0: 
                index_list.append(i)
        self.index_list = index_list
        
        print "list_length: ",len(self.index_list)
        
        Weather_keyword = [u'雷' , u'冰'  , u'风'  , u'雾' ,  u'雨', u'雪']
        
        #输出极端天气情况
        for i in self.index_list:
            temp_list = []
            for item in Weather_keyword:
                if item in self.allsentence[i]:
                    temp_list.append(item)
            if  len(temp_list) != 0:
                for item in temp_list:
                    print item,
                print self.time_flag[i]
                #print self.allsentence[i]
            
      
    def allrun(self):
        self.get_text_weibo()
        self.text_freq()
        self.jieba_TF_IDF()
        self.lda_cluster()
        self.Weather_Analysis()
    
if __name__ =="__main__":
    weibo_file = u"首都机场weibo"
    word_file = u"Airport_dict(Beijing).txt"
    #file_address = os.path.dirname(os.path.abspath(__file__))
    freq_path = rootPath + '\\result\\' + weibo_file+"freq.txt"
    weibo_path = rootPath + '\\result\\' + weibo_file
    word_path = rootPath + '\\Word_Dict_Parse\\'+word_file
    weibo_cluster = Clustering_analysis(weibo_path, freq_path, word_path, topics_count = 4, ottopK=7)
    weibo_cluster.allrun()
    print "all_finish"
