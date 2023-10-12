#!/usr/bin/env python
# -*- coding: utf-8 -*- #

from codecs import open
import os
import sys
import pystache
from itertools import islice
import argparse
import imp
import importlib.util
import shutil
import re
import datetime
import time
import pytz
from bs4 import BeautifulSoup
import markdown
from markdown.extensions.toc import TocExtension
#import mdx_smartypants
import pprint
import cProfile
from xml.sax.saxutils import escape

# Settings Import

parser = argparse.ArgumentParser(description='Yak Barber is a fiddly little time sink, and blog system.')
parser.add_argument('-s','--settings',nargs=1,help='Specify a settings.py file to use.')
parser.add_argument('-c','--cprofile',action='store_true', default=False,help='Run cProfile to check run time and elements.')
args = parser.parse_args()
if args.settings is not None:
  settingsPath = args.settings[0]
else:
  settingsPath = './settingstest.py'
#settings = imp.load_source('settingstest.py',settingsPath)
settings = imp.load_source('settingstest.py',settingsPath)
#spec = importlib.util.spec_from_file_location(settingsPath,'settings.py')
#settings = importlib.util.module_from_spec(spec)
#spec.loader.exec_module(settings)

# Settings Local

root = settings.root
webRoot = settings.webRoot
contentDir = settings.contentDir
templateDir = settings.templateDir
outputDir = settings.outputDir
sitename = settings.sitename
author = settings.author
ogpDefaultImage = settings.ogpDefaultImage
postsPerPage = settings.postsPerPage
typekitId = settings.typekitId

# 'meta','fenced_code','footnotes','smart_strong','smarty'

#md = markdown.Markdown(extensions=['meta','smarty','toc'])
md = markdown.Markdown(extensions=['meta','smarty', TocExtension(anchorlink=True)])


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

def decode_dict(dict):
  """Decodes all entries in a dict to UTF-8.

  Args:
    dict: A dict.

  Returns:
    A dict with all entries decoded to UTF-8.
  """

  new_dict = {}
  for key, value in dict.items():
    new_dict[key] = decode_value(value)
  return new_dict

def decode_list(list):
  """Decodes all entries in a list to UTF-8.

  Args:
    list: A list.

  Returns:
    A list with all entries decoded to UTF-8.
  """

  new_list = []
  for item in list:
    new_list.append(decode_value(item))
  return new_list

def decode_value(value):
  """Decodes a value to UTF-8.

  Args:
    value: A value to decode.

  Returns:
    A decoded value.
  """

  if isinstance(value, bytes):
    return value.decode("utf-8")
  elif isinstance(value, dict):
    return decode_dict(value)
  elif isinstance(value, list):
    return decode_list(value)
  else:
    return value
    
def named_entities(text):
	return text.encode('ascii', 'xmlcharrefreplace')
	
def convert_http_to_https(url):
  return re.sub('http://joe-steel', 'https://joe-steel', url)

def removePunctuation(text):
  text = re.sub(r'\s[^a-zA-Z0-9]\s',' ',text)
  text = re.sub(r'[^a-zA-Z0-9\s]+','',text)
  text = text.encode('ascii','xmlcharrefreplace')
  text = text.decode('utf-8')
  return text

def templateResources():
  tList = os.listdir(templateDir)
  tList = [x for x in tList if ('.html' or '.xml') not in x]
  for tr in tList:
      fullPath = os.path.join(templateDir, tr)
      if (os.path.isfile(fullPath)):
          shutil.copy(fullPath, outputDir)

def openConvert(mdfile):
  with open(mdfile, 'r', encoding='utf-8') as f:
    rawfile = f.read()
    converted = md.convert(rawfile)
    try:
      if re.match(r'[a-zA-Z0-9]+',md.Meta['title'][0]):
        converted = convert_http_to_https(converted)
        convertedMeta = [md.Meta, converted]
        return convertedMeta
      else:
        return None
    except:
      return None

def aboutPage():
  with open(contentDir + 'about.markdown', 'r', encoding='utf-8') as f:
    rawfile = f.read()
    converted = {'about': md.convert(rawfile),'sitename':sitename,'webRoot':webRoot}
  converted['typekitId'] = typekitId
  with open(templateDir + 'about.html','r', encoding='utf-8') as f:
    aboutTemplate = f.read()
  with open(outputDir + 'about.html', 'w', encoding='utf-8') as f:
    aboutResult = pystache.render(aboutTemplate,converted)
    return f.write(aboutResult)

def extractTags(html,tag):
  soup = BeautifulSoup(html, 'html.parser')
  to_extract = soup.findAll(tag)
  for item in to_extract:
    item.extract()
  return str(soup)
  
def stripTags(html):
	soup = BeautifulSoup(html, 'html.parser')
	text = soup.get_text()
	return text
	

def renderPost(post, posts):
  metadata = {}
  for k, v in post[0].items():
    metadata[k] = decode_value(v[0])
#    metadata[k] = v[0]
  metadata['content'] = post[1]
  metadata['sitename'] = sitename
  metadata['webRoot'] = webRoot
  metadata['author'] = author
  metadata['typekitId'] = typekitId
  metadata['date'] = str(metadata['date'])
  if 'image' in metadata:
    metadata['image'] = metadata['image']
  else:
    metadata['image'] = ogpDefaultImage
  postName = removePunctuation(metadata['title'])
  postName = metadata['date'].split(' ')[0] + '-' + postName.replace(' ','-').replace('‑','-')
  postName = '-'.join(postName.split('-'))
  postFileName = outputDir + postName + '.html'
  metadata['postURL'] = webRoot + postName + '.html'
#  metadata['title'] = str(mdx_smartypants.unicode_entities(metadata['title']))
  metadata['title'] = stripTags(str(markdown.markdown((metadata['title']), extensions=['smarty'])))
#  metadata['title'] = stripTags(metadata['title'])
  if 'link' in metadata:
    templateType = '/post-content-link.html'
  else:
    templateType = '/post-content.html'
  with open(templateDir + templateType,'r','utf-8') as f:
    postContentTemplate = f.read()
    postContent = pystache.render(postContentTemplate,metadata,decode_errors='ignore')
    metadata['post-content'] = postContent
  with open(templateDir + '/post-page.html','r','utf-8') as f:
    postPageTemplate = f.read()
    postPageResult = pystache.render(postPageTemplate,metadata,decode_errors='ignore')
  with open(postFileName,'w','utf-8') as f:
    f.write(postPageResult)
  return posts.append(metadata)


def RFC3339Convert(timeString):
  timeString = decode_value(timeString)
  strip = time.strptime(timeString, '%Y-%m-%d %H:%M:%S')
  dt = datetime.datetime.fromtimestamp(time.mktime(strip))
  pacific = pytz.timezone('US/Pacific')
  ndt = dt.replace(tzinfo=pacific)
  utc = pytz.utc
  return ndt.astimezone(utc).isoformat().split('+')[0] + 'Z'


def feed(posts):
  posts = decode_value(posts)
  feedDict = posts[0]
  entryList = str()
  feedDict['gen-time'] = datetime.datetime.utcnow().isoformat('T') + 'Z'
  with open(templateDir + '/atom.xml','r','utf-8') as f:
    atomTemplate = f.read()
  with open(templateDir + '/atom-entry.xml','r','utf-8') as f:
    atomEntryTemplate = f.read()
  for e,p in enumerate(posts):
    p['date'] = RFC3339Convert(p['date'])
    p['content'] = extractTags(p['content'],'script')
    p['content'] = extractTags(p['content'],'object')
    p['content'] = extractTags(p['content'],'iframe')
    p['title'] = stripTags(p['title'])
    if e < 100:
      atomEntryResult = pystache.render(atomEntryTemplate,p)
      entryList += atomEntryResult
  feedDict['atom-entry'] = entryList
  feedResult = pystache.render(atomTemplate,feedDict,string_encode='utf-8')
  with open(outputDir + 'feed.xml','w','utf-8') as f:
    f.write(feedResult)

def paginatedIndex(posts):
  posts = decode_value(posts)
  indexList = sorted(posts,key=lambda k: k['date'])[::-1]
  feed(indexList)
  postList = []
  for i in indexList:
    postList.append(i['post-content'])
  indexOfPosts = splitEvery(postsPerPage,indexList)
  with open(templateDir + '/index.html','r','utf-8') as f:
    indexTemplate = f.read()
  indexDict = {}
  indexDict['sitename'] = sitename
  indexDict['typekitId'] = typekitId
  for e,p in enumerate(indexOfPosts):
    indexDict['post-content'] = p
#    print(e)
#    for x in p:
#      print(x['date'])
    if e == 0:
      fileName = 'index.html'
      if len(indexList) > postsPerPage:
        indexDict['previous'] = webRoot + 'index2.html'
    else:
      fileName = 'index' + str(e+1) + '.html'
      if e == 1:
        indexDict['next'] = webRoot + 'index.html'
        indexDict['previous']  = webRoot + 'index' + str(e+2) + '.html'
      else:
        indexDict['previous'] = webRoot + 'index' + str(e+2) + '.html'
        if e < len(indexList):
          indexDict['next'] = webRoot + 'index' + str(e-1) + '.html'
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
#  print(convertedList[1])
  sortedList = sorted(convertedList, key=lambda x: x[1], reverse=True)
#  pprint.pprint(convertedList, indent=1, depth=4)
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
