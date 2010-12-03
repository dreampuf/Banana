#-------------------------------------------------------------------------------
# Name:        Base
# Author:      soddy
# Created:     09/11/2010
# Copyright:   (c) soddy 2010
# Email:       soddyque@gmail.com
#-------------------------------------------------------------------------------
#!/usr/bin/env python
# -*- coding: UTF-8 -*-
#

import cgi, os, logging, sys
import datetime
import wsgiref.handlers
from functools import wraps

from google.appengine.ext import db
from google.appengine.ext import webapp
from google.appengine.api import memcache
from google.appengine.ext.webapp import template

from ext.sessions import Session
import Model

from jinja2 import Environment, Template
from jinja2.loaders import FileSystemLoader

reload(sys)
sys.setdefaultencoding("utf-8")
def requires_admin(method):
	@wraps(method)
	def wrapper(self, *args, **kwargs):
		if not self.is_login:
			self.redirect(users.create_login_url(self.request.uri))
			return
		else:
			return method(self, *args, **kwargs)
	return wrapper

#only ajax methed allowed
def ajaxonly(method):
    @wraps(method)
    def wrapper(self, *args, **kwargs):
        if not self.request.headers["X-Requested-With"]=="XMLHttpRequest":
            self.response.set_status(404)
        else:
            return method(self, *args, **kwargs)
    return wrapper

#only request from same host can passed
def hostonly(method):
    @wraps(method)
    def wrapper(self, *args, **kwargs):
        if  self.request.headers['Referer'].startswith(os.environ['HTTP_HOST'],7):
            return method(self, *args, **kwargs)
        else:
            self.response.set_status(404)
    return wrapper

def cache(key="",time=3600):
	def _decorate(method):
		def _wrapper(*args, **kwargs):
			request=args[0].request
			response=args[0].response
			skey=key+ request.path_qs
			#logging.info('skey:'+skey)
			html= memcache.get(skey)
			#arg[0] is BaseRequestHandler object

			if html:
				 logging.info('cache:'+skey)
				 response.last_modified =html[1]
				 ilen=len(html)
				 if ilen>=3:
					response.set_status(html[2])
				 if ilen>=4:
					for skey,value in html[3].items():
						response.headers[skey]=value
				 response.out.write(html[0])
			else:
				if 'last-modified' not in response.headers:
					response.last_modified = format_date(datetime.utcnow())

				method(*args, **kwargs)
				result=response.out.getvalue()
				status_code = response._Response__status[0]
				logging.debug("Cache:%s"%status_code)
				memcache.set(skey,(result,response.last_modified,status_code,response.headers),time)

		return _wrapper
	return _decorate

def idgen(start):
    start = start
    while True:
        yield start
        start = start + 1

def extrac(obj, filter=None):
    pros = dir(obj)
    isfilter = not filter == None
    result = {}
    for i in pros:
        if isfilter and i in filter:
            result[i] = getattr(obj, i)
    return result


class Event(object):
    _observers = {}
    def __init__(self):
        super(Event, self).__init__()

    @classmethod
    def register(cls, etype, observer):
        if not cls._observers.has_key(etype):
            cls._observers[etype] = []
        cls._observers[etype].append(observer)

    @classmethod
    def unregister(cls, etype, observer):
        if not cls._observers.has_key(etype):
            return
        cls._observers[etype].remove(observer)

    @classmethod
    def notify(cls, etype, *args, **kw):
        if cls._observers.has_key(etype):
            for observer in cls._observers:
                observer(*args, **kw)
class _ConfigProperty(Event):

    def __init__(self, name, default=None, useMemoryCache=True):
        self.name = "config_%s" % name
        self.default= default
        self.usememorycache = useMemoryCache

    def __get__(self, instance, klass):
        return Model.Setting.getValue(self.name, self.default, self.usememorycache)

    def __set__(self, instance, value):
        Model.Setting.setValue(self.name, value, self.usememorycache)

class Config(Event):
    domain = os.environ['HTTP_HOST']
    baseurl = "http://" + domain
    lang = "zh-cn"
    rootdir = os.path.split(os.path.abspath(sys.argv[0]))[0]
    version = "1.0"
    rss = "/rss"

##    title = Model.Setting.getValue("config_title", "Banana")
##    subtitle = Model.Setting.getValue("config_subtitle", "an other blog")
##    charset = Model.Setting.getValue("config_charset", "utf-8")
##    footer = Model.Setting.getValue("config_footer", "")
##    headlink = Model.Setting.getValue("config_headlink", ["/css/style.css", "/js/jquery-1.4.4.min.js"])

    title = _ConfigProperty("title", "Banana")
    subtitle = _ConfigProperty("subtitle", "an other blog",)
    charset = _ConfigProperty("charset", "utf-8")
    footer = _ConfigProperty("footer", "")
    headlink = _ConfigProperty("headlink", ["/css/style.css", "/js/jquery-1.4.4.min.js"])

##    _filter = ("title", "subtitle", "charset", "footer", "headlink")
    def __new__(cls, *args, **kw):
        if not hasattr(cls, "_instance"):
            orig = super(Config, cls)
            cls._instence = orig.__new__(cls, *args, **kw)
        return cls._instence

##    def __set__(self, attrname, value):
##        logging.info("WWWWWWset setting.%s:%s" % (attrname, value))
##        if hasattr(self, attrname) and attrname in _filter:
##            logging.info("set setting.%s:%s" % (attrname, value))
##            setattr(self, attrname, value)
##            Model.Setting.setValue("config_%s" % attrname, value)

Config = Config()

env = Environment(loader=FileSystemLoader(os.path.join("tpl")))

class BaseRequestHandler(webapp.RequestHandler, Event):
    '''Base Web Request Class'''
    AfterGenerateHeadlink = "AfterGenerateHeadlink"
    def __init__(self, *args, **kw):
        super(BaseRequestHandler, self).__init__(*args, **kw)

        headlink = [(os.path.splitext(i)[1][1:], i) for i in Config.headlink]

        self.notify(self.AfterGenerateHeadlink, headlink) #head元素事件
        self.data = { "baseurl" : Config.baseurl,
                      "charset" : Config.charset,
                      "blog_title" : Config.title,
                      "blog_subtitle" : Config.subtitle,
                      "blog_footer" : Config.footer,
                      "head_link": headlink,
                      }
        self.session= Session()

    def render(self, path, template_vals={}):
        self.data.update(template_vals)
        global env
        tpl = env.get_template(path)
        tmpl = tpl.render(self.data)
        self.response.out.write(tmpl)

    def q(self, key):
        return self.request.get(key)

    def redirect_self(self):
        self.redirect(self.request.url)

    def write(self, value):
        '''
        value : string
            the out of you want
        '''
        self.response.out.write(value)

class FrontRequestHandler(BaseRequestHandler):
    '''Front Web Request Class'''
    def __init__(self, *args, **kw):
        super(FrontRequestHandler, self).__init__(*args, **kw)
        self.data.update({"rss_url" : Config.rss,
                          "head_link" : [],
                          "blog_subtitle" : Config.subtitle})

class BackRequestHandler(BaseRequestHandler):
    '''Back Web Request Class'''
    AfterBackGenerateSitebar = "AfterBackGenerateSitebar"
    def __init__(self, *args, **kw):
        super(BackRequestHandler, self).__init__(*args, **kw)
        sitebar = {
                    "网站管理": [
                                ("基本设置", "/admin/config"),
                                ("用户管理", "/admin/user"),
                                ("附件管理", "/admin/attachments")
                                ],
                    "内容管理": [
                                ("文章管理", "/admin/post"),
                                ("分类管理", "/admin/category"),
                                ("标签管理", "/admin/tags"),
                                ("评论管理", "/admin/comments")
                                ]
                  }

        self.notify(self.AfterBackGenerateSitebar, sitebar) #发出边栏生成事件
        self.data.update({
                          "sitebar" : sitebar
                          })
        self.data["head_link"].append(("css", "/css/admin.css"))


class Memcache:
    @classmethod
    def get(cls, key):
        return memcache.get(key)

    @classmethod
    def set(cls, key, value, time=0):
        memcache.set(key, value, time)

    @classmethod
    def delete(cls, key, seconds=0):
        memcache.delete(key, seconds)

    @classmethod
    def incr(cls, key, delta=1):
        memcache.incr(key, delta)

    @classmethod
    def decr(cls, key, delta=1):
        memcache.decr(key, delta)

    @classmethod
    def flush_all(cls):
        memcache.flush_all()

    @classmethod
    def get_stats(cls):
        return memcache.get_stats()


class HtmlHelper(object):
    ''' HTML生成工具类 '''
    tpl = Template('<{{ tagname }} {{ others }}{% if noText %} />{% else %}>{{ text }}</{{ tagname }}>{% endif %}')
    emptytags = list("input isindex base meta link nextid range img br hr frame wbr basefont spacer audioscope area param keygen col limittext spot tab over right left choose atop and of".split(" "))

    @classmethod
    def For(cls, tagname, *args, **kw):
        '''
        tagname:string
            标签名称
        args:dict
            特殊字符的键值方法,如果有某些python关键字作为属性则无法直接使用名称参数.exp: {"for":"somename"} .
        text:string
            文本域
        '''
        for i in args:
            kw.update(i)
        kw = dict([(k, v) for (k, v) in kw.items() if v != ""])
        tagname = tagname.lower()
        noText = tagname.lower() in cls.emptytags

        if kw.has_key("text"):
            '''
            如果存在text,则根据:
                1.如果是list或者tuple则每项之间加换行符,如果tagname为select则输出option子元素
                2.如如果是dict则按照key:value输出并加换行符,如果tagname为select则输出option子元素并指明value和text
                3.否则则输出字符串
            '''
            text = kw.pop("text")
            if isinstance(text, (list, tuple)):
                if tagname == "select":
                    text = "".join(['<option value="%s">%s</option>' % (i, i) for i in text])
                else:
                    text = "\n".join(text)
            elif isinstance(text, dict):
                if tagname == "select":
                    text = "\n".join(['<option value="%s">%s</option>' % (key, val) for (key, val) in text.items()])
                else:
                    text = "\n".join(["%s:%s" % (key, val) for (key, val) in text.items()])
        else:
            text = ""

        others = " ".join(['%s="%s"'%(key, value) for key, value in kw.items()])
        return cls.tpl.render({ "tagname" : tagname,
                            "noText": noText,
                            "text": text,
                            "others": others })
    @classmethod
    def ForTable(cls, content):
        '''转换为HTML表单'''
        htmls = '<table width="100%%" class="formtabel" style="padding:0px; margin:1px;" cellspacing="0" cellpadding="0"> \
                 <tbody>%s</tbody></table>'
        trs = []
        for i in content:

##            if isinstance(i, dict) and i.has_key("style") and i.has_key("items"):
##                #每行单独的样式
##                trs.append('<tr style="%s">' % i.pop(style))
##                i = i.pop("items")

            itemlen = len(i)
            assert itemlen > 0
            width = int(100 / itemlen)

            for j in i:
                if isinstance(j, (str, unicode)):
                    trs.append("<td>%s</td>" % j)
                    continue

                if  j.has_key("width"):
                    jwidth = j.pop("width")
                    if not (jwidth.endswith("%") or jwidth.endswith("px")):
                        jwidth = "%spx" % jwidth
                else:
                    jwidth = "%s%%" % width

                tagname = j.pop("tagname")
                cls.For(tagname, j)
                trs.append('<td style="width:%s">%s</td>' % (jwidth, cls.For(tagename, j)))
            trs.append("</tr>")
        htmls = htmls % "".join(trs)
        return htmls

    @classmethod
    def ForA(cls, text, href="", klass="", **kw):
        return cls.For("a", {"class":klass}, text=text,href=href, **kw)

    @classmethod
    def ForBr(cls, **kw):
        return cls.For("br", **kw)
    @classmethod
    def ForLabel(cls, text="", forname="", **kw):
        return cls.For("lablel", {"for":forname, "text":text+":"}, **kw)
    @classmethod
    def ForInput(cls, name, value="", type="text", **kw):
        return cls.For("input", type=type, name=name, value=value, **kw)

    @classmethod
    def ForInputHidden(cls, name, value="", **kw):
        return cls.For("input", type="hidden", name=name, value=value, **kw)

    @classmethod
    def ForInputLabel(cls, text, name="", type="text", value="", middle="", **kw):
        return "%s%s%s" % (cls.ForLabel(text, name), middle, cls.ForInput(name, type, value, **kw))

    @classmethod
    def ForInputButton(cls, value, **kw):
        return cls.For("input", type="button", value=value, **kw)
    @classmethod
    def ForInputSubmit(cls, value, **kw):
        return cls.For("input", type="submit", value=value, **kw)

    @classmethod
    def ForTextArea(cls, name="", text="", **kw):
        return cls.For("textarea", name=name, text=text, **kw)

    @classmethod
    def ForTextAreaLabel(cls, text, name="", value="", **kw):
        return "%s%s%s" % (cls.ForLabel(text, name), cls.ForBr(), cls.For("textarea", name=name, text=value, **kw))

    @classmethod
    def ForButton(cls, text, **kw):
        return cls.For("button", text=text, **kw)






