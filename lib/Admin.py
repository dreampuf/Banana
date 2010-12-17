#!/usr/bin/env python
# -*- coding: UTF-8 -*-
#-------------------------------------------------------------------------------
# Name:        administer
# Author:      soddy
# Created:     24/11/2010
# Copyright:   (c) soddy 2010
# Email:       soddyque@gmail.com
#-------------------------------------------------------------------------------
#
import logging, sys, datetime, traceback
from google.appengine.ext import db
from google.appengine.api import memcache
from django.utils import simplejson
import Base, Model
from Base import HtmlHelper, Config


def fromq(v):
    '''From the v return v if v != "",else return None if v == ""'''
    return v if v != "" else None

class AdminLogin(Base.BackRequestHandler):
    def get(self):
        self.render("AdminLogin.html", {"a":HtmlHelper.ForInputLabel("Name", "bb") + HtmlHelper.For("br") + HtmlHelper.ForInput("ooo", "submit", "提交吧")})

    def post(self):
        username = self.request.get("username")
        password = self.request.get("password")
        logging.info(self.request.postvars)
        self.response.out.write("%s %s" %(username, password))

class AdminMainHandler(Base.BackRequestHandler):
    def get(self):

        self.render("AdminIndex.html")

class AdminConfigHandler(Base.BackRequestHandler):
    def get(self):

        data = {
            "title":"基本设置",
            "blogtitle": Config.title,
            "blogsubtitle": Config.subtitle,
            "charset": Config.charset,
            "headlink": "\n".join(Config.headlink),
            "footer": Config.footer,
            "posturl": Config.posturl,
            "commentstatus": Config.commentstatus,
            "commentneedcheck": Config.commentneedcheck,
            "localtimezone": Config.localtimezone,
            "author": Config.author,
            "feed": Config.feed,
            "feednumber": Config.feednumber,
            "feedshowpre": Config.feedshowpre,
            "indexnumber": Config.indexnumber,
            "indexshowpre": Config.indexshowpre,
            "hub": "\n".join(Config.hub),
            "domain": Config.domain
        }

        self.render("AdminConfig.html", data)

    def post(self):
        title = fromq(self.q("blogtitle"))
        subtitle = fromq(self.q("blogsubtitle"))
        charset = fromq(self.q("charset"))
        headlink = fromq(self.q("headlink").replace("\r", "").split("\n"))
        hub = fromq(self.q("hub").replace("\r", "").split("\n"))
        footer = fromq(self.q("footer"))
        posturl = fromq(self.q("posturl"))
        commentstatus = fromq(self.q("commentstatus"))
        commentneedcheck = fromq(self.q("commentneedcheck")) == "True"
        localtimezone = int(self.q("localtimezone")) if self.q("localtimezone").isdigit() else 8
        author = fromq(self.q("author"))
        feed = fromq(self.q("feed"))
        feednumber = int(self.q("feednumber")) if self.q("feednumber").isdigit() else 20
        feedshowpre = fromq(self.q("feedshowpre")) == "True"
        indexnumber = int(self.q("indexnumber")) if self.q("indexnumber").isdigit() else 20
        indexshowpre = fromq(self.q("indexshowpre")) == "True"
        domain = self.q("domain")


        Config.title = title
        Config.subtitle = subtitle
        Config.charset = charset
        Config.headlink = headlink
        Config.footer = footer
        Config.localtimezone = localtimezone
        if Config.posturl != posturl:
            Config.posturl = posturl
            i = 0;
            posts = Model.Post.all().fetch(1000)
            postslen = len(posts)
            while postslen > 0:
                for p in posts:
                    p.realurl = Base.processurl(p)
                    p.put()
                i += postslen
                posts = Model.Post.all().fetch(1000, offset=i)
        Config.commentstatus = commentstatus
        Config.commentneedcheck = commentneedcheck
        Config.author = author
        Config.feed = feed
        Config.feednumber = feednumber
        Config.feedshowpre = feedshowpre
        Config.indexnumber = indexnumber
        Config.indexshowpre = indexshowpre
        Config.hub = hub
        Config.domain = domain


        self.redirect_self()

class AdminUserHandler(Base.BackRequestHandler):
    def get(self, slug=None):
        pre = self.q("p")

        if slug != None and slug.lower() == "new":
            nuser = Model.User(username="", password="", email="a@a.com")

            self.render("AdminUser_single.html", { "user": nuser,
                                                    "title":"新增用户",
                                                   "pre": "%s%s%s" % (Config.baseurl, "/admin/user/", pre) })
            return

        issingle = slug != None and not slug.isdigit()
        if issingle: #修改
            try:
                user = Model.User.get(slug)
            except:
                self.error(404)
                return

##            htmls = HtmlHelper.ForTable([( HtmlHelper.ForLabel("用户名", "username"), HtmlHelper.ForInput("username", user.username) ),
##                                         ( HtmlHelper.ForLabel("密码", "password"), HtmlHelper.ForInput("password", user.password) ),
##                                         ( HtmlHelper.ForLabel("创建时间", "created"), HtmlHelper.ForInput("created", user.created) ),
##                                         ( HtmlHelper.ForLabel("上次登录IP", "lastip"), HtmlHelper.ForInput("lastip", user.lastip)),
##                                         ( HtmlHelper.ForLabel("上次登录时间", "lastlogin"), HtmlHelper.ForInput("lastlogin", user.lastlogin)),
##                                         ( HtmlHelper.ForInputSubmit("修改"), HtmlHelper.ForA("返回", "%s%s%s" % (Config.baseurl, "/admin/user/", pre)) ) ])

            self.render("AdminUser_single.html", { "issingle": issingle,
                                                    "user": user,
                                                    "title":"修改用户",
                                                    "pre": "%s%s%s" % (Config.baseurl, "/admin/user/", pre)})

            return

        #列表
        p = slug != None and slug.isdigit() and int(slug) or 1
        users = Model.User.fetch(p)

##        controls = [[ HtmlHelper.ForA("序号"), HtmlHelper.ForA("用户名", widti="15px"), HtmlHelper.ForA("上次登录时间"), HtmlHelper.ForA("操作") ]]
        idgenerater = Base.idgen((p-1) * 20 + 1)

##        for i in users.data:
##            controls.append([str(idgenerater.next()),
##                             HtmlHelper.ForA(i.username, "%s%s%s"%(Config.baseurl, "/admin/user/", i.key())),
##                             HtmlHelper.ForA(i.lastlogin),
##                             HtmlHelper.ForA("修改", data = i.key(), klass="formfunbutton") +
##                                HtmlHelper.ForA("删除", data = i.key(), klass="formfunbutton")])
##
##        #logging.info(controls)
##
##        htmls = "%s%s" % ( HtmlHelper.For("div", text = HtmlHelper.ForInputButton("新建") +
##                                                        HtmlHelper.ForInputButton("删除")),
##                           HtmlHelper.ForTable(controls)
##                           )

        datas = [(str(idgenerater.next()), i.username, i.lastlogin, i.key()) for i in users.data]

        self.render("AdminUser.html", { "datas" : datas,
                                        "title":"用户管理",
                                        "p": users })

    def post(self, slug=None):
        logging.info(slug)
        if slug == None or slug == "":
            self.redirect("/admin/user")
        if slug == "new":
            try:
                user = Model.User()
                user.username = fromq(self.q("username"))
                user.password = fromq(self.q("password"))
                user.email = fromq(self.q("email"))
                user.put()
            except:
                logging.info("store fail in user (%s, %s, %s)" % (user.username, user.password, user.email))
        else:
            try:
                user = Model.User.get(slug)
                action = self.q("action")
                if action == "delete" and user != None:
                    user.delete()
                user.username = fromq(self.q("username"))
                user.password = fromq(self.q("password"))
                user.email = fromq(self.q("email"))
                user.put()
            except:
                logging.info("store fail in user (%s, %s, %s)" % (user.username, user.password, user.email))
        self.redirect("/admin/user")


    def delete(self, slug=None):
        if slug != None:
            try:
                t = Model.User.get(slug)
                t.delete()
            except:
                self.write("error")
                return
            self.write("ok")


class AdminAttachmentHandler(Base.BackRequestHandler):
    '''
    Attachment Admin manager
    '''
    def get(self, slug=None):
        pre = self.q("p")

        if slug != None and slug.lower() == "new":  #TODO 新增附件未实现
            nuser = Model.User(username="", password="", email="")

            self.render("AdminUser_single.html", { "user": nuser,
                                                   "pre": "%s%s%s" % (Config.baseurl, "/admin/user/", pre) })
            return

        issingle = slug != None and not slug.isdigit()
        if issingle: #TODO 修改未实现
            try:
                user = Model.User.get(slug)
            except:
                self.error(404)
                return

            self.render("AdminUser_single.html", { "issingle": issingle,
                                                    "title":"附件修改",
                                                    "user": user,
                                                    "pre": "%s%s%s" % (Config.baseurl, "/admin/user/", pre)})
            return

        #列表
        p = int(slug) if slug != None and slug.isdigit() else 1
        attachments = Model.Attachment.fetch(p, fun=lambda x: x.order("-created"))

        idgenerater = Base.idgen((p-1) * 20 + 1)
        datas = [(str(idgenerater.next()), i.filename, i.filetype, i.filesize, i.belong, i.key()) for i in attachments.data]
        self.render("AdminAttachment.html", { "datas" : datas,
                                              "title":"附件管理",
                                              "p": attachments })

    def post(self, slug=None):
        action = self.q("action")
        if action == "delete" and slug != None:
            fl = Model.Attachment.get(slug)
            if fl != None:
                fl.delete()
                self.write("ok")
                return
        user = Model.User.all().get()

        filename = self.q("Filename")
        filedata = self.q("Filedata")
        #logging.info(dir(filedata))
        fl = Model.Attachment()
        fl.belong = user
        fl.filename = filename
        fl.setfiletype(filename)
        fl.filesize = len(filedata)
        fl.content = Model.toBlob(filedata)
        fl.put()

        logging.info(fl.key())
        self.write(fl.key())

    def delete(self, slug=None):
        if slug !=None:
            try:
                t = Model.Attachment.get(slug)
                t.delete()
            except:
                self.write("error")
                return
            self.write("ok")


class AdminCategoryHandler(Base.BackRequestHandler):
    '''
    Category manage
    '''
    def get(self, slug=None):
        pre = self.q("p")

        if slug != None and slug.lower() == "new": #新增
            ncat = Model.Category(title="", description="", url="")

            self.render("AdminCategory_single.html", { "category": ncat,
                                                       "title": "新增分类",
                                                       "pre": "%s%s%s" % (Config.baseurl, "/admin/category/", pre) })
            return

        issingle = slug != None and not slug.isdigit()
        if issingle: #修改
            try:
                category = Model.Category.get(slug)
            except:
                self.error(404)
                return

            self.render("AdminCategory_single.html", { "issingle": issingle,
                                                        "title": "修改分类",
                                                        "category": category,
                                                        "pre": "%s%s%s" % (Config.baseurl, "/admin/category/", pre)})
            return

        #列表
        p = int(slug) if slug != None and slug.isdigit() else 1
        categorys = Model.Category.fetch(p)
        idgenerater = Base.idgen((p-1) * 20 + 1)

        datas = [(str(idgenerater.next()), i.title, i.description,  i.order, i.url, i.posts.count(), i.key()) for i in categorys.data]
        datas.sort(lambda x,y: -1 if x[3]<y[3] else 0 if x[3]==y[3] else 1 )

        self.render("AdminCategory.html", { "datas" : datas,
                                            "title": "分类管理",
                                            "p": categorys })

    def post(self, slug=None):
        if slug != None and slug == "new":
            try:
                ncat = Model.Category()
                ncat.title = fromq(self.q("title"))
                ncat.description = fromq(self.q("description"))
                ncat.url = fromq(self.q("url"))
                ncat.order = int(fromq(self.q("order")))

                ncat.put()
            except:
                logging.info("save fail in category (%s,%s,%s)" %(ncat.title, ncat.description, ncat.url))
        elif slug != None:
            try:
                action = self.q("action")

                ncat = Model.Category.get(slug)
                if ncat == None:
                    self.redirect("/admin/category")
                    return

                if action == "delete":
#                    n = 0
#                    posts = Model.Post.all().filter("category =", ncat).fetch(1000)
#                    plen = len(posts)
#                    if plen > 0:
#                        for
                    ncat.delete()
                    self.write("ok")
                    return
                else:
                    ncat.title = fromq(self.q("title"))
                    ncat.description = fromq(self.q("description"))
                    ncat.url = fromq(self.q("url"))
                    ncat.order = int(fromq(self.q("order")))
                    ncat.put()
            except:
                logging.info("update fail in category (%s,%s,%s)" %(ncat.title, ncat.description, ncat.url))

        self.redirect("/admin/category")

    def delete(self, slug=None):
        if slug !=None:
            try:
                t = Model.Category.get(slug)
                t.delete()
            except:
                self.write("error")
                return
            self.write("ok")

class AdminTagHandler(Base.BackRequestHandler):
    '''
    Tag manage
    '''
    def get(self, slug=None):
        pre = self.q("p")

        if slug != None and slug.lower() == "new": #新增
            ntag = Model.Tag(title="", description="")

            self.render("AdminTag_single.html", { "tag": ntag,
                                                  "title":"新增标签",
                                                  "pre": "%s%s%s" % (Config.baseurl, "/admin/tag/", pre) })
            return

        issingle = slug != None and not slug.isdigit()
        if issingle: #修改
            try:
                tag = Model.Tag.get(slug)
            except:
                self.error(404)
                return

            self.render("AdminTag_single.html", { "issingle": issingle,
                                                  "title": "修改标签",
                                                  "tag": tag,
                                                  "pre": "%s%s%s" % (Config.baseurl, "/admin/tag/", pre)})
            return

        #列表
        p = int(slug) if slug != None and slug.isdigit() else 1
        tags = Model.Tag.fetch(p)
        idgenerater = Base.idgen((p-1) * 20 + 1)

        datas = [(str(idgenerater.next()), i.title, i.description, i.postslen, i.key()) for i in tags.data]

        self.render("AdminTag.html", { "datas" : datas,
                                       "title": "标签管理",
                                       "p": tags })

    def post(self, slug=None):
        if slug != None and slug == "new":
            try:
                ntag = Model.Tag()
                ntag.title = fromq(self.q("title"))
                ntag.description = fromq(self.q("description"))
                ntag.put()
            except:
                logging.info("save fail in tag (%s,%s) case :%s" %(ntag.title, ntag.description, sys.exc_info()))
        elif slug != None:
            try:
                action = self.q("action")
                ntag = Model.Tag.get(slug)
                if action == "delete":
                    rels = Model.tags_posts.all().filter("tag =", ntag).fetch(1000)
                    Model.tags_posts.deletes(rels)
                    ntag.delete()
                    self.write("ok")
                    return
                else:
                    ntag.title = fromq(self.q("title"))
                    ntag.description = fromq(self.q("description"))
                    ntag.put()
            except:
                logging.info("update fail in tag (%s,%s) case:%s" %(ntag.title, ntag.description, sys.exc_info()))

        self.redirect("/admin/tag")

    def delete(self, slug=None):
        if slug !=None:
            try:
                t = Model.Tag.get(slug)
                if t != None:
                    hasUseTag = Model.tags_posts.all().filter("tag =", t).fetch(1000)
                    tlen = len(hasUseTag)
                    n = 0
                    while tlen > 0:
                        Model.tags_posts.deletes(hasUseTag)
                        hasUseTag = Model.tags_posts.all().filter("tag =", t).fetch(1000, n)
                        n += tlen
                        tlen = len(hasUseTag)
                    t.delete()
            except:
                self.write("error")
                return
            self.write("ok")



class AdminPostHandler(Base.BackRequestHandler):
    '''
    Post manage
    '''
    def get(self, slug=None):
        pre = self.q("p")

        if slug != None and slug.lower() == "new": #新增
            self.data["head_link"].append(("js", "/js/markitup/jquery.markitup.js"))
            self.data["head_link"].append(("js", "/js/markitup/sets/html/set.js"))
            self.data["head_link"].append(("css", "/js/markitup/skins/jtageditor/style.css"))
            self.data["head_link"].append(("css", "/js/markitup/sets/html/style.css"))
            self.data["head_link"].append(("js", "/js/swfobject.js"))
            self.data["head_link"].append(("css", "/js/uploadify/uploadify.css"))
            self.data["head_link"].append(("js", "/js/uploadify/jquery.uploadify.v2.1.4.min.js"))
            self.data["head_link"].append(("js", "/js/keyword.js"))

            npost = Model.Post(title="", content="", precontent="", url="", tags = [], created=Base.UTCtoLocal(datetime.datetime.now()))

            self.render("AdminPost_single.html", { "post": npost,
                                                   "cates": Model.Category.all().fetch(1000),
                                                   "pre": "%s%s%s" % (Config.baseurl, "/admin/post/", pre),
                                                   "title": "添加文章" })
            return

        issingle = slug != None and not slug.isdigit()
        if issingle: #修改
            self.data["head_link"].append(("js", "/js/markitup/jquery.markitup.js"))
            self.data["head_link"].append(("js", "/js/markitup/sets/html/set.js"))
            self.data["head_link"].append(("css", "/js/markitup/skins/jtageditor/style.css"))
            self.data["head_link"].append(("css", "/js/markitup/sets/html/style.css"))
            self.data["head_link"].append(("js", "/js/swfobject.js"))
            self.data["head_link"].append(("css", "/js/uploadify/uploadify.css"))
            self.data["head_link"].append(("js", "/js/uploadify/jquery.uploadify.v2.1.4.min.js"))
            self.data["head_link"].append(("js", "/js/keyword.js"))
            try:
                post = Model.Post.get(slug)
            except:
                self.error(404)
                return
            tags = ",".join([i.title for i in post.tags])
            post.created = Base.UTCtoLocal(post.created)
            self.render("AdminPost_single.html", { "issingle": issingle,
                                                   "cates": Model.Category.all().fetch(1000),
                                                   "curcate": post.category,
                                                   "post": post,
                                                   "tag": tags,
                                                   "pre": "%s%s%s" % (Config.baseurl, "/admin/post/", pre),
                                                   "title": "修改文章" })
            return

        #列表
        p = int(slug) if slug != None and slug.isdigit() else 1
        posts = Model.Post.fetch(p, fun=lambda x: x.order("-created"))
        idgenerater = Base.idgen((p-1) * 20 + 1)

        datas = [(str(idgenerater.next()), i.title, i.category.title, i.category.key(), Base.UTCtoLocal(i.created), i.key()) for i in posts.data]

        self.render("AdminPost.html", { "datas" : datas,
                                        "title": "文章管理",
                                        "p": posts })

    def post(self, slug=None):
        if slug != None and slug == "new":
            try:
                p = Model.Post()
                p.title = fromq(self.q("title"))
                p.author = Model.User.all().get() #TODO
                category = Model.Category.get(fromq(self.q("category")))
                p.category = category
                p.created = datetime.datetime.now()
                p.url = fromq(self.q("url"))
                Base.processurl(p)
                p.created = Base.ParserLocalTimeToUTC(self.q("created"))
                p.content = fromq(self.q("content"))
                p.precontent = fromq(self.q("precontent"))
                p.put()

                tags = fromq(self.q("tag")).split(",")
                if len(tags) == 1 and tags[0] == "":
                    pass
                else:
                    for i in tags:
                        t = Model.Tag.all().filter("title =", i).get()
                        if t == None:
                            t = Model.Tag(title=i, description="在神秘的 %s 我降临啦" % datetime.datetime.now().strftime("%Y/%m/%d %H:%M:%S"))
                            t.put()

                        rela = Model.tags_posts.all().filter("tag =", t).filter("post =", p).get()
                        if rela == None:
                            rela = Model.tags_posts()
                            rela.post = p
                            rela.tag = t
                            rela.put()

                Base.pinghub()
            except:
                exc_type, exc_value, exc_traceback = sys.exc_info()
                logging.info("save fail in Post case :%s" %(traceback.format_exception(exc_type,
                                                                                            exc_value,
                                                                                            exc_traceback), ))
        elif slug != None:
            try:
                p = Model.Post.get(slug)
                if p == None:
                    self.redirect("/admin/post")
                    return
                action = self.q("action")
                if action == "delete":
                    Model.Comment.deletes(Model.Comment.all().filter("belong =", p).fetch(1000))
                    Model.tags_posts.deletes(Model.tags_posts.all().filter("post =", p).fetch(1000))
                    p.delete()
                    self.write("ok")
                    return
                else:
                    p.title = fromq(self.q("title"))
                    p.author = Model.User.all().get() #TODO
                    category = Model.Category.get(fromq(self.q("category")))
                    p.category = category
                    p.url = fromq(self.q("url"))
                    Base.processurl(p)
                    p.created = Base.ParserLocalTimeToUTC(self.q("created"))
                    p.content = fromq(self.q("content"))
                    p.precontent = fromq(self.q("precontent"))
                    p.put()

                tags = fromq(self.q("tag")).split(",")
                if tags == None:
                    ralas = Model.tags_posts.all().filter("post =", p).fetch(1000)
                    Model.tags_posts.deletes(ralas)
                else:
                    for i in tags:
                        t = Model.Tag.all().filter("title =", i).get()
                        if t == None:
                            t = Model.Tag(title=i, description="在神秘的 %s 我降临啦" % datetime.datetime.now().strftime("%Y/%m/%d %H:%M:%S"))
                            t.put()

                        rela = Model.tags_posts.all().filter("tag =", t).filter("post =", p).get()
                        if rela == None:
                            rela = Model.tags_posts()
                            rela.post = p
                            rela.tag = t
                            rela.put()

            except:
                exc_type, exc_value, exc_traceback = sys.exc_info()
                logging.info("save fail in Post case :%s" %(traceback.format_exception(exc_type,
                                                                                            exc_value,
                                                                                            exc_traceback), ))

        self.redirect("/admin/post")

    def delete(self, slug=None):
        if slug !=None:
            try:
                t = Model.Post.get(slug)

                comments = t.comments.fetch(1000)

                Model.Comment.deletes(comments)
                tags = Model.tags_posts.all().filter("post =", t.key()).fetch(1000)
                Model.tags_posts.deletes(tags)

                t.delete()
            except:
                self.write("error case:%s" % (sys.exc_info(),))
                return
            self.write("ok")

class AdminCommentHandler(Base.BackRequestHandler):
    '''
    Comment manage
    '''
    def get(self, slug=None):
        pre = self.q("p")

        if slug != None and slug.lower() == "new": #新增
            cment = Model.Comment(content="", ip="", website=db.Link(""), email=db.Email(""))

            self.render("AdminComment_single.html", { "comment": cment,
                                                      "title": "新增评论",
                                                      "pre": "%s%s%s" % (Config.baseurl, "/admin/comment/", pre) })
            return

        issingle = slug != None and not slug.isdigit()
        if issingle: #修改
            try:
                cment = Model.Comment.get(slug)
                logging.info(cment.author.username)
            except:
                self.error(404)
                return
            self.render("AdminComment_single.html", { "issingle": issingle,
                                                        "title": "修改评论",
                                                        "comment": cment,
                                                        "pre": "%s%s%s" % (Config.baseurl, "/admin/comment/", pre)})
            return

        #列表
        p = int(slug) if slug != None and slug.isdigit() else 1
        comments = Model.Comment.fetch(p, fun=lambda x: x.order("-created"))
        idgenerater = Base.idgen((p-1) * 20 + 1)

        datas = [(str(idgenerater.next()), i.content[:400], i.ip, Base.UTCtoLocal(i.created), i.key()) for i in comments.data]

        self.render("AdminComment.html", { "datas" : datas,
                                           "title": "评论管理",
                                           "p": comments })

    def post(self, slug=None):
        if slug != None and slug == "new":#TODO Post a New Comment
            try:
                cment = Model.Comment()
                cment.content = fromq(self.q("content"))
                cment.created = Base.UTCtoLocal(datetime.datetime.now())
                cment.put()
            except:
                logging.info("save fail in Comment (%s) case:%s" %(ntag.content, sys.exc_info()))
        elif slug != None:
            try:
                cment = Model.Comment.get(slug)
                action = self.q("action")
                if action == "delete" and cment != None:
                    cment.delete()
                    self.write("ok")
                    return
                else :
                    cment.content = fromq(self.q("content"))
                    cment.put()
            except:
                logging.info("update fail in Comment (%s) case:%s" %(ntag.content, sys.exc_info()))

        self.redirect("/admin/comment")

    def delete(self, slug=None):
        if slug !=None:
            try:
                t = Model.Comment.get(slug)
                t.delete()
            except:
                self.write("error")
                return
            self.write("ok")

class AdminCronHandler(Base.BackRequestHandler):
    '''
    Cron Jobs
    '''
    def get(self, slug=None):
        if slug == "refreshview":
            view = memcache.get("views", namespace="Front")
            if view != None:
                for k,v in view.items():
                    p = Model.Post.all().filter("realurl =", k).get()
                    if p:
                        p.views += v
                        p.put()
            memcache.delete("views", namespace="Front")



