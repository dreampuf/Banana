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
import logging, mimetypes
from google.appengine.ext import db
from google.appengine.ext import *
from google.appengine.api import mail
import Base, Model
from Base import HtmlHelper, Config

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






