#!/usr/bin/python

# Crawls to get all the symbols in Yahoo's DB.

import sys
import httplib
import time
import re

#PARAMS
delay = 2 #secs between reqs


#RECURSIVE CRAWLER
urls_visited = set()
symbols = []
def crawl(url):
    # skip stuff we've visited
    if url in urls_visited:
        print>>sys.stderr, "been here before, skipping: %s"%url
        return
    urls_visited.add(url)

    # be nice
    time.sleep(delay) 

    # fetch the site
    print>>sys.stderr, "crawling %s..."%url
    conn = httplib.HTTPConnection("biz.yahoo.com")
    conn.request("GET", url)
    resp = conn.getresponse()
    if resp.status != 200:
        print >> sys.stderr, "skipping, http error %s"%resp.status
    html = resp.read()

    # parse out links
    links = []
    for match in re.finditer('href="?(?P<url>/i/.*?\\.html)"?', html):
        links.append(match.group('url'))

    # parse out symbols
    for match in re.finditer('<tt>(?P<sym>[^ <]+)</tt>', html):
        sym = match.group('sym')
        symbols.append(match.group('sym'))
        print sym
        sys.stdout.flush()

    # recursively crawl links
    for link in links:
        crawl(link)

#MAIN
def main():
    #crawl("http://biz.yahoo.com/i/")
    crawl("/i/")
    #for symbol in symbols:
    #    print symbol

#do it.
main()
