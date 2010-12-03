#-------------------------------------------------------------------------------
# Name:        Test Model
# Author:      soddy
# Created:     25/11/2010
# Copyright:   (c) soddy 2010
# Email:       soddyque@gmail.com
#-------------------------------------------------------------------------------
#!/usr/bin/env python
# -*- coding: UTF-8 -*-
#
import sys, os, logging
from datetime import datetime, timedelta
from time import time
import unittest
from urllib import urlencode

sys.path.append("..")
from lib import gaeunit

#from lib.Base import *

class ConfigTest(unittest.TestCase):
    tc = gaeunit.GAETestCase("run")

    def setup(self):
        logging.info("in Test")

    def test_defaulte(self):
        self.assertEqual("asdas", "asdas")
