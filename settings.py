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
# From the typekit "kit" get the 7 characters before the ".js"
# If you're not using Adobe TypeKit, leave this blank and it will not process.
typekitId = ''
postsPerPage = 10