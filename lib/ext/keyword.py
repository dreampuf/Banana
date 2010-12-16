#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import sys, logging
reload(sys)
sys.setdefaultencoding('utf-8')
import os
from django.utils import simplejson as json
CUT_LENGTH=8
RANK_LIMIT=1.5

dbfile = open(os.path.join("lib", "ext", "dict.txt"))
dict_db=json.read(dbfile.read())

stop_word=set(u""",，.。“”"'?？!！[]()［］（） 　:;：；/\\{}＼／｛｝\r\n\t《》、*&#…-abcdefghijklmnopqrstuvwxyz1234567890与的我个已是了着有可要和下这不任""")

def __init__():
    dict=open(u"词库.dic")
    for i in dict:
        i=i.strip().split('	')
        #print i[0],i[1]
        dict_db[i[0]]=str(float(i[1])/100054692)
    dict_db.sync()

class Keyword(object):
    def __init__(self,pre,next):
        self.__count=0
        self.__pre=set()
        self.__next=set()
        self.add(pre,next)

    def add(self,pre,next):
        self.__count+=1
        self.__pre.add(pre)
        self.__next.add(next)
        
    def valid(self):
        if ( len(self.__pre)==1 and self.__pre!=set([''])) or (len(self.__next)==1 and self.__next!=set(['']) )or self.__count==1:
            return False

        #print "self.__pre",self.__pre
        #for i in self.__next:
            #print "self.__next",i
        return True
    def __int__(self):
        return self.__count
    def __str__(self):
        return str(self.__count)
        
class KeywordManager(object):
    def __init__(self):
        self.list=[]
        self.dict={}

    def __add_item(self,pre,word,next):
        if self.dict.has_key(word):
            self.dict[word].add(pre,next)
        else:
            self.dict[word]=Keyword(pre,next)

    def add(self,char):
        self.list.append(char)

    def sync(self):
        length=len(self.list)
        for i in xrange(2,CUT_LENGTH):
            pre=''
            if length>=i:
                for j in xrange(length-i):
                    self.__add_item(pre,''.join(self.list[j:j+i]),self.list[j+1])
                    pre=self.list[j]
                self.__add_item(pre,''.join(self.list[length-i:]),u"")
            else:
                break
            
        self.list=[]


def keyword(input):
    word={}
    keyword_manager=KeywordManager()
    total_len=0
    input = input.replace("\r", "").split("\n")
    for i in input:
        i=i.strip().decode('utf-8')
        total_len+=len(i)
        for j in i:
            if j in stop_word:
                keyword_manager.sync()
            else:
                keyword_manager.add(j)
    keyword_manager.sync()
    word_list={}
    for k,v in keyword_manager.dict.iteritems():
        if v.valid():
            word_list[k]=float(int(v))
    trash=set()

    def add(word):
        if word in word_list:
            if v/word_list[word]>0.618:
                trash.add(word)
            else:
                return False
        return True

    word_list_finally=[]
    for k,v in word_list.iteritems():
        if len(k)>2:
            if add(k[1:]) and add(k[:-1]):
                if k not in trash:
                    word_list_finally.append((k,v))
        elif k not in trash:
            word_list_finally.append((k,v))

    word_list2=[]
    no_login_word_list=[]
    from cmath import log10
    for i in word_list_finally:
        if i[0].encode('utf-8') in dict_db:
            rank=log10(i[1]/float(dict_db[i[0].encode('utf-8')])).real
            word_list2.append(
                    (
                        i[0],
                        rank
                    )
                 )
        else:
            rank=i[1]*log10(len(i[0])).real
            if rank>1.7:
                no_login_word_list.append((i[0],rank))
    sorter=lambda x,y:-1 if x[1]>y[1] else 0 if x[1]==y[1] else 1
    word_list2.sort(sorter)
    no_login_word_list.sort(sorter)
    keyword_no=total_len/300+3
    result=word_list2[:keyword_no]+no_login_word_list
    result.sort(sorter)
    return [i[0] for i in result]

if __name__=="__main__1":
    #__init__()
    input=open(u'马化腾：差点收购YouTube.txt')
    #input=open(u'f2.txt')
    word_list=keyword(input)
    for i in word_list:
        print i
    #raw_input("finished")
