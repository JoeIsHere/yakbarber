#!/usr/bin/env python
# -*- coding: utf-8 -*- #

import markdown

root = "./"
webRoot = u"http://YOURDOMAIN"
contentDir = "content/"
templateDir = root + "templates/default/"
outputDir = root + "output/"
sitename = u'YOUR TITLE'
md = markdown.Markdown(extensions=['meta'])
postsPerPage = 10