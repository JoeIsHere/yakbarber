#!/usr/bin/env python
# -*- coding: utf-8 -*- #

from codecs import open
import os
import sys
import pprint
import pystache
from itertools import islice
import argparse
import imp
import shutil
import re
import time

# Settings Import

parser = argparse.ArgumentParser(description='Yak Barber is a fiddly little time sink, and blog system.')
parser.add_argument('-s','--settings',nargs=1,help='Specify a settings.py file to use.')
args = parser.parse_args()
if args.settings is not None:
  settingsPath = args.settings[0]
else:
  settingsPath = './settings.py'
settings = imp.load_source('settings.py',settingsPath)

# Settings Local

root = settings.root
webRoot = settings.webRoot
contentDir = settings.contentDir
templateDir = settings.templateDir
outputDir = settings.outputDir
sitename = settings.sitename
author = settings.author
md = settings.md
postsPerPage = settings.postsPerPage

# 'meta','fenced_code','footnotes','smart_strong','smarty'

def safeMkDir(f):
    d = f
    if not os.path.exists(d):
        os.makedirs(d)

def splitEvery(n, iterable):
    i = iter(iterable)
    piece = list(islice(i, n))
    while piece:
        yield piece
        piece = list(islice(i, n))

def removePunctuation(text):
  text = re.sub(r'\s[^a-zA-Z0-9]\s',' ',text)
  text = re.sub(r'[^a-zA-Z0-9\s]+','',text)
  text = text.encode('ascii','xmlcharrefreplace')
  return text

def templateResources():
  tList = os.listdir(templateDir)
  tList = [x for x in tList if ('.html' or '.xml') not in x]
  for tr in tList:
      fullPath = os.path.join(templateDir, tr)
      if (os.path.isfile(fullPath)):
          shutil.copy(fullPath, outputDir)

def openConvert(mdfile):
  with open(mdfile, 'r', 'utf-8') as f:
    rawfile = f.read()
    converted = md.convert(rawfile)
    if re.match(r'[a-zA-Z0-9]+',md.Meta[u'title'][0]):
      convertedMeta = [md.Meta, converted]
      return convertedMeta
    else:
      return None


def renderPost(post, posts):
  metadata = {}
  for k, v in post[0].iteritems():
    metadata[k] = v[0]
  metadata[u'content'] = post[1]
  metadata[u'sitename'] = sitename
  metadata[u'webRoot'] = webRoot
  metadata[u'author'] = author
  postName = removePunctuation(metadata[u'title'])
  postName = metadata[u'date'].split(' ')[0] + '-' + postName.replace(u' ',u'-')
  postName = u'-'.join(postName.split('-'))
  postFileName = outputDir + postName + '.html'
  metadata[u'postURL'] = webRoot + postName + '.html'
  with open(templateDir + u'/post-content.html','r','utf-8') as f:
    postContentTemplate = f.read()
    postContent = pystache.render(postContentTemplate,metadata,decode_errors='ignore')
    metadata['post-content'] = postContent
  with open(templateDir + u'/post-page.html','r','utf-8') as f:
    postPageTemplate = f.read()
    postPageResult = pystache.render(postPageTemplate,metadata,decode_errors='ignore')
  with open(postFileName,'w','utf-8') as f:
    f.write(postPageResult)
  return posts.append(metadata)

def feed(posts):
  feedDict = posts[0]
  feedDict.setdefault('atom-entry',[])
  feedDict['gen-time'] = time.asctime(time.localtime())
  with open(templateDir + u'/atom.xml','r','utf-8') as f:
    atomTemplate = f.read()
  with open(templateDir + u'/atom-entry.xml','r','utf-8') as f:
    atomEntryTemplate = f.read()
  for e,p in enumerate(posts):
    if e < postsPerPage:
      atomEntryResult = pystache.render(atomEntryTemplate,p)
      feedDict['atom-entry'].append(atomEntryResult)
  feedResult = pystache.render(atomTemplate,feedDict)
  with open(outputDir + 'feed','w','utf-8') as f:
    f.write(feedResult)

def paginatedIndex(posts):
  indexList = sorted(posts,key=lambda k: k[u'date'])[::-1]
  feed(indexList)
  postList = []
  for i in indexList:
    postList.append(i['post-content'])
  indexOfPosts = splitEvery(postsPerPage,indexList)
  with open(templateDir + u'/index.html','r','utf-8') as f:
    indexTemplate = f.read()
  indexDict = {}
  indexDict[u'sitename'] = sitename
  for e,p in enumerate(indexOfPosts):
    indexDict['post-content'] = p
    print e
    for x in p:
      print x['title']
    if e == 0:
      fileName = u'index.html'
      if len(indexList) > postsPerPage:
        indexDict[u'previous'] = webRoot + u'index2.html'
    else:
      fileName = u'index' + str(e+1) + u'.html'
      if e == 1:
        indexDict[u'next'] = webRoot + u'index.html'
        indexDict[u'previous']  = webRoot + u'index' + str(e+2) + u'.html'
      else:
        indexDict[u'previous'] = webRoot + u'index' + str(e+2) + u'.html'
        if e < len(indexList):
          indexDict[u'next'] = webRoot + u'index' + str(e-1) + u'.html'
    indexPageResult = pystache.render(indexTemplate,indexDict)
    with open(outputDir + fileName,'w','utf-8') as f:
      f.write(indexPageResult)

def start():
  convertedList = []
  posts =[]
  contentList = os.listdir(contentDir)
  for c in contentList:
    if c.endswith('.md') or c.endswith('.markdown'):
      mdc = openConvert(contentDir+c)
      if mdc is not None:
        convertedList.append(mdc)
  sortedList = sorted(convertedList, key=lambda x: x[0], reverse=True)
  #pprint.pprint(convertedList, indent=1, depth=4)
  for post in sortedList:
    renderPost(post,posts)
  paginatedIndex(posts)
  templateResources()


def main():
  safeMkDir(contentDir)
  safeMkDir(templateDir)
  safeMkDir(outputDir)
  start()

if __name__ == "__main__":
  main()