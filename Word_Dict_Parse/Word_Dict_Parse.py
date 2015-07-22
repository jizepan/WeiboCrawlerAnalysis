# _*_coding=utf-8_*_

import jieba

fo= open(u"机场.txt","r")
word_list = []
a = fo.readlines()

for item in a:
    seg_list = jieba.cut(item, cut_all=False)
    sentence =  " ".join(seg_list)
    if u"北京" not in sentence:
        temp_list = sentence.split()
        for item_dummy in temp_list:
            word_list.append(item_dummy)
word_set = list(set(word_list))
print word_set

fw= open("Airport_dict(Beijing).txt","w")
for item in word_set:
    if len(item)>1:
        fw.write(item.encode('utf-8')+" "+"\n")
fw.close()
