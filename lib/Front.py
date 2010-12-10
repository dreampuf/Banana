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
import logging, mimetypes, sys, os
from google.appengine.ext import db
from google.appengine.ext import *
from google.appengine.api import mail
import Base, Model, yui
from Base import Config
from lib.ext import captcha

class IndexHandler(Base.FrontRequestHandler):
    '''
    首页
    '''
    @yui.client_cache()
    def get(self, slug=None):
        p = slug != None and slug.isdigit() and int(slug) or 1

##        try:
        posts = Model.Post.fetch(p, fun=lambda x: x.filter("status =", Model.PostStatus.NORMAL).order("-created"))

        datas = [(i.url,
                  i.realurl,
                  i.title,
                  i.comments.count(),
                  i.created,
                  i.views,
                  i.precontent,
                  i.category.title,
                  i.author.username,
                  [tag.title for tag in i.tags]) for i in posts.data]

        cates = Model.Category.all().order("order").filter("ishidden =", False).fetch(1000)
        cates = [(i.title, i.description, i.url, i.posts.count()) for i in cates]

        tags = Model.Tag.all().fetch(1000)
        logging.info(datas)
        tags.sort(lambda x,y: -1 if x.postslen > y.postslen else 0 if x.postslen == y.postslen else 1)

        self.render("index.html", { "is_home": True,
                                    "posts": datas,
                                    "categorys": cates,
                                    "tags": tags[:20],
                                    "p": posts
                                  })
##        except:
##            logging.info("error in index, case:\n %s" % (sys.exc_info(),))
##            self.error(404)

class CategoryHandler(Base.FrontRequestHandler):
    '''
    分类
    '''
    def get(self, slug=None, p=None):
        if slug == None:
            self.redirect("/")
        else:
            cate = Model.Category.all().filter("url =", slug).get()
            if cate == None:
                self.error(404)
            else:
                p = 1 if p == None else int(p) if p.isdigit() else 1
                posts = Model.Post.fetch(p, fun=lambda x: x.filter("status =", Model.PostStatus.NORMAL).filter("category =", cate).order("-created"))
                datas = [(i.url,
                          i.realurl,
                          i.title,
                          i.comments.count(),
                          i.created,
                          i.views,
                          i.precontent,
                          i.category.title,
                          i.author.username,
                          [tag.title for tag in i.tags]) for i in posts.data]

                cates = Model.Category.all().order("order").filter("ishidden =", False).fetch(1000)
                cates = [(i.title, i.description, i.url, i.posts.count()) for i in cates]

                self.render("index.html", { "title": cate.title,
                                            "posts": datas,
                                            "categorys": cates,
                                            "p": posts,
                                            "pagetag": "" })

class TagHandler(Base.FrontRequestHandler):
    '''
    标签
    '''
    def get(self, slug=None):
        if slug == None:
            tags = Model.Tag.all().fetch(1000)

        else:
            pass

class SearchHandler(Base.FrontRequestHandler):
    '''
    搜索
    '''
    def get(self, slug=None):
        pass

class AttachmentsHandler(Base.FrontRequestHandler):
    '''
    附件浏览
    '''
    def get(self, slug=None):
        if slug != None:
            try:
                attach = Model.Attachment.get(slug)
            except:
                logging.info("get attachment error %s" % ( slug,) )
                self.redirect("/")

            contype = mail.EXTENSION_MIME_MAP[attach.filetype] \
                            if mail.EXTENSION_MIME_MAP.has_key(attach.filetype) \
                            else "application/octet-stream"

            self.response.header["Content-Type"] = contype
            self.response.header["Content-Disposition"] = str("filename=%s" % (attach.filename, ))
            self.write(attach.content)
        else:
            self.error(404)

class CommentHandler(Base.FrontRequestHandler):
    '''评论'''
    def post(self, slug=None):
        postkey = self.q("postkey")
        redirect = self.q("redirect")
        author = self.q("author")
        email = self.q("email")
        url = self.q("url")
        content = self.q("comment")
        recaptcha_challenge_field = self.q("recaptcha_challenge_field")
        recaptcha_response_field = self.q("recaptcha_response_field")

        if Config.commentstatus == Base.CommentStatus.DISENABLE:
            self.redirect(redirect)

        charep = captcha.submit( recaptcha_challenge_field,
                                        recaptcha_response_field,
                                        Config.recaptcha_private_key,
                                        self.request.remote_addr )
        if not charep.is_valid: #如果没有验证通过
            self.session["error"] = "验证码错误!"
            self.session["lastcomment"] = content
            self.redirect(redirect)
            return

        p = Model.Post.get(postkey)
        if p == None:
            self.redirect(redirect)

        error = []
        curuser = self.session.get("curuser", None)
        cment = Model.Comment()
        if curuser == None: #如果不是登录用户
            if Config.commentstatus != Base.CommentStatus.ENABLE: #如果不允许非登录用户评论
                self.redirect(redirect)

            if author.strip() == "":
                error.append("用户名不能为空")

            if email.strip() == "":
                error.append("邮箱地址不能为空")

            cment.nickname = author
        else: #是登录用户
            cment.author = curuser

        if content.strip() == "":
            error += "内容不能为空"

        if len(error):
            self.session["error"] = ",".join(error)
            self.redirect(redirect)

        cment.belong = p
        cment.commenttype = Model.CommentType.COMMENT
        cment.content = content
        cment.ip = self.request.remote_addr
        cment.email = Model.toEmail(email)
        cment.website = Model.toLink(url)
        if Config.commentneedcheck: #是否需要审核
            cment.hascheck = False
        cment.put()

        self.redirect(redirect)

class URLHandler(Base.FrontRequestHandler):
    '''
    Router
    '''
    def get(self, slug=None):
        if slug == None:
            self.redirect("/")

        #url is post realurl
        post = Model.Post.all().filter("realurl =", slug).get()
        if post != None:
            logging.info(post.key().id())
            data = {}
            data["is_post"] = True
            data["title"] = post.title
            data["commentstatus"] = Config.commentstatus if post.enablecomment else Base.CommentStatus.DISENABLE
            if self.session.get("lastcomment") != None:
                data["lastcomment"] = self.session.get("lastcomment")
                del self.session["lastcomment"]
            if self.session.get("error") != None:
                data["error"] = self.session.get("error")
                del self.session["error"]

            if post.status == Model.PostStatus.PAGE: #如果是page
                if post.enablecomment: #评论处理,并取得已评论数
                    cments = [(i.commenttype, i.created, i.nickname, i.hascheck, i.content) for i in post.comments.order("created").fetch(1000)]
                    cmentlen = len(cments)
                    data["comments"] = cments
                else:
                    cmentlen = post.comments.count()

                #url, realurl, title, lencomment, created, views, content, authorname, tags, postkey
                data["post"] = ( post.url,
                                 post.realurl,
                                 post.title,
                                 cmentlen,
                                 post.created,
                                 post.views,
                                 post.content,
                                 post.key() )

                tplfile = "page.html"
            else : #否则只是普通POST
                prev = Model.Post.all().order("created").filter("created <", post.created).get()
                next = Model.Post.all().order("created").filter("created >", post.created).get()
                if prev != None:
                    data["prev"] = prev
                if next != None:
                    data["next"] = next
                if post.enablecomment: #评论处理,并取得已评论数
                    #ctype, created, nickname, hascheck, content
                    cments = [(i.commenttype, i.created, i.nickname, i.hascheck, i.content) for i in post.comments.order("created").fetch(1000)]
                    cmentlen = len(cments)
                    data["comments"] = cments
                else:
                    cmentlen = post.comments.count()

                data["post"] = ( post.url,
                                 post.realurl,
                                 post.title,
                                 cmentlen,
                                 post.created,
                                 post.views,
                                 post.content,
                                 post.author.username,
                                 [tag.title for tag in post.tags],
                                 post.category,
                                 post.key() )

                tplfile = "single.html"

            self.render(tplfile, data)






