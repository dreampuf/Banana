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
import logging, sys, os, urllib
from google.appengine.api import mail, memcache, urlfetch
from django.utils import simplejson as json
import Base, Model, yui as SER
from Base import Config
from lib.ext import captcha
from datetime import datetime

def urlview(handler):
    def view_handler(*args, **kw):
        url = args[1]
        url = urllib.unquote(url)

        view = memcache.get("views", namespace="Front")
        if view == None:
            view = {}
        if not view.has_key(url):
            view[url] = 0
        view[url] += 1
        memcache.set("views", view, namespace="Front")
        return handler(*args, **kw)
    return view_handler



class IndexHandler(Base.FrontRequestHandler):
    '''
    首页
    '''
    @SER.server_cache(60)
    def get(self, slug=None):
        p = slug != None and slug.isdigit() and int(slug) or 1

##        try:
        posts = Model.Post.fetch(p, plen=Config.indexnumber, fun=lambda x: x.filter("status =", Model.PostStatus.NORMAL).order("-created"))
        isShowPre = Config.indexshowpre
        datas = [(i.url,
                  i.realurl,
                  i.title,
                  i.comments.count(),
                  Base.UTCtoLocal(i.created),
                  i.views,
                  i.precontent if isShowPre else i.content,
                  i.category.title,
                  i.author.username,
                  [tag.title for tag in i.tags]) for i in posts.data]

        cates = Model.Category.all().order("order").filter("ishidden =", False).fetch(1000)
        cates = [(i.title, i.description, i.url, i.posts.count()) for i in cates]

        tags = Model.Tag.all().fetch(1000)
        tags.sort(lambda x,y: -1 if x.postslen > y.postslen else 0 if x.postslen == y.postslen else 1)

        cments = Model.Comment.all().order("-created").fetch(10)
        cments = [(i.belong.realurl, i.content, Base.UTCtoLocal(i.created), ) for i in cments]

        self.render("index.html", { "is_home": True,
                                    "posts": datas,
                                    "categorys": cates,
                                    "lastcomments": cments,
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
    @SER.server_cache(60)
    def get(self, slug=None, p=None):
        if slug == None:
            self.redirect("/")
        else:
            cate = Model.Category.all().filter("url =", slug).get()
            if cate == None:
                self.error(404)
            else:
                p = 1 if p == None else int(p) if p.isdigit() else 1
                isShowPre = Config.indexshowpre
                posts = Model.Post.fetch(p, fun=lambda x: x.filter("status =", Model.PostStatus.NORMAL).filter("category =", cate).order("-created"))
                datas = [(i.url,
                          i.realurl,
                          i.title,
                          i.comments.count(),
                          Base.UTCtoLocal(i.created),
                          i.views,
                          i.precontent if isShowPre else i.content,
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
            self.response.header["Cache-Control"] = "max-age=900"
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
        cment.ip = self.request.client_ip
        cment.email = Model.toEmail(email)
        cment.website = Model.toLink(url)
        if Config.commentneedcheck: #是否需要审核
            cment.hascheck = False
        cment.put()

        self.redirect(redirect)

class FeedHandler(Base.FrontRequestHandler):
    '''
    Feed
    '''
    def get(self, slug=None):
        self.set_content_type("atom")
        if slug == None:
            data = { "language": Config.lang,
                     "title": Config.title,
                     "subtitle": Config.subtitle,
                     "rss": Config.feed,
                     "last_update": Base.UTCtoLocal(datetime.now()),
                     "author": Config.author,
                     "hubs": Config.hub,
                     "charset": Config.charset
            }
            posts = Model.Post.all().filter("status IN", (Model.PostStatus.NORMAL, Model.PostStatus.PAGE, Model.PostStatus.TOP)).order("-created").fetch(Config.feednumber)
            isShowPre = Config.feedshowpre
            posts = [( i.title,
                       i.author.username,
                       i.key().id(),
                       i.realurl,
                       Base.UTCtoLocal(i.created),
                       i.precontent if isShowPre else i.content
                     ) for i in posts]
            data["posts"] = posts

            self.render("feed.xml", data)


class ToolHandler(Base.FrontRequestHandler):
    '''
    Unity
    '''
    def post(self, slug):
        if slug == "analysispost":
#            data = self.q("data")
#            multi = self.q("multi") if self.q("multi") == "" else 0
#            response = urlfetch.fetch(url="http://www.ftphp.com/scws/api.php",
#                                      method=urlfetch.POST,
#                                      payload=urllib.urlencode({"data":data,
#                                                                "multi":multi,
#                                                                "respond":"json",
#                                                                "ignore": "yes"})
#                                      )
#            self.set_content_type("json")
#            self.write(response.content)
            pass
        elif slug == "keyword":
            data = self.q("data")
            from lib.ext.keyword import keyword
            result = keyword(data)
            self.set_content_type("json")
            self.write(json.write(result))
        elif slug == "pinghub":
            data = urllib.urlencode({'hub.url': "%s/%s"%(Config.baseurl, Config.feed), 'hub.mode': 'publish'})
            rpcs = []
            for i in Config.hub:
                rpc = urlfetch.create_rpc()
                urlfetch.make_fetch_call(rpc, i)
                rpcs.append(rpc)
            for i in rpcs:
                i.wait()



class URLHandler(Base.FrontRequestHandler):
    '''
    Router
    '''
    @urlview
    #@SER.server_cache(60)
    def get(self, slug=None):
        if slug == None:
            self.redirect("/")

        if slug == Config.feed:
            response = FeedHandler(self.request, self.response)
            response.get()
            return
        #url is post realurl
        slug = urllib.unquote(slug)

        post = Model.Post.all().filter("realurl =", slug).get()
        if post != None:
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
                    cments = [(i.commenttype, Base.UTCtoLocal(i.created), i.nickname, i.hascheck, i.content) for i in post.comments.order("created").fetch(1000)]
                    cmentlen = len(cments)
                    data["comments"] = cments
                else:
                    cmentlen = post.comments.count()

                #url, realurl, title, lencomment, created, views, content, authorname, tags, postkey
                data["post"] = ( post.url,
                                 post.realurl,
                                 post.title,
                                 cmentlen,
                                 Base.UTCtoLocal(post.created),
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
                    cments = [(i.commenttype, Base.UTCtoLocal(i.created), i.nickname, i.hascheck, i.content) for i in post.comments.order("created").fetch(1000)]
                    cmentlen = len(cments)
                    data["comments"] = cments
                else:
                    cmentlen = post.comments.count()

                data["post"] = ( post.url,
                                 post.realurl,
                                 post.title,
                                 cmentlen,
                                 Base.UTCtoLocal(post.created),
                                 post.views,
                                 post.content,
                                 post.author.username,
                                 [tag.title for tag in post.tags],
                                 post.category,
                                 post.key() )

                tplfile = "single.html"

            self.render(tplfile, data)






