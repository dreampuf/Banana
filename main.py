#!/usr/bin/env python
# -*- coding: UTF-8 -*-
#-------------------------------------------------------------------------------
# Name:        Main
# Author:      soddy
# Created:     09/11/2010
# Copyright:   (c) soddy 2010
# Email:       soddyque@gmail.com
#-------------------------------------------------------------------------------
#

import cgi, sys, os, logging, datetime

sys.path.append("lib")
from google.appengine.ext.webapp import util
from lib import Base, Model, Admin, Front, yui

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
        logging.info(self.request.remote_addr)
        htmls = '''
<form method="post"><input id="upfilebtn" type="file" name="upfile" /><input type="submit"></form>
<script>
$(function(){
    $('#upfilebtn').uploadify({
            'uploader': '/js/uploadify/uploadify.swf',
            'script': '/a',
            'cancelImg': '/js/uploadify/cancel.png',
            'wmode': 'transparent',
            auto: true,
            sizeLimit: 1000000,
            multi: true,
            onComplete: function (event, ID, fileObj, response, data) {
                console.log(arguments);
            }
        });
});
</script>
'''
        self.write(htmls)

    def post(self):
        import zipfile, StringIO
        zfile = self.request.params["Filedata"]

        #logging.info(dir(zfile.file))
        #sio = StringIO.StringIO(zfile)

        zf = zipfile.ZipFile(zfile.file, "rb")
        nl = zf.namelist()
        for i in nl:
            if i.endswith(".py"):
                exec(zf.read(i).replace('\r\n', '\n'))
                logging.info("has exec")

        zf.close()

        logging.info(nl)

        self.write("ok")

class SearchHandler(Base.FrontRequestHandler):
    def get(self, slug=None):
        htmls = '''
<html>
<head>
<script src="http://blog.macgoo.com/js/common.js">
$(function(){
$.ajax({
    type:"DELETE",
    url:"/search",
    data:{"user":"!23123"},
    success:function(msg){
        if(msg == "ok") {
            console.log("ok");
        }
    },
    error:function(xhr, textStatus, errorThrown){
        alert("出错"+textStatus);
    }
});
});
</script>
</head>
<body>
<form method="post">
<input type="text" name="search" value="your want search" /> <input type="submit" value="提交" />
</form>
</html>
'''
        self.write(htmls)

    def post(self, slug=None):
        arg = self.q("search")

        result = Model.Post.all().search(arg).fetch(1000)
        for i in result:
            self.write('<a href="%s">%s</a><br />'%(i.key(), i.title))

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
        htmls = '''<html><script src="/js/common.js"></script><body>
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
            a.created = datetime.datetime.now()
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
            attach.filesize = len(attach.content)
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
        self.write(str(end_time - start_time))



class InstallHandler(Base.FrontRequestHandler):
    def get(self):
        pass
    def post(self):
        pass

def main():
    application = yui.WsgiApplication([
    ("^[/]?", Front.IndexHandler),
    ("^/page[/]?(.+)?$", Front.IndexHandler),
    ("^/comment[/]?(.+)?$", Front.CommentHandler),
    ("^/attachment[/]?(.+)?$", Front.AttachmentsHandler),
    ("^/category[/]?(.+)?[/]?(.+)?$", Front.CategoryHandler),
    ("^/tag[/]?(.+)?$", Front.TagHandler),
    ("^/tool[/]?(.+)?$", Front.ToolHandler),


    ("^/search[/]?(.+)?$", SearchHandler),
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
    ("^/admin/cron[/]?(.+)?$", Admin.AdminCronHandler),


    ("^/([\w\W]+)", Front.URLHandler)
    ], default_response_class=yui.Response)
    util.run_wsgi_app(application)

if __name__ == '__main__':
    main()
