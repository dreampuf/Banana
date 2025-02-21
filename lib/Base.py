#!/usr/bin/env python
# -*- coding: UTF-8 -*-
#-------------------------------------------------------------------------------
# Name:        Base
# Author:      soddy
# Created:     09/11/2010
# Copyright:   (c) soddy 2010
# Email:       soddyque@gmail.com
#-------------------------------------------------------------------------------
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
import Model, yui

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

def dump(obj):
    out = []
    out.append("%s:\n\n"%obj)
    for i in dir(obj):
        if i.startswith("_"):
            continue
        try:
            out.append("   %s:  %s\n" % (i, getattr(obj, i)))
        except:
            pass
    logging.info("".join(out))

def processurl(p):
    url = Config.posturl

    mapper = { "%category%": p.category.title,
               "%year%": p.created.year,
               "%month%": p.created.month,
               "%day%": p.created.day,
               "%title%": p.title,
               "%url%": p.url,
               "%author%": p.author.username }

    for key, val in mapper.items():
        if url.find(key) != -1:
            url = url.replace(key, str(val))

    p.realurl = url


def pinghub():
    data = urllib.urlencode({'hub.url': "%s/%s"%(Config.baseurl, Config.feed), 'hub.mode': 'publish'})
    rpcs = []
    for i in Config.hub:
        rpc = urlfetch.create_rpc()
        urlfetch.make_fetch_call(rpc, i)
        rpcs.append(rpc)
    for i in rpcs:
        i.wait()

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

ZERO_TIME_DELTA = datetime.timedelta(0)
class LocalTimezone(datetime.tzinfo):
	def utcoffset(self, dt):
		return datetime.timedelta(hours=Config.localtimezone)

	def dst(self, dt):
		return ZERO_TIME_DELTA

LOCAL_TIMEZONE = LocalTimezone()

class UTC(datetime.tzinfo):
	def utcoffset(self, dt):
		return ZERO_TIME_DELTA

	def dst(self, dt):
		return ZERO_TIME_DELTA
UTC = UTC()

def ParserTime(dtstr, format = "%Y/%m/%d %H:%M:%S"):
    return datetime.datetime.strptime(dtstr, format)

def ParserLocalTimeToUTC(dtstr, format = "%Y/%m/%d %H:%M:%S"):
    return ParserTime(dtstr, format).replace(tzinfo=LOCAL_TIMEZONE).astimezone(UTC) \
                .replace(tzinfo=None) #fix in Google Engine App


def LocalToUTC(dt):
    if dt.tzinfo:
        dt.replace(tzinfo=None)
    return dt.replace(tzinfo=LOCAL_TIMEZONE).astimezone(UTC)

def UTCtoLocal(dt):
    if dt.tzinfo:
        dt.replace(tzinfo=None)
    return dt.replace(tzinfo=UTC).astimezone(LOCAL_TIMEZONE) \
                .replace(tzinfo=None) #fix in Google Engine App


class CommentStatus(object):
    DISENABLE = "disenable"
    ENABLE = "enable"
    USERONLY = "useronly"

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
    lang = "zh-CN"
    rootdir = os.path.split(os.path.abspath(sys.argv[0]))[0]
    version = "1.0"

    domain = _ConfigProperty("domain", os.environ['HTTP_HOST'])
    #baseurl = "http://" + domain

    localtimezone = _ConfigProperty("localtimezone", 8)
    title = _ConfigProperty("title", "Banana")
    subtitle = _ConfigProperty("subtitle", "an other blog")
    author = _ConfigProperty("author", "Banana")
    charset = _ConfigProperty("charset", "utf-8")
    feed = _ConfigProperty("feed", "feed")
    feednumber = _ConfigProperty("feednumber", 20)
    feedshowpre = _ConfigProperty("feedshowpre", False)
    hub = _ConfigProperty("hub", ["http://pubsubhubbub.appspot.com/"])
    indexnumber = _ConfigProperty("indexnumber", 20)
    indexshowpre = _ConfigProperty("indexshowpre", True)
    footer = _ConfigProperty("footer", "")
    headlink = _ConfigProperty("headlink", ["/css/style.css", "/js/common.js"])
    posturl = _ConfigProperty("posturl", "%year%/%month%/%url%.html")
    commentstatus = _ConfigProperty("commentstatus", CommentStatus.ENABLE)
    commentneedcheck = _ConfigProperty("commentneedcheck", False)

    recaptcha_public_key = _ConfigProperty("recaptcha_public_key",'6Le-a78SAAAAAPBtWkwwMmwsk21LWhA-WySPzY5o')
    recaptcha_private_key = _ConfigProperty("recaptcha_private_key", '6Le-a78SAAAAAPpK1K0hm5FuyOBU7KPJmJxxMjas')

    def __new__(cls, *args, **kw):
        if not hasattr(cls, "_instance"):
            orig = super(Config, cls)
            cls._instence = orig.__new__(cls, *args, **kw)
        return cls._instence

Config = Config()
Config.baseurl = "http://" + Config.domain

env = Environment(loader=FileSystemLoader(os.path.join("tpl")), trim_blocks=True)

class BaseRequestHandler(yui.RequestHandler, Event):
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
        self.set_content_type("text/html")

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

    def from_request(self, obj, fun=lambda x: x):
        #TODO
        '''update obj from self.request.parmas'''
        src = self.request.params
        for i in src.keys():
            if hasattr(obj, i):
                #logging.info("1")
                o = getattr(obj, i)
                if isinstance(o, int):
                    #logging.info("2")
                    setattr(obj, i, int(fun(o)))
                elif isinstance(o, (str, unicode)):
                    #logging.info("3")
                    setattr(obj, i, fun(o))
                else:
                    #logging.info("4")
                    setattr(obj, i, fun(o))
        #dump(obj)

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
        self.data.update({"feed_url" : Config.feed,
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
                                ("附件管理", "/admin/attachment")
                                ],
                    "内容管理": [
                                ("添加文章", "/admin/post/new"),
                                ("文章管理", "/admin/post"),
                                ("分类管理", "/admin/category"),
                                ("标签管理", "/admin/tag"),
                                ("评论管理", "/admin/comment")
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


class Plugin(Event):

    def __init__(self):
        super(Plugin, self).__init__()







class Theme(Event):
    def __init__(self):
        super(Theme, self).__init__()





