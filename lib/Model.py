#-------------------------------------------------------------------------------
# Name:        Model
# Author:      soddy
# Created:     09/11/2010
# Copyright:   (c) soddy 2010
# Email:       soddyque@gmail.com
#-------------------------------------------------------------------------------
#!/usr/bin/env python
# -*- coding: UTF-8 -*-
#
import pickle, logging
from google.appengine.ext import db
from google.appengine.ext.db import Model as DBModel
from google.appengine.api import memcache

def expand(ls, n = []):
    for i in ls:
        if isinstance(i, list):
            expand(i, n)
        else:
            n.append(i)
    return n

def toBlob(val):
    return db.Blob(val)

_settingcache = {}

class Setting(DBModel):
    name=db.StringProperty()
    value=db.TextProperty()

    @classmethod
    def getValue(cls,name,default=None, useMemoryCache=True):
        '''
        name:string
            键
        default:obj
            默认值,如果不存在该设置,则返回默认值
        useMemoryCache:boolean
            是否使用全局缓存.该缓存在多个python实例不共享
        '''
        global _settingcache
        if useMemoryCache and _settingcache.has_key(name) :
            return _settingcache[name]
        else:
            n = memcache.get("setting.%s" % name)
            if n != None:
                if useMemoryCache:
                    _settingcache[name] = n
                return n
        try:
            opt=Setting.get_by_key_name(name)
            result = pickle.loads(str(opt.value))

            if useMemoryCache:
                _settingcache[name] = result
            memcache.set("setting.%s" % name, result, 0)
            return result
        except:
            return default

    @classmethod
    def setValue(cls,name,value, useMemoryCache=True):
        '''
        name:string
            键
        value:obj
            值
        useMemoryCache:boolean
            是否使用全局缓存.该缓存在多个python实例不共享
        '''
        if useMemoryCache:
            global _settingcache
            _settingcache[name] = value

        memcache.set("setting.%s" % name, value, 0)

        opt=Setting.get_or_insert(name)
        opt.name=name
        opt.value=pickle.dumps(value)
        opt.put()

    @classmethod
    def remove(cls,name):
        global _settingcache
        if _settingcache.has_key(name):
            del _settingcache[name]
        memcache.delete("setting.%s" % name, 0)
        opt= Setting.get_by_key_name(name)
        if opt:
            opt.delete()

class _Pager(object):
    def __init__(self, data, count, index, last):
        self.data = data
        self.count = count
        self.index = index
        self.prev = index - 1
        self.next = (index + 1 > last) and 0 or (index + 1)
        self.last = last

class BaseModel(DBModel):
    def __init__(self, parent=None, key_name=None, _app=None, **kwds):
        self.__isdirty = False
        DBModel.__init__(self, parent=None, key_name=None, _app=None, **kwds)

    def __setattr__(self,attrname,value):
        """
        DataStore api stores all prop values say "email" is stored in "_email" so
        we intercept the set attribute, see if it has changed, then check for an
        onchanged method for that property to call
        """
        if (attrname.find('_') != 0):
            if hasattr(self,'_' + attrname):
                curval = getattr(self,'_' + attrname)
                if curval != value:
                    self.__isdirty = True
                    if hasattr(self,attrname + '_onchange'):
                        getattr(self,attrname + '_onchange')(curval,value)
        DBModel.__setattr__(self,attrname,value)

    def put(self, **kw):
        if not self.is_saved():
            tname = "tablecounter_%s" % (self.__class__.__name__ , )
            tval = Setting.getValue(tname, useMemoryCache=False)
            if tval == None:
                tval = self.__class__.all().count(None)
            Setting.setValue(tname, tval + 1, False)
        super(BaseModel, self).put(**kw)

    def delete(self, **kw):
        if self.is_saved():
            tname = "tablecounter_%s" % self.__class__.__name__
            tval = Setting.getValue(tname, useMemoryCache=False)
            if tval == None:
                tval = self.__class__.all().count(None)
            Setting.setValue(tname, tval - 1, False)
        super(BaseModel, self).delete(**kw)

    @classmethod
    def fetch(cls, p, plen = 20):
        #limit, offset=0, **kwargs
        total = cls.total()
        n = total / plen
        if total % plen != 0:
            n = n + 1
        #logging.info(n)
        if p < 0 or p > n:
            p = 1
        offset = (p - 1) * plen
        results = cls.all().fetch(plen, offset)
        return _Pager(results, total, p, n)

    @classmethod
    def total(cls):
        tname = "tablecounter_%s" % cls.__name__
        tval = Setting.getValue(tname, useMemoryCache=False)
        if tval == None:
            logging.info("beLongtime")
            tval = cls.all().count(None)
            Setting.setValue(tname, tval, False)
        return tval




class User(BaseModel):
    username = db.StringProperty()
    password = db.StringProperty()
    created = db.DateTimeProperty(auto_now_add=True)
    lastip = db.StringProperty()
    lastlogin = db.DateTimeProperty(auto_now=True)

    email = db.StringProperty()

class Category(BaseModel):
    title = db.StringProperty()
    description = db.StringProperty()
    order = db.IntegerProperty(default=0)
    url = db.StringProperty()

class Tag(BaseModel):
    title = db.StringProperty()
    description = db.StringProperty()

    @property
    def posts(self):
        return [i.post for i in self.__posts]

class Post(BaseModel):
    category = db.ReferenceProperty(Category, collection_name="posts")
    author = db.ReferenceProperty(User, collection_name="posts")
    title = db.StringProperty()
    created = db.DateTimeProperty(auto_now=True)
    url = db.StringProperty()
    content = db.TextProperty()
    precontent = db.TextProperty()

    @property
    def tags(self):
        return [i.tag for i in self.__tags]

class tags_posts(BaseModel):
    tag = db.ReferenceProperty(Tag, collection_name="__posts")
    post = db.ReferenceProperty(Post, collection_name="__tags")

class Comment(BaseModel):
    belong = db.ReferenceProperty(Post, collection_name="comments")
    author = db.ReferenceProperty(User, collection_name="comments")
    re = db.SelfReferenceProperty(collection_name="children")
    content = db.TextProperty()
    created = db.DateTimeProperty(auto_now_add=True)
    ip = db.StringProperty()
    website = db.LinkProperty()
    email = db.EmailProperty()

    def setWebsite(self, val):
        self.website = db.Link(val)

    def setEmail(self, val):
        self.email = db.Email(val)

class Attachment(BaseModel):
    beuse = db.ReferenceProperty(Post, collection_name="attachments")
    belong = db.ReferenceProperty(User, collection_name="attachments")

    filename = db.StringProperty()
    filetype = db.StringProperty()
    content = db.BlobProperty()

    @classmethod
    def toContent(cls, val):
        return db.Blob(val)









