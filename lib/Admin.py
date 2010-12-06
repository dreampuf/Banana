#-------------------------------------------------------------------------------
# Name:        administer
# Author:      soddy
# Created:     24/11/2010
# Copyright:   (c) soddy 2010
# Email:       soddyque@gmail.com
#-------------------------------------------------------------------------------
#!/usr/bin/env python
# -*- coding: UTF-8 -*-
#
import logging, sys, datetime
from google.appengine.ext import db
from google.appengine.ext import *
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
            "commentneedcheck": Config.commentneedcheck
        }
        logging.info(str(Config.commentneedcheck))
        self.render("AdminConfig.html", data)

    def post(self):
        title = fromq(self.q("blogtitle"))
        subtitle = fromq(self.q("blogsubtitle"))
        charset = fromq(self.q("charset"))
        headlink = fromq(self.q("headlink").replace("\r", "").split("\n"))
        footer = fromq(self.q("footer"))
        posturl = fromq(self.q("posturl"))
        commentstatus = fromq(self.q("commentstatus"))
        commentneedcheck = fromq(self.q("commentneedcheck")) == "True"

        Config.title = title
        Config.subtitle = subtitle
        Config.charset = charset
        Config.headlink = headlink
        Config.footer = footer
        Config.posturl = posturl
        Config.commentstatus = commentstatus
        Config.commentneedcheck = commentneedcheck


        self.redirect_self()

class AdminUserHandler(Base.BackRequestHandler):
    def get(self, slug=None):
        pre = self.q("p")

        if slug != None and slug.lower() == "new":
            nuser = Model.User(username="", password="", email="")

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

        controls = [[ HtmlHelper.ForA("序号"), HtmlHelper.ForA("用户名", widti="15px"), HtmlHelper.ForA("上次登录时间"), HtmlHelper.ForA("操作") ]]
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
        logging.info(self.request.params)
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
        datas = [(str(idgenerater.next()), i.filename, i.filetype, i.belong, i.key()) for i in attachments.data]
        self.render("AdminAttachment.html", { "datas" : datas,
                                              "title":"附件管理",
                                              "p": attachments })

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
                ncat = Model.Category.get(slug)
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
                ntag = Model.Tag.get(slug)
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

            npost = Model.Post(title="", content="", precontent="", url="", tags = [])

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
            try:
                post = Model.Post.get(slug)
            except:
                self.error(404)
                return
            tags = ",".join([i.title for i in post.tags])
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

        datas = [(str(idgenerater.next()), i.title, i.category.title, i.category.key(), i.created, i.key()) for i in posts.data]

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
                p.url = fromq(self.q("url"))
                p.created = datetime.datetime.now()
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
            except:
                logging.info("save fail in tag (%s,%s) case :%s" %(ntag.title, ntag.description, sys.exc_info()))
        elif slug != None:
            try:
                p = Model.Post.get(slug)
                if p == None:
                    self.redirect("/admin/post")
                    return

                p.title = fromq(self.q("title"))
                p.author = Model.User.all().get() #TODO
                category = Model.Category.get(fromq(self.q("category")))
                p.category = category
                p.url = fromq(self.q("url"))
                Base.processurl(p)
                p.created = datetime.datetime.now()
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

            except:
                logging.info("update fail in tag (%s,%s) case:%s" %(ntag.title, ntag.description, sys.exc_info()))

        self.redirect("/admin/post")

    def delete(self, slug=None):
        if slug !=None:
            try:
                t = Model.Post.get(slug)

                comments = t.comments.fetch(1000)

                Model.Comment.deletes(comments)
                logging.info("GeiLi?")
                tags = Model.tags_posts.all().filter("post =", t.key()).fetch(1000)
                Model.tags_posts.deletes(tags)

                t.delete()
            except:
                self.write("error case:%s" % (str(sys.exc_info()),))
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

        datas = [(str(idgenerater.next()), i.content[:400], i.ip, i.created, i.key()) for i in comments.data]

        self.render("AdminComment.html", { "datas" : datas,
                                           "title": "评论管理",
                                           "p": comments })

    def post(self, slug=None):
        if slug != None and slug == "new":#TODO Post a New Comment
            try:
                cment = Model.Comment()
                cment.content = fromq(self.q("content"))

                cment.put()
            except:
                logging.info("save fail in Comment (%s) case:%s" %(ntag.content, sys.exc_info()))
        elif slug != None:
            try:
                cment = Model.Comment.get(slug)
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






