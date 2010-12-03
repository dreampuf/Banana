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
import logging
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
        htmls = HtmlHelper.ForTable(( [ HtmlHelper.ForLabel("博客名称", "blogtitle"), HtmlHelper.ForInput("blogtitle", Config.title) ],
                                      [ HtmlHelper.ForLabel("博客描述", "blogsubtitle"), HtmlHelper.ForInput("blogsubtitle", Config.subtitle) ],
                                      [ HtmlHelper.ForLabel("网站编码", "charset"), HtmlHelper.ForInput("charset", Config.charset)],
                                      [ HtmlHelper.ForLabel("页首脚本", "headlink"), HtmlHelper.ForTextArea("headlink", Config.headlink, style="width:90%; height:100px;")],
                                      [ HtmlHelper.ForLabel("页尾代码", "footer"), HtmlHelper.ForTextArea("footer", Config.footer, style="width:90%; height:100px;")],
                                      [ HtmlHelper.ForInputSubmit("提交")],
                                       ))
        data = {
            "blogtitle": Config.title,
            "blogsubtitle": Config.subtitle,
            "charset": Config.charset,
            "headlink": "\n".join(Config.headlink),
            "footer": Config.footer
        }
        self.render("AdminConfig.html", data)

    def post(self):
        title = fromq(self.q("blogtitle"))
        subtitle = fromq(self.q("blogsubtitle"))
        charset = fromq(self.q("charset"))
        headlink = fromq(self.q("headlink").replace("\r", "").split("\n"))
        footer = fromq(self.q("footer"))

        Config.title = title
        Config.subtitle = subtitle
        Config.charset = charset
        Config.headlink = headlink
        Config.footer = footer

        self.redirect_self()

class AdminUserHandler(Base.BackRequestHandler):
    def get(self, slug=None):
        pre = self.q("p")

        if slug != None and slug.lower() == "new":
            nuser = Model.User(username="", password="", email="")

            self.render("AdminUser_single.html", { "user": nuser,
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

        self.render("AdminUser.html", { "datas" : datas, "p": users })

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
                                                    "user": user,
                                                    "pre": "%s%s%s" % (Config.baseurl, "/admin/user/", pre)})
            return

        #列表
        p = int(slug) if slug != None and slug.isdigit() else 1
        attachments = Model.Attachment.fetch(p)

        idgenerater = Base.idgen((p-1) * 20 + 1)
        datas = [(str(idgenerater.next()), i.filename, i.filetype, i.belong, i.key()) for i in attachments.data]
        self.render("AdminAttachments.html", { "datas" : datas, "p": attachments })

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
                                                        "category": category,
                                                        "pre": "%s%s%s" % (Config.baseurl, "/admin/category/", pre)})
            return

        #列表
        p = int(slug) if slug != None and slug.isdigit() else 1
        categorys = Model.Category.fetch(p)
        idgenerater = Base.idgen((p-1) * 20 + 1)

        datas = [(str(idgenerater.next()), i.title, i.description,  i.order, i.url, i.posts.count(), i.key()) for i in categorys.data]
        datas.sort(lambda x,y: -1 if x[3]<y[3] else 0 if x[3]==y[3] else 1 )

        self.render("AdminCategory.html", { "datas" : datas, "p": categorys })

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
    pass

class AdminPostHandler(Base.BackRequestHandler):
    pass

class AdminCommentHandler(Base.BackRequestHandler):
    pass








