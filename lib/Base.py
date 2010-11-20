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

import cgi
import datetime
import wsgiref.handlers
from functools import wraps

from google.appengine.ext import db
from google.appengine.ext import webapp
from google.appengine.api import memcache

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

class BaseRequestHandler(webapp.RequestHandler):
    '''Base Web Request Class'''
    pass

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


