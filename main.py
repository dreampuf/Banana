#-------------------------------------------------------------------------------
# Name:        Main
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

from google.appengine.ext import db
from google.appengine.ext import webapp

from lib import Base, Model

class MainHandler(Base.BaseRequestHandler):
    def get(self):
        p = Model.Post.get_by_id(1)
##        p.put()
##        for i in range(5):
##            c = Model.Comment(belong=p, content="aasd%s" % i)
##            c.put()
        for c in p.comments:
            self.response.out.write(c.content + "<br />")

        a = [[6, 5, 4, 3, 2, 1], [6, 5, 4, 3, 2, 1], [6, 5, 4, 3, 2, 1], [6, 5, 4, 3, 2, 1], [6, 5, 4, 3, 2, 1], [6, 5, 4, 3, 2, 1]]
        b = Model.expand(a)
        self.response.out.write(b)

class InstallHandler(Base.BaseRequestHandler):
    def get(self):
        pass
    def post(self):
        pass

def main():
    application = webapp.WSGIApplication([
    ("/", MainHandler)
    ], debug=True)
    wsgiref.handlers.CGIHandler().run(application)

if __name__ == '__main__':
    main()
