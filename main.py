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


        self.write("Model.User.Cout = %s;counters = %s" % (Model.User.all().count(None), Model.User.total()))
        #t = Model.Tag.fetch(1)
        #self.write(" =====%s=======%s=========<br />" % (t.count, t.last))
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
        import string, random

##        a = Model.User.all().fetch(5)
##        p = Model.Post.all().fetch(5)
##        for i in range(r.randint(5, 20)):
##            c = Model.Comment()
##            c.author = a[r.randint(0, 4)]
##            c.belong = p[r.randint(0, 4)]
##            c.content = "".join(r.sample(string.uppercase * 5, r.randint(50, 130)))
##            c.ip = "%s.%s.%s.%s" % (r.randint(0,255), r.randint(0,255), r.randint(0,255), r.randint(0,255))
##            c.setEmail("%s@%s.%s"%("".join(r.sample(string.lowercase, r.randint(3, 10))),
##                                   "".join(r.sample(string.lowercase, r.randint(2, 4))),
##                                   "".join(r.sample(string.lowercase, r.randint(2, 4)))))
##            c.setWebsite("%s://%s.%s.%s" % (["http", "https"][r.randint(0, 1)],
##                                               "".join(r.sample(string.lowercase, r.randint(2, 4))),
##                                               "".join(r.sample(string.lowercase, r.randint(2, 8))),
##                                               "".join(r.sample(string.lowercase, r.randint(2, 4)))))
##            c.put()
##        clen = Model.Category.total()
##        cl = Model.Category.all().fetch(clen)
##
##        for i in range(5):
##            atag = Model.Tag()
##            atag.title = "".join(r.sample(string.uppercase, 3))
##            atag.description = "".join(r.sample(string.lowercase, 5))
##            atag.put()
##
##        tlen = Model.Tag.all().count(None)
##        tl = Model.Tag.all().fetch(tlen)
##
##        for i in range(5):
##            apost = Model.Post()
##            apost.category = cl[r.randint(0, clen - 1)]
##            apost.author = a[r.randint(0, 4)]
##            apost.title = "".join(r.sample(string.ascii_lowercase, r.randint(3, 5)))
##            apost.content = "".join(r.sample(string.ascii_lowercase, len(string.ascii_lowercase)))
##            apost.precontent = "".join(r.sample(string.ascii_lowercase, len(string.ascii_lowercase)/2))
##            apost.url = "".join(r.sample(["Hello", "Hi", "Thanks", "PP", "need", "ok", "case", "jump", "cci", "wourld", "html", "javascript", "tt"], 5))
##            apost.put()
##
##            for j in range(r.randint(0,3)):
##                posttag = Model.tags_posts()
##                posttag.tag = tl[r.randint(0, tlen - 1)]
##                posttag.post = apost
##                posttag.put()
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

        self.write("OK")

import string, random, datetime, time
longstring = string.lowercase * 1000
class DataProcessHandler(Base.FrontRequestHandler):
    def getRstr(self, low, uper):
        times = uper / 26
        if times < 1:
            times = 1
        return "".join(random.sample(longstring, random.randrange(low, uper)))

    def getRip(self):
        return "%s.%s.%s.%s" % (random.randint(0,255), random.randint(0,255), random.randint(0,255), random.randint(0,255))

    def getRemail(self):
        return "%s@%s.%s"%("".join(random.sample(string.lowercase, random.randint(3, 10))),
                                   "".join(random.sample(string.lowercase, random.randint(2, 4))),
                                   "".join(random.sample(string.lowercase, random.randint(2, 4))))

    def getRurl(self):
        return "%s://%s.%s.%s" % (["http", "https"][random.randint(0, 1)],
                                   "".join(random.sample(string.lowercase, random.randint(2, 4))),
                                   "".join(random.sample(string.lowercase, random.randint(2, 8))),
                                   "".join(random.sample(string.lowercase, random.randint(2, 4))))
    def getRtime(self):
        return datetime.datetime(  2010,
                                   random.randrange(1, 12),
                                   random.randrange(1, 29),
                                   random.randrange(1, 24),
                                   random.randrange(1, 60),
                                   random.randrange(1, 60))

    def get(self, slug=None):
        htmls = '''<html><script src="/js/jquery-1.4.4.min.js"></script><body>
<script type="text/javascript">
$(function(){
    $("#clearbtn").click(function(){
        $.ajax({
           type: "DELETE",
           url: "/init",
           success: function(msg){
             alert( msg );
           }
        });
    });
    $("#initbtn").click(function(){
        $.ajax({
           type: "POST",
           url: "/init",
           success: function(msg){
             alert( msg );
           }
        });
    });
});
</script>
<form method="DELETE" ><input id="clearbtn" type="button" value="清空" /></form>
<form method="POST" ><input id="initbtn" type="button" value="初始化所有数据" /></form>
</body></html>'''
        self.write(htmls)

    def post(self, slug=None):
        start_time = time.clock()
        #Init User
        for i in range(random.randint(5, 40)):
            a = Model.User()
            a.username = self.getRstr(2, 7)
            a.password = self.getRstr(3, 8)
            a.lastip = self.getRip()
            a.created = self.getRtime()
            a.lastlogin = self.getRtime()
            a.setEmail(self.getRemail())
            a.put()
        users = Model.User.all().fetch(1000)
        ulen = len(users)

        #Init Category
        for i in range(random.randrange(30)):
            c = Model.Category()
            c.title = self.getRstr(2, 5)
            c.url = self.getRstr(2, 8)
            c.description = self.getRstr(10, 20)
            c.order = random.randrange(5)
            c.put()
        categorys = Model.Category.all().fetch(1000)
        clen = len(categorys)

        #Init Tag
        for i in range(random.randrange(40)):
            t = Model.Tag()
            t.title = self.getRstr(1, 5).upper()
            t.description = self.getRstr(10, 20)
            t.put()
        tags = Model.Tag.all().fetch(1000)
        tlen = len(tags)

        #Init Post
        for i in range(random.randrange(100)):
            a = Model.Post()
            a.category = categorys[random.randrange(clen)]
            a.author = users[random.randrange(ulen)]
            a.title = self.getRstr(3, 15)
            a.content = self.getRstr(50, 200)
            a.precontent= self.getRstr(20, 70)
            a.url = self.getRstr(3, 10)
            Base.processurl(a)
            a.views= random.randrange(110)
            a.put()

            #Init tags_post
            hastag = []
            for j in range(random.randrange(4)):
                t = tags[random.randrange(tlen)]
                if t in hastag:
                    continue
                else:
                    hastag.append(t)
                tp = Model.tags_posts()
                tp.tag = t
                tp.post = a
                tp.put()
        posts = Model.Post.all().fetch(1000)
        plen = len(posts)

        #Init Comment
        for i in range(random.randrange(20, 200)):
            cment = Model.Comment()
            cment.author = None if random.randrange(10) > 3 else users[random.randrange(ulen)]
            cment.belong = posts[random.randrange(plen)]
            cment.content = self.getRstr(10, 30)
            cment.created = self.getRtime()
            cment.nickname = self.getRstr(2, 10)
            cment.ip = self.getRip()
            cment.setWebsite(self.getRurl())
            cment.setEmail(self.getRemail())
            cment.put()

        #Init Attachment
        files = ( os.path.join("static", "images", "foot-wp.gif"),
                  os.path.join("static", "images", "layout2.png"),
                  os.path.join("static", "css", "admin.css"),
                  os.path.join("static", "js", "jquery-1.4.4.js") )
        for i in range(random.randrange(5, 25)):
            attach = Model.Attachment()
            attach.belong = users[random.randrange(ulen)]
            attach.beuse = posts[random.randrange(plen)]
            attach.created = self.getRtime()
            afile = files[random.randrange(4)]
            attach.filename = os.path.split(afile)[1]
            attach.filetype = os.path.splitext(attach.filename)[1][1:]
            attach.content = Model.toBlob(open(afile).read())
            attach.put()

        end_time = time.clock()
        self.write(end_time - start_time)


    def delete(self, slug=None):
        start_time = time.clock()
        tables = (Model.Attachment, Model.Category, Model.Comment, Model.Post, Model.Tag, Model.User, Model.tags_posts)
        for i in tables:
            while(i.all().count(None) > 0):
                items = i.all().fetch(1000)
                i.deletes(items)
        end_time = time.clock()
        self.write(end_time - start_time)



class InstallHandler(Base.FrontRequestHandler):
    def get(self):
        pass
    def post(self):
        pass

def main():
    application = webapp.WSGIApplication([
    ("^[/]?", Front.IndexHandler),
    ("^/page[/]?(.+)?$", Front.IndexHandler),
    ("^/attachments[/]?(.+)?$", Front.AttachmentsHandler),
    ("^/category[/]?(.+)?[/]?(.+)?$", Front.CategoryHandler),
    ("^/tag[/]?(.+)?$", Front.TagHandler),

    ("^/a[/]?$", TestHandler ),
    ("^/init[/]?$", DataProcessHandler),

    ("^/admin[/]?$", Admin.AdminMainHandler),
    ("^/admin/login[/]?$", Admin.AdminLogin),
    ("^/admin/config[/]?$", Admin.AdminConfigHandler),
    ("^/admin/user[/]?(.+)?$", Admin.AdminUserHandler),
    ("^/admin/attachment[/]?(.+)?$", Admin.AdminAttachmentHandler),
    ("^/admin/category[/]?(.+)?$", Admin.AdminCategoryHandler),
    ("^/admin/post[/]?(.+)?$", Admin.AdminPostHandler),
    ("^/admin/tag[/]?(.+)?$", Admin.AdminTagHandler),
    ("^/admin/comment[/]?(.+)?$", Admin.AdminCommentHandler),

    ("^/([\w\W]+)", Front.URLHandler)
    ], debug=True)
    wsgiref.handlers.CGIHandler().run(application)

if __name__ == '__main__':
    main()
