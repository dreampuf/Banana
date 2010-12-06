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
import Base, Model
from Base import HtmlHelper, Config

class IndexHandler(Base.FrontRequestHandler):
    '''
    首页
    '''
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

            self.response.headers["Content-Type"] = contype
            logging.info("attachment; filename=%s" % attach.filename)
            self.response.headers["Content-Disposition"] = str("filename=%s.%s" % (attach.filename, attach.filetype))
            self.write(attach.content)

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
            data = {}
            data["is_post"] = True
            data["title"] = post.title
            data["commentstatus"] = Config.commentstatus if post.enablecomment else Base.CommentStatus.DISENABLE
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






