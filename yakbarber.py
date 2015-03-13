#!/usr/bin/env python
# -*- coding: utf-8 -*- #

from codecs import open
import os
import sys
import pystache
from itertools import islice
import argparse
import imp
import shutil
import re
import datetime
import time
import pytz
import BeautifulSoup
import markdown
import mdx_smartypants
import cProfile

# Settings Import

parser = argparse.ArgumentParser(description='Yak Barber is a fiddly little time sink, and blog system.')
parser.add_argument('-s','--settings',nargs=1,help='Specify a settings.py file to use.')
parser.add_argument('-c','--cprofile',action='store_true', default=False,help='Run cProfile to check run time and elements.')
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
postsPerPage = settings.postsPerPage
typekitId = settings.typekitId

# 'meta','fenced_code','footnotes','smart_strong','smarty'

md = markdown.Markdown(extensions=['meta','smartypants','toc(anchorlink=True)'])

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
    try:
      if re.match(r'[a-zA-Z0-9]+',md.Meta[u'title'][0]):
        converted = converted
        convertedMeta = [md.Meta, converted]
        return convertedMeta
      else:
        return None
    except:
      return None

def aboutPage():
  with open(contentDir + u'about.markdown', 'r', 'utf-8') as f:
    rawfile = f.read()
    converted = {'about': md.convert(rawfile),'sitename':sitename,'webRoot':webRoot}
  converted[u'typekitId'] = typekitId
  with open(templateDir + u'about.html','r','utf-8') as f:
    aboutTemplate = f.read()
  with open(outputDir + u'about.html', 'w', 'utf-8') as f:
    aboutResult = pystache.render(aboutTemplate,converted)
    return f.write(aboutResult)

def renderPost(post, posts):
  metadata = {}
  for k, v in post[0].iteritems():
    metadata[k] = v[0]
  metadata[u'content'] = post[1]
  metadata[u'sitename'] = sitename
  metadata[u'webRoot'] = webRoot
  metadata[u'author'] = author
  metadata[u'typekitId'] = typekitId
  postName = removePunctuation(metadata[u'title'])
  postName = metadata[u'date'].split(' ')[0] + '-' + postName.replace(u' ',u'-').replace(u'‑',u'-')
  postName = u'-'.join(postName.split('-'))
  postFileName = outputDir + postName + '.html'
  metadata[u'postURL'] = webRoot + postName + '.html'
  metadata[u'title'] = unicode(mdx_smartypants.unicode_entities(metadata[u'title']))
  if u'link' in metadata:
    templateType = u'/post-content-link.html'
  else:
    templateType = u'/post-content.html'
  with open(templateDir + templateType,'r','utf-8') as f:
    postContentTemplate = f.read()
    postContent = pystache.render(postContentTemplate,metadata,decode_errors='ignore')
    metadata['post-content'] = postContent
  with open(templateDir + u'/post-page.html','r','utf-8') as f:
    postPageTemplate = f.read()
    postPageResult = pystache.render(postPageTemplate,metadata,decode_errors='ignore')
  with open(postFileName,'w','utf-8') as f:
    f.write(postPageResult)
  return posts.append(metadata)

def extractTags(html,tag):
  soup = BeautifulSoup.BeautifulSoup(html)
  to_extract = soup.findAll(tag)
  for item in to_extract:
    item.extract()
  return unicode(soup)

def RFC3339Convert(timeString):
  strip = time.strptime(timeString, '%Y-%m-%d %H:%M:%S')
  dt = datetime.datetime.fromtimestamp(time.mktime(strip))
  pacific = pytz.timezone('US/Pacific')
  ndt = dt.replace(tzinfo=pacific)
  utc = pytz.utc
  return ndt.astimezone(utc).isoformat().split('+')[0] + 'Z'


def feed(posts):
  feedDict = posts[0]
  entryList = str()
  feedDict['gen-time'] = datetime.datetime.utcnow().isoformat('T') + 'Z'
  with open(templateDir + u'/atom.xml','r','utf-8') as f:
    atomTemplate = f.read()
  with open(templateDir + u'/atom-entry.xml','r','utf-8') as f:
    atomEntryTemplate = f.read()
  for e,p in enumerate(posts):
    p[u'date'] = RFC3339Convert(p[u'date'])
    p[u'content'] = extractTags(p[u'content'],'script')
    p[u'content'] = extractTags(p[u'content'],'object')
    p[u'content'] = extractTags(p[u'content'],'iframe')
    if e < 100:
      atomEntryResult = pystache.render(atomEntryTemplate,p)
      entryList += atomEntryResult
  feedDict['atom-entry'] = entryList
  feedResult = pystache.render(atomTemplate,feedDict,string_encode='utf-8')
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
  indexDict[u'typekitId'] = typekitId
  for e,p in enumerate(indexOfPosts):
    indexDict['post-content'] = p
    print e
    #for x in p:
      #print x['title']
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
  aboutPage()
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
  if args.cprofile:
    cProfile.run('main()')
  else:
    main()
