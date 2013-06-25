#!/usr/bin/env python
#

import sys
import urllib
from httplib import *
import time
import datetime

#PARAMS
nsyms_per_query = 100
query_delay = 2
yahoo_cols_txt = "symbol, last_trade, open, high, low, close, volume, avg_daily_volume, ebitda"
yahoo_cols = "slohgpva2j4"


#CONSOLE UI
print("Yahoo! Finance scraper")
print("Usage: ./yahoo.py [filename w/ ticker symbols, 1 per line, not urlencoded]")
assert len(sys.argv) == 2

fname = sys.argv[1]
syms = []
with open(fname, "r") as f:
    for line in f:
        syms.append(line.strip().upper())


#http://ichart.finance.yahoo.com/table.csv?s=MSFT&a=02&b=13&c=1986&d=07&e=9&f=2011&g=d&ignore=.csv
#SCRAPE YAHOO
sys.stderr.write("scraping yahoo\n")
print("%s\n"%yahoo_cols_txt)
maxd = datetime.date.today()
for sym in syms:

    # READ ALL HISTORICAL DATA FROM YAHOO
    print ""
    print "FETCHING DATA FOR "+sym
    yahoo_host = "ichart.finance.yahoo.com"
    yahoo_url = "/table.csv?s=%s&a=01&b=1&c=1940&d=%02d&e=%d&f=%d&g=d&ignore=.csv"%(sym,maxd.day,maxd.month,maxd.year)
    sys.stderr.write("getting %s\n"%yahoo_url)

    conn = HTTPConnection(yahoo_host)
    conn.request("GET", yahoo_url)

    # HANDLE FAILS
    resp = conn.getresponse()
    csv = ""
    if resp.status != 200:
        csv = "ERROR: fetched http://%s%s, got %s\n"%(yahoo_host, yahoo_url, resp.status)
    else:
        csv = resp.read()

    # WRITE TO FILE
    csv_fname = "prices/%s.csv"%sym
    with open(csv_fname, "w") as f:
        f.write(csv)

    # BE NICE
    time.sleep(query_delay)

sys.stderr.write("done!\n")

