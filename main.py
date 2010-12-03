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

import cgi, sys, os
import datetime
import wsgiref.handlers

sys.path.append("lib")

from google.appengine.ext import db
from google.appengine.ext import webapp

from lib import Base, Model, Admin, Front

class MainHandler(Base.FrontRequestHandler):
    def get(self):
        import random,time,string
        r = random.Random()
        start_time = time.clock()
        a = Model.User.all().get()

##        t = Model.Category(title="我的日记", url="myriji", description="7788", order=0).put()
##        Model.Category(title="我的周记", url="myweek", description="still7788", order=4).put()
##        Model.Category(title="我的月记", url="mymouth", description="andandand7788", order=2).put()
##        Model.Category(title="我的季记", url="bbasd", description="你好,谢谢,再见", order=3).put()
##        Model.Category(title="嘻嘻哈伊", url="ooxx", description="tata", order=1).put()
##        for i in range(r.randint(10, 20)):
##
####            t = Model.Attachment( filename="%s%s" % ("".join(r.sample(string.ascii_lowercase, 5)),i),
####                                  filetype="banana",
####                                  content=Model.toBlob(open(os.path.join("static", "images", "favicon.ico")).read()),
####                                  belong=a )
##            t.put()
##        t = Model.User.all().fetch(1000)
##        while len(t) > 0:
##            Model.db.delete(t)
##            t = Model.User.all().fetch(1000)

        self.write("Model.User.Cout = %s;counters = %s" % (Model.User.all().count(None), Model.User.total()))
        t = Model.Tag.fetch(1)
        self.write(" =====%s=======%s=========<br />" % (t.count, t.last))
        end_time = time.clock()
        diff = end_time - start_time
        self.write("<br />%s<br />" % diff)

##        t.delete()

##        self.write("%s   %s<br />" % (t.title, t.is_saved()))
##        self.write((t.__class__.__name__))

        start_time = time.clock()
        #self.write(Model.Tag.all().count(None))
        end_time = time.clock()
        diff = end_time - start_time
        self.write("<br />%s" % diff)

class TestHandler(Base.FrontRequestHandler):
    def get(self):
        self.data.update({ "title":"HHHHHHHHH",
                           "is_home" : True })
        self.render("index.html")

class InstallHandler(Base.FrontRequestHandler):
    def get(self):
        pass
    def post(self):
        pass

def main():
    application = webapp.WSGIApplication([
    ("^[/]?", MainHandler),
    ("^/a[/]?$", TestHandler ),
    ("^/attachments[/]?(.+)?$", Front.AttachmentsHandler),
    ("^/admin[/]?$", Admin.AdminMainHandler),
    ("^/admin/login[/]?$", Admin.AdminLogin),
    ("^/admin/config[/]?$", Admin.AdminConfigHandler),
    ("^/admin/user[/]?(.+)?$", Admin.AdminUserHandler),
    ("^/admin/attachments[/]?(.+)?$", Admin.AdminAttachmentHandler),
    ("^/admin/category[/]?(.+)?$", Admin.AdminCategoryHandler),
    ("^/admin/post[/]?(.+)?$", Admin.AdminPostHandler),
    ("^/admin/tags[/]?(.+)?$", Admin.AdminTagHandler),
    ("^/admin/comments[/]?(.+)?$", Admin.AdminCommentHandler),


    ], debug=True)
    wsgiref.handlers.CGIHandler().run(application)

if __name__ == '__main__':
    main()
