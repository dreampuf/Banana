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
import pickle
from google.appengine.ext import db
from google.appengine.ext.db import Model as DBModel

def expand(ls):
    n = []
    for i in ls:
        if isinstance(i, list):
            n.append(expand(i))
        else:
            n.append(i)
    return n

class BaseModel(db.Model):
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

class Setting(BaseModel):
	name=db.StringProperty()
	value=db.TextProperty()

	@classmethod
	def getValue(cls,name,default=None):
		try:
			opt=Setting.get_by_key_name(name)
			return pickle.loads(str(opt.value))
		except:
			return default

	@classmethod
	def setValue(cls,name,value):
		opt=Setting.get_or_insert(name)
		opt.name=name
		opt.value=pickle.dumps(value)
		opt.put()

	@classmethod
	def remove(cls,name):
		opt= Setting.get_by_key_name(name)
		if opt:
			opt.delete()

class User(BaseModel):
    username = db.StringProperty()
    password = db.StringProperty()
    created = db.DateTimeProperty(auto_now_add=True)
    lastip = db.StringProperty()
    lastlogin = db.DateTimeProperty(auto_now=True)

class Category(BaseModel):
    title = db.StringProperty()
    description = db.StringProperty()
    order = db.IntegerProperty(default=0)

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
    filetype = db.StringProperty()
    content = db.BlobProperty()

    def setContent(self, val):
        self.content = db.Blob(val)









