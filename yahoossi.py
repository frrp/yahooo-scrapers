#!/usr/bin/env python

#Gets sector / subsector / industry / company. Writes ticker symbols to tickers.txt
import httplib
import re
import time

fname = "tickers.txt"
f = open(fname, "w")

nmisses = 0
nmaxmisses = 120
delay = 1.2
i = 0
while True:

    # DON'T DDOS YAHOO
    time.sleep(delay)

    # TRY TO GET LIST OF PUBLIC COMPANIES
    i += 1
    url = "/ic/%s_cl_pub.html"%i
    print ""
    print "GETTING %s"%url
    conn = httplib.HTTPConnection("biz.yahoo.com")
    conn.request("GET", url)
    resp = conn.getresponse()

    # HANDLE FAIL
    if resp.status != 200:
        print "HTTP returned ERROR %s"%resp.status
        nmisses += 1
        if nmisses > nmaxmisses:
            print "MAX ERRORS EXCEEDED, EXITING"
            break
        continue

    # ON SUCCESS, PARSE OUT TICKER SYMS
    nmisses = 0
    html = resp.read()
    print html
    for match in re.finditer("finance.yahoo.com/q\\?s=([^\"]+)", html):
        sym = match.group(1)
        f.write("%s\n"%sym)

print "done!"
f.close()
